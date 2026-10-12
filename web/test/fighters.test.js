import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { skirmish, CLASSIC, BUILDINGS } from "../src/content.js";
import { fighterStats, damageFighter } from "../src/fighters.js";
import { freshProgress } from "../src/storage.js";
import { buyTowerSkill } from "../src/experience.js";
import { researchView } from "../src/research-view.js";
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-6, `${a} != ${b}`);
const tick = (s, n) => {
  for (let i = 0; i < n * 40; i++) s.update(0.025);
};
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
  const store = s.addBuilding("battery", 0, 0, true);
  store.level = 4;
  store.energy = 1000;
  const hangar = s.addBuilding("hangar", 60, 0, true);
  s.networkDirty = true;
  s.rebuildNetwork();
  s.diff = { ...s.diff, damage: 0 };
  const enemy = s.spawnEnemy("fighter", 0);
  enemy.x = 300;
  enemy.y = 0;
  enemy.hp = enemy.maxHp = 1e5;
  return { s, store, hangar, enemy };
}
test("hangar launches paid craft within range, respects berth/cadence and charges carried energy", () => {
  const { s, hangar } = lab();
  const energy = s.buildings.reduce((n, b) => n + b.energy, 0),
    minerals = s.minerals;
  tick(s, 0.025);
  assert.equal(s.fighters.length, 1);
  near(minerals - s.minerals, 20);
  near(energy - s.buildings.reduce((n, b) => n + b.energy, 0), 24);
  near(s.fighters[0].energy, 24);
  near(s.fighters[0].fuel, 20 - 0.025);
  tick(s, 1);
  assert.equal(s.fighters.length, 1);
  tick(s, 5);
  assert.equal(s.fighters.length, stats(hangar).fighterSlots);
  assert.ok(s.fighters.some((f) => f.x > hangar.x + 20));
  assert.ok(s.xpEarned > 0);
  assert.ok(s.enemies[0].hp < 1e5);
});
test("disconnected, unbuilt and unaffordable hangars cannot manufacture fighters", () => {
  for (const mode of ["disconnected", "unbuilt", "poor", "distant"]) {
    const { s, store, hangar, enemy } = lab();
    if (mode === "disconnected") {
      store.energy = 0;
      hangar.energy = 0;
    }
    if (mode === "unbuilt") {
      hangar.construction = 0;
      hangar.constructionUnits = 0;
    }
    if (mode === "poor") s.minerals = 19;
    if (mode === "distant") enemy.x = 900;
    tick(s, 0.025);
    assert.equal(s.fighters.length, 0, mode);
  }
});
test("survivors return and dock; repairs, rearming, fuel and shields consume real power", () => {
  const { s } = lab({ fighter_craft: { shields: 5 } });
  tick(s, 0.025);
  const f = s.fighters[0];
  s.enemies = [];
  f.x = 130;
  f.y = 0;
  f.angle = Math.PI;
  tick(s, 1);
  assert.equal(f.mode, "docked");
  damageFighter(f, f.shieldCharge + 10);
  f.energy -= 5;
  f.fuel -= 5;
  const before = s.buildings.reduce((n, b) => n + b.energy, 0),
    hp = f.hp,
    energy = f.energy,
    fuel = f.fuel,
    shield = f.shieldCharge;
  tick(s, 0.5);
  const paid = s.buildings.reduce((n, b) => n + b.energy, 0);
  const restoration =
    f.hp -
    hp +
    (f.energy - energy) +
    0.2 * (f.fuel - fuel) +
    0.2 * (f.shieldCharge - shield);
  near(before - paid, restoration);
  assert.ok(f.hp > hp);
  assert.ok(f.shieldCharge > shield);
  assert.ok(s.xpEarned > 0);
  assert.ok(s.masteryEarned > 0);
});
test("enemy fighter attacks can damage aircraft; finite fuel and lost hangars remove craft", () => {
  const { s, enemy } = lab();
  tick(s, 0.025);
  const f = s.fighters[0];
  f.x = 280;
  f.y = 0;
  enemy.x = 281;
  enemy.y = 0;
  s.diff = { ...s.diff, damage: 1 };
  const hp = f.hp;
  tick(s, 0.025);
  assert.ok(f.hp < hp);
  f.fuel = 0.001;
  tick(s, 0.025);
  assert.equal(s.fighters.length, 0);
  const other = lab();
  tick(other.s, 0.025);
  other.s.recycle(other.hangar.id);
  tick(other.s, 0.025);
  assert.equal(other.s.fighters.length, 0);
});
test("hangar tiers and independent craft mastery stack without retroactively healing existing aircraft", () => {
  assert.deepEqual(
    BUILDINGS.hangar.stats.map((s) => s.fighterSlots),
    [2, 3, 4, 6],
  );
  const { s, hangar } = lab({
    hangar: { slots: 3, launch: 10, service: 10 },
    fighter_craft: { damage: 10, fuel: 10, hull: 10, shields: 10, armor: 10 },
  });
  near(stats(hangar).fighterSlots, 5);
  near(stats(hangar).launchInterval, 5 / 1.3);
  const config = fighterStats(s.rules);
  near(config.hp, 120);
  near(config.damage, 30);
  near(config.fuel, 30);
  near(config.shield, 24);
  tick(s, 0.025);
  const f = s.fighters[0],
    original = { ...f.config };
  s.setResearchLoadout([], {}, { fighter_craft: { hull: 50, fuel: 50 } });
  assert.deepEqual(f.config, original);
  const p = freshProgress();
  p.experience.masteryXp = 100;
  assert.equal(buyTowerSkill(p, "fighter_craft", "damage").ok, true);
  assert.equal(buyTowerSkill(p, "hangar", "slots").ok, false);
  assert.match(
    researchView(p, "solar_cells", () => "", {
      page: "towers",
      tower: "fighter_craft",
    }),
    /Fighter craft/,
  );
});
test("aircraft and hangar servicing resume deterministically; Classic has no hangar access", () => {
  const { s } = lab();
  tick(s, 2);
  const copy = new Simulation(s.mission, "normal", s.snapshot());
  copy.diff = { ...copy.diff, damage: 0 };
  tick(s, 2);
  tick(copy, 2);
  assert.deepEqual(copy.fighters, s.fighters);
  assert.deepEqual(copy.enemies, s.enemies);
  const classic = new Simulation(CLASSIC[0]);
  assert.equal(classic.mission.unlocked.includes("hangar"), false);
  assert.equal(classic.build("hangar", 0, 0).ok, false);
});
