import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { skirmish, CLASSIC } from "../src/content.js";
import {
  missilePayloadStats,
  interceptMissile,
} from "../src/missile-flight.js";
import { freshProgress, saveProgress, loadProgress } from "../src/storage.js";
import { buyTowerSkill } from "../src/experience.js";
import { researchView } from "../src/research-view.js";
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-7, `${a} != ${b}`);
function lab(towers = {}) {
  const s = new Simulation(
    { ...skirmish(42, "sandbox"), waves: 0 },
    "normal",
    null,
    [],
    {},
    towers,
  );
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  const battery = s.addBuilding("battery", 0, 0, true);
  battery.energy = 100;
  const launcher = s.addBuilding("missile", 60, 0, true);
  s.networkDirty = true;
  s.rebuildNetwork();
  return { s, battery, launcher };
}
test("ordnance mastery stacks payload damage/range with launcher skills and configures fifty-rank limits", () => {
  const baseline = stats(lab().launcher);
  const { launcher } = lab({
    missile: { damage: 10, range: 10 },
    missile_round: {
      damage: 10,
      range: 10,
      splash: 10,
      fuel: 10,
      hull: 10,
      shields: 10,
    },
  });
  const configured = stats(launcher);
  near(configured.damage, baseline.damage * 1.5 * 1.5);
  near(configured.range, baseline.range * 1.3 * 1.3);
  near(configured.splash, baseline.splash * 1.4);
  near(configured.missileFuel, 12);
  near(configured.missileHull, 30);
  near(configured.missileShield, 6);
  near(configured.launchEnergy, 2.2);
  const maximum = missilePayloadStats({
    towers: { missile_round: { fuel: 50, hull: 50, shields: 50 } },
  });
  near(maximum.fuel, 28);
  near(maximum.hull, 70);
  near(maximum.shield, 70);
});
test("launch pays ammunition and shield charge once; upgrades do not refill in-flight hull, shield or fuel", () => {
  const { s, launcher } = lab({
    missile_round: { fuel: 10, hull: 10, shields: 10 },
  });
  const enemy = s.spawnEnemy("fighter", 0);
  enemy.x = 220;
  enemy.y = 0;
  const energy = s.buildings.reduce((n, b) => n + b.energy, 0),
    minerals = s.minerals;
  s.update(0.025);
  assert.equal(s.projectiles.length, 1);
  const p = s.projectiles[0];
  near(p.maxHp, 30);
  near(p.shieldCapacity, 6);
  near(p.fuelCapacity, 12);
  near(s.minerals, minerals - 5);
  near(energy - s.buildings.reduce((n, b) => n + b.energy, 0), 2.2);
  interceptMissile(p, 8);
  const before = { hp: p.hp, shield: p.shieldCharge, life: p.life };
  s.setResearchLoadout(
    [],
    {},
    { missile_round: { fuel: 50, hull: 50, shields: 50 } },
  );
  assert.deepEqual({ hp: p.hp, shield: p.shieldCharge, life: p.life }, before);
  near(stats(launcher).missileFuel, 28);
  const restored = new Simulation(s.mission, "normal", s.snapshot());
  assert.deepEqual(restored.projectiles, s.projectiles);
});
test("projectile shields absorb interception first, remain finite and do not recharge", () => {
  const p = { hp: 30, shieldCharge: 6, life: 12 };
  assert.equal(interceptMissile(p, 10), false);
  near(p.shieldCharge, 0);
  near(p.hp, 26);
  assert.equal(interceptMissile(p, 10), false);
  near(p.hp, 16);
  assert.equal(interceptMissile(p, 20), true);
  near(p.life, 0);
});
test("blast-radius mastery damages an enemy outside the original explosion radius", () => {
  const run = (splash) => {
    const { s, launcher } = lab({ missile_round: { splash } });
    s.minerals = 0;
    const configured = stats(launcher),
      baseline = stats(lab().launcher);
    const primary = s.spawnEnemy("fighter", 0);
    primary.x = 200;
    primary.y = 200;
    primary.hp = primary.maxHp = 10000;
    const nearby = s.spawnEnemy("fighter", 0);
    nearby.x = 200 + baseline.splash * 1.2;
    nearby.y = 200;
    nearby.hp = nearby.maxHp = 10000;
    s.projectiles.push({
      id: 900,
      x: 199,
      y: 200,
      targetId: primary.id,
      damage: configured.damage,
      splash: configured.splash,
      speed: 160,
      life: 8,
      hp: 20,
      friendly: true,
      angle: 0,
    });
    s.update(0.025);
    return nearby.hp;
  };
  near(run(0), 10000);
  assert.ok(run(25) < 10000);
});
test("ordnance purchases use existing mastery budget, persist, and Classic excludes the modifiers", () => {
  const p = freshProgress();
  p.experience.masteryXp = 100;
  assert.equal(buyTowerSkill(p, "missile_round", "fuel").ok, true);
  assert.equal(buyTowerSkill(p, "missile_round", "hull").ok, false);
  let value;
  const storage = {
    getItem: () => value,
    setItem: (_, v) => {
      value = v;
    },
  };
  saveProgress(p, storage);
  assert.equal(loadProgress(storage).experience.towers.missile_round.fuel, 1);
  const html = researchView(p, "solar_cells", () => "", {
    page: "towers",
    tower: "missile_round",
  });
  for (const name of [
    "Warhead damage",
    "Engagement range",
    "Blast radius",
    "Fuel reserves",
    "Missile hull",
    "Missile shields",
  ])
    assert.ok(html.includes(name));
  assert.match(html, /NEW LAUNCHES/);
  const classic = new Simulation(
    CLASSIC[0],
    "normal",
    null,
    [],
    {},
    {
      missile_round: {
        fuel: 50,
        damage: 50,
        hull: 50,
        shields: 50,
        splash: 50,
      },
    },
  );
  const launcher = classic.addBuilding("missile", 0, 0, true);
  near(stats(launcher).missileFuel, 8);
  near(stats(launcher).missileHull, 20);
  near(stats(launcher).missileShield, 0);
});
