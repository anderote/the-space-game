import test from "node:test";
import assert from "node:assert/strict";
import { Simulation } from "../src/engine.js";
import { skirmish, CLASSIC } from "../src/content.js";
import {
  shieldCapacity,
  enemyDamageMultiplier,
} from "../src/shield-modules.js";
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-6, `${a} != ${b}`);
const tick = (s, n) => {
  for (let i = 0; i < n * 40; i++) s.update(0.025);
};
function lab(ids = ["capacitive_armor"]) {
  const s = new Simulation({ ...skirmish(42, "sandbox"), waves: 0 });
  s.setResearchLoadout(ids);
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.networkDirty = true;
  return s;
}
test("shield modules require research, minerals, completed construction and stop at three tiers", () => {
  const s = lab([]),
    b = s.addBuilding("solar", 0, 0, true);
  assert.equal(s.upgradeShield(b.id).ok, false);
  s.setResearchLoadout(["capacitive_armor"]);
  s.minerals = 99;
  assert.equal(s.upgradeShield(b.id).ok, false);
  s.minerals = 1e4;
  for (let level = 1; level <= 3; level++) {
    const before = s.minerals,
      cost = s.shieldModuleCost(b),
      charge = b.shieldCharge || 0;
    assert.equal(s.upgradeShield(b.id).ok, true);
    assert.equal(s.minerals, before - cost);
    assert.equal(s.upgradeShield(b.id).ok, false);
    assert.equal(b.shieldCharge, charge);
    tick(s, 5);
    assert.equal(b.shieldLevel, level);
    assert.equal(b.construction, 1);
  }
  assert.equal(s.upgradeShield(b.id).ok, false);
  assert.equal(
    s.upgradeShield(s.addBuilding("station", 80, 0, true).id).ok,
    false,
  );
});
test("rechargeable shields absorb full hits then spill to hull; no repair XP for shield loss", () => {
  const s = lab([]),
    b = s.addBuilding("laser", 0, 0, true);
  s.rules.shieldModules = true;
  b.shieldLevel = 1;
  b.shieldCharge = shieldCapacity(b);
  const hp = b.hp;
  s.damageBuilding(b, 30);
  near(b.hp, hp);
  near(b.shieldCharge, 10);
  near(b.repairXpDebt || 0, 0);
  s.damageBuilding(b, 25);
  near(b.hp, hp - 15);
  near(b.shieldCharge, 0);
  near(b.repairXpDebt, 15);
});
test("recharge waits after hits and consumes exact energy, including solar own reserve", () => {
  const s = lab(),
    b = s.addBuilding("solar", 0, 0, true);
  b.shieldLevel = 1;
  b.shieldCharge = 0;
  b.lastDamaged = 0;
  s.rebuildNetwork();
  tick(s, 4.9);
  near(b.shieldCharge, 0);
  let consumed = 0;
  for (let i = 0; i < 100; i++) {
    s.update(0.025);
    consumed += s.drawnThisTick;
  }
  assert.ok(b.shieldCharge > 0);
  near(consumed, b.shieldCharge * 0.2);
  const charge = b.shieldCharge;
  s.damageBuilding(b, 1);
  const after = b.shieldCharge;
  tick(s, 4);
  near(b.shieldCharge, after);
  assert.ok(charge > after);
});
test("disconnected powerless shields cannot recharge; stored charge still protects", () => {
  const s = lab(),
    b = s.addBuilding("laser", 0, 0, true);
  b.energy = 0;
  b.shieldLevel = 1;
  b.shieldCharge = 0;
  s.rebuildNetwork();
  tick(s, 10);
  near(b.shieldCharge, 0);
  b.shieldCharge = 20;
  const hp = b.hp;
  s.damageBuilding(b, 15);
  near(b.hp, hp);
  near(b.shieldCharge, 5);
});
test("module charge and paid spending survive snapshot; live research cannot refill shields", () => {
  const s = lab(),
    b = s.addBuilding("battery", 0, 0, true);
  s.rebuildNetwork();
  s.minerals = 1e4;
  assert.equal(s.upgradeShield(b.id).ok, true);
  tick(s, 10);
  b.shieldCharge = 17;
  const saved = new Simulation(s.mission, "normal", s.snapshot()),
    copy = saved.buildings.find((x) => x.id === b.id);
  near(copy.shieldCharge, 17);
  assert.equal(copy.shieldLevel, 1);
  assert.equal(copy.upgradeSpent, 100);
  s.setResearchLoadout(["capacitive_armor", "hull_weave"]);
  near(b.shieldCharge, 17);
  s.setResearchLoadout([]);
  near(b.shieldCharge, 0);
  s.setResearchLoadout(["capacitive_armor"]);
  near(b.shieldCharge, 0);
});
test("all player classes receive capacity; Classic keeps original damage and disables modules", () => {
  const s = lab();
  for (const type of [
    "relay",
    "miner",
    "solar",
    "battery",
    "repair",
    "laser",
    "thel",
    "missile",
  ]) {
    const b = s.addBuilding(type, 0, 0, true);
    b.shieldLevel = 3;
    near(shieldCapacity(b), b.maxHp * 0.5);
  }
  const classic = new Simulation(CLASSIC[0], "normal", null, [
    "capacitive_armor",
  ]);
  const b = classic.buildings[0];
  b.shieldLevel = 3;
  near(shieldCapacity(b), 0);
  assert.equal(classic.upgradeShield(b.id).ok, false);
  near(enemyDamageMultiplier(CLASSIC[0]), 1);
  near(enemyDamageMultiplier(skirmish(1)), 0.9);
});
test("modern direct attacks and bomber impacts deal ten percent less actual damage", () => {
  const s = lab([]),
    b = s.addBuilding("solar", 0, 0, true);
  const e = s.spawnEnemy("fighter", 0);
  e.x = 10;
  e.y = 0;
  s.rebuildNetwork();
  const hp = b.hp;
  tick(s, 1);
  near(hp - b.hp, 45);
  s.enemies = [];
  const before = b.hp;
  s.projectiles = [
    {
      id: 999,
      targetId: b.id,
      enemy: true,
      x: b.x,
      y: b.y,
      speed: 100,
      damage: 40,
      life: 2,
      hp: 20,
    },
  ];
  s.update(0.025);
  near(before - b.hp, 36);
});

test("connected shield charging consumes supplier energy and produces normal network flows", () => {
  const s = lab(),
    store = s.addBuilding("battery", 0, 0, true),
    b = s.addBuilding("laser", 60, 0, true);
  store.energy = 100;
  b.energy = 0;
  b.shieldLevel = 1;
  b.shieldCharge = 0;
  s.rebuildNetwork();
  tick(s, 1);
  assert.ok(b.shieldCharge > 0);
  near(100 - store.energy, b.shieldCharge * 0.2);
  assert.ok(s.flows.some((f) => f.consumer === b.id));
});
test("shield module costs honor fabrication discounts and retain paid refund amounts", () => {
  const s = lab(),
    b = s.addBuilding("solar", 0, 0, true);
  s.setResearchLoadout(["capacitive_armor"], { economy: 20 });
  s.minerals = 1000;
  near(s.shieldModuleCost(b), 80);
  assert.equal(s.upgradeShield(b.id).ok, true);
  near(s.minerals, 920);
  near(b.upgradeSpent, 80);
  const before = s.minerals;
  assert.equal(s.recycle(b.id).ok, true);
  near(s.minerals - before, 240);
});
