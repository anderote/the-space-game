import test from "node:test";
import assert from "node:assert/strict";
import { Simulation } from "../src/engine.js";
import { CAMPAIGN, CLASSIC, skirmish } from "../src/content.js";
import {
  normalizeExperience,
  masteryBudget,
  experienceBudget,
  buyTowerSkill,
  buyBaseStat,
} from "../src/experience.js";
import {
  freshProgress,
  bankExperience,
  saveProgress,
  loadProgress,
} from "../src/storage.js";
const run = () => new Simulation({ ...CAMPAIGN[1], goal: 1e9, firstWave: 1e9 });
const tick = (s, n) => {
  for (let i = 0; i < n * 40; i++) s.update(0.025);
};
test("mastery rewards kills once, excludes interception and self-destruction", () => {
  const s = run(),
    e = s.spawnEnemy("fighter", 0);
  s.damageEnemy(e, 1);
  assert.equal(s.masteryEarned, 0);
  s.damageEnemy(e, 1e9);
  s.damageEnemy(e, 1e9);
  assert.equal(s.masteryEarned, 10);
  s.damageEnemy({ hp: 10, interceptable: true }, 100);
  assert.equal(s.masteryEarned, 10);
});
test("completed construction and upgrades earn paid-cost mastery; free and canceled builds do not", () => {
  const s = run();
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.networkDirty = true;
  s.minerals = 1e5;
  const sun = s.addBuilding("solar", 0, 0, true);
  sun.level = 5;
  s.addBuilding("battery", 0, 60, true).energy = 1000;
  s.rebuildNetwork();
  const b = s.build("laser", 60, 0).building;
  assert.equal(s.masteryEarned, 0);
  tick(s, 8);
  assert.equal(b.construction, 1);
  assert.equal(s.masteryEarned, b.baseCost * 0.1);
  const before = s.masteryEarned,
    cost = s.upgradeCost(b);
  s.upgrade(b.id);
  assert.equal(s.masteryEarned, before);
  tick(s, 8);
  assert.equal(b.construction, 1);
  assert.equal(s.masteryEarned, before + cost * 0.1);
  tick(s, 8);
  assert.equal(s.masteryEarned, before + cost * 0.1);
  const canceled = s.build("relay", -60, 0).building;
  s.recycle(canceled.id);
  tick(s, 2);
  assert.equal(s.masteryEarned, before + cost * 0.1);
});
test("mastery repair credit consumes real damage debt exactly once", () => {
  const s = run(),
    b = s.buildings[0];
  s.damageBuilding(b, 20);
  s.creditRepair(b, 15);
  s.creditRepair(b, 20);
  s.creditRepair(b, 20);
  assert.equal(s.masteryEarned, 2);
  assert.equal(s.xpEarned, 2);
});
test("both pools bank independently, persist, and do not duplicate on resume", () => {
  const p = freshProgress(),
    s = run();
  s.xpEarned = 250;
  s.masteryEarned = 100;
  assert.deepEqual(bankExperience(p, s), {
    xp: 250,
    levels: 2,
    mastery: 100,
    masteryLevels: 1,
  });
  assert.equal(buyTowerSkill(p, "laser", "damage").ok, true);
  assert.equal(experienceBudget(p).available, 2);
  assert.equal(buyBaseStat(p, "armor").ok, true);
  assert.equal(masteryBudget(p).available, 0);
  const restored = new Simulation(s.mission, "normal", s.snapshot());
  assert.equal(bankExperience(p, restored).mastery, 0);
  let saved;
  const store = { getItem: () => saved, setItem: (_, v) => (saved = v) };
  saveProgress(p, store);
  assert.deepEqual(loadProgress(store).experience, p.experience);
  restored.masteryEarned += 150;
  assert.equal(bankExperience(p, restored).masteryLevels, 1);
});
test("legacy mastery migration retains ranks and releases command points once", () => {
  const old = {
      xp: 450,
      ranks: { armor: 1 },
      towers: { laser: { damage: 2 } },
    },
    e = normalizeExperience(old);
  assert.equal(e.masteryXp, 250);
  assert.equal(masteryBudget({ experience: e }).available, 0);
  assert.equal(experienceBudget({ experience: e }).available, 2);
  assert.deepEqual(normalizeExperience(e), e);
  assert.deepEqual(normalizeExperience({ ...e, masteryXp: 0 }).towers, {});
});
test("Classic cannot bank mastery and old snapshots start fresh", () => {
  const p = freshProgress();
  for (const mission of [CLASSIC[0]]) {
    const s = new Simulation(mission);
    s.masteryEarned = 100;
    assert.equal(bankExperience(p, s).mastery, 0);
  }
  const s = run(),
    snap = s.snapshot();
  delete snap.masteryEarned;
  delete snap.masteryCredit;
  const restored = new Simulation(s.mission, "normal", snap);
  assert.equal(bankExperience(p, restored).mastery, 0);
});
