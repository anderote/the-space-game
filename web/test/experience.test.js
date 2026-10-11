import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { CAMPAIGN, CLASSIC, skirmish, BUILDINGS } from "../src/content.js";
import {
  BASE_STATS,
  experienceBudget,
  buyBaseStat,
  normalizeExperience,
} from "../src/experience.js";
import {
  freshProgress,
  bankExperience,
  loadProgress,
  saveProgress,
  resetProgress,
} from "../src/storage.js";
import { researchBudget, researchLoadout } from "../src/research.js";
import { researchView } from "../src/research-view.js";
const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
function lab(ids = [], ranks = {}) {
  const s = new Simulation(
    { ...CAMPAIGN[1], firstWave: 10000, goal: 100000 },
    "normal",
    null,
    ids,
    ranks,
  );
  s.buildings = [];
  s.links = [];
  s.asteroids = [];
  s.networkDirty = true;
  return s;
}

test("XP crosses exact increasing level thresholds and points cannot be overspent", () => {
  const p = freshProgress();
  for (const [xp, level, available] of [
    [99.9, 1, 0],
    [100, 2, 1],
    [249.9, 2, 1],
    [250, 3, 2],
    [450, 4, 3],
  ]) {
    p.experience.xp = xp;
    assert.equal(experienceBudget(p).level, level);
    assert.equal(experienceBudget(p).available, available);
  }
  for (let i = 0; i < 3; i++) assert.equal(buyBaseStat(p, "armor").ok, true);
  assert.equal(buyBaseStat(p, "harvest").ok, false);
  assert.equal(buyBaseStat(p, "unknown").ok, false);
  assert.equal(experienceBudget(p).available, 0);
  assert.deepEqual(
    normalizeExperience({ xp: Infinity, ranks: { armor: 50 } }),
    { xp: 0, ranks: {} },
  );
  assert.deepEqual(
    normalizeExperience({ xp: 100, ranks: { armor: 999, harvest: 999 } }).ranks,
    { armor: 1 },
  );
});

test("XP stats affect real defenses, building, harvesting, weapons, repairs and generation", () => {
  const ranks = Object.fromEntries(BASE_STATS.map((s) => [s.id, 2]));
  const s = lab(
    ["precision_drills", "focus_lenses", "repair_tools", "solar_cells"],
    ranks,
  );
  const solar = s.addBuilding("solar", 0, 0, true);
  const miner = s.addBuilding("miner", 60, 0, true);
  const laser = s.addBuilding("laser", 0, 60, true);
  const repair = s.addBuilding("repair", -60, 0, true);
  s.rebuildNetwork();
  assert.ok(
    Math.abs(stats(solar).generation / BUILDINGS.solar.generation - 1.32) <
      1e-8,
  );
  assert.ok(Math.abs(stats(miner).rate - (4 / 3) * 1.25 * 1.1) < 1e-8);
  assert.ok(Math.abs(stats(laser).damage - 30 * 1.15 * 1.06) < 1e-8);
  assert.ok(Math.abs(stats(repair).rate - 20 * 1.25 * 1.1) < 1e-8);
  assert.equal(s.rules.buildSpeed, 1.1);
  s.damageBuilding(solar, 100);
  assert.equal(solar.maxHp - solar.hp, 96);
  const before = solar.hp,
    energy = solar.energy,
    minerals = s.minerals;
  s.setResearchLoadout(s.researchIds, { ...ranks, armor: 3, power: 3 });
  assert.equal(solar.hp, before);
  assert.equal(solar.energy, energy);
  assert.equal(s.minerals, minerals);
  assert.ok(stats(solar).generation > BUILDINGS.solar.generation * 1.32);
});

test("fabrication points shorten actual construction without bypassing its energy need", () => {
  const build = (ranks, supply) => {
    const s = lab([], ranks);
    if (supply) {
      const sun = s.addBuilding("solar", 0, 0, true);
      sun.level = 5;
      s.addBuilding("battery", 0, 60, true).energy = 200;
    }
    s.minerals = 10000;
    s.rebuildNetwork();
    const b = s.build("laser", 60, 0).building;
    tick(s, 2);
    return b.construction;
  };
  assert.ok(build({ fabrication: 10 }, true) > build({}, true));
  assert.equal(build({ fabrication: 20 }, false), 0);
});

test("only actual enemy hull damage earns combat XP; shields, overkill and missiles do not", () => {
  const s = lab();
  const enemy = s.spawnEnemy("fighter", 0);
  const hp = enemy.hp;
  enemy.shield = 10;
  s.damageEnemy(enemy, 10);
  assert.equal(s.xpEarned, 0);
  s.damageEnemy(enemy, 100000);
  assert.ok(Math.abs(s.xpEarned - hp * 0.05) < 1e-8);
  s.damageEnemy(enemy, 100000);
  const projectile = { hp: 20, interceptable: true, life: 1 };
  s.damageEnemy(projectile, 100000);
  assert.ok(Math.abs(s.xpEarned - hp * 0.05) < 1e-8);
});

test("drone repairs grant XP only for battle damage and preserve energy conservation", () => {
  const s = lab();
  const target = s.addBuilding("solar", 0, 0, true);
  const home = s.addBuilding("repair", 60, 0, true);
  s.rebuildNetwork();
  target.hp -= 50; // Untracked fixture damage earns no repair credit.
  s.drones = [
    {
      id: 999,
      homeId: home.id,
      targetId: target.id,
      x: 0,
      y: 0,
      hp: 60,
      energy: 80,
      returning: false,
      launchCooldown: 0,
    },
  ];
  tick(s, 1);
  assert.equal(s.xpEarned, 0);
  s.damageBuilding(target, 20);
  const xpBefore = s.xpEarned,
    energy = s.drones[0].energy;
  tick(s, 1);
  assert.ok(Math.abs(s.xpEarned - xpBefore - 2) < 1e-8);
  assert.ok(Math.abs(energy - s.drones[0].energy - 20) < 1e-8);
  assert.ok((target.repairXpDebt || 0) < 1e-8);
  // More healing of untracked fixture damage earns no additional XP.
  tick(s, 0.25);
  assert.ok(Math.abs(s.xpEarned - xpBefore - 2) < 1e-8);
});

test("rare ships arrive every third wave, reward values persist, and Classic stays unmodified", () => {
  const s = new Simulation(skirmish(518, "endless"));
  for (let wave = 1; wave <= 6; wave++) {
    s.enemies = [];
    s.callWave();
    const elites = s.enemies.filter((e) => e.rare);
    assert.equal(elites.length, wave % 3 === 0 ? 1 : 0);
    if (elites.length) {
      assert.equal(elites[0].intelValue, 2);
      assert.ok(elites[0].maxHp > 0);
    }
  }
  const saved = new Simulation(s.mission, "normal", s.snapshot());
  assert.deepEqual(saved.enemies, s.enemies);
  const classic = new Simulation(CLASSIC[0], "normal", null, ["hull_weave"], {
    armor: 20,
    harvest: 20,
  });
  assert.deepEqual(classic.statRanks, {});
  assert.equal(classic.rules.armor, 0);
  assert.equal(classic.spawnEnemy("mothership").intelValue, 0);
});

test("legacy Intel balances and purchases migrate once, with all owned research active", () => {
  let text = JSON.stringify({
    version: 2,
    completed: { 0: { stars: 3 } },
    challenges: {},
    intel: { mined: 1000, kills: 10 },
    endless: { cleared: 5 },
    research: {
      owned: ["solar_cells", "deep_storage", "precision_drills"],
      active: ["solar_cells"],
    },
  });
  const store = {
    getItem: () => text,
    setItem: (_, v) => {
      text = v;
    },
  };
  const p = loadProgress(store);
  assert.equal(researchBudget(p).earned, 23);
  assert.equal(researchBudget(p).available, 15);
  assert.deepEqual(p.research.active, p.research.owned);
  assert.equal(p.experience.xp, 250);
  assert.equal(experienceBudget(p).available, 2);
  saveProgress(p, store);
  assert.deepEqual(loadProgress(store), p);
  const s = lab();
  s.xpEarned = 20;
  bankExperience(p, s);
  assert.equal(p.experience.xp, 270);
});

test("fresh start writes a recoverable backup, clears progression and preserves settings", () => {
  const entries = new Map(),
    store = {
      getItem: (key) => entries.get(key),
      setItem: (key, value) => entries.set(key, value),
    };
  const p = freshProgress();
  p.intel.rare = 100;
  p.experience = { xp: 250, ranks: { armor: 2 } };
  p.completed[0] = { stars: 3 };
  p.research = { owned: ["solar_cells"], active: ["solar_cells"] };
  p.settings.quality = "low";
  const reset = resetProgress(p, store);
  assert.deepEqual(JSON.parse(entries.get(reset.backupKey)), p);
  assert.equal(researchBudget(reset.progress).available, 6);
  assert.equal(experienceBudget(reset.progress).level, 1);
  assert.equal(researchLoadout(reset.progress, CAMPAIGN[0]).length, 0);
  assert.deepEqual(reset.progress.completed, {});
  assert.equal(reset.progress.settings.quality, "low");
  assert.equal(loadProgress(store).resetToken, reset.backupKey);
  assert.throws(() =>
    resetProgress(p, {
      setItem: () => {
        throw new Error("quota");
      },
    }),
  );
});

test("XP stat screen shows available points and costs independently of Intel", () => {
  const p = freshProgress();
  p.experience.xp = 250;
  const view = researchView(p, "solar_cells", () => "", {
    page: "stats",
    inGame: true,
    mission: CAMPAIGN[1],
  });
  assert.match(view, /COMMAND LEVEL 3/);
  assert.match(view, /2<small> UNASSIGNED POINTS/);
  assert.match(view, /Improve Armor · 1 point/);
  assert.doesNotMatch(view, /LOADOUT|SLOTS/);
});

test("restoring a damaged mission objective earns repair XP and cannot repeat on reload", () => {
  const mission = {
    ...CAMPAIGN[1],
    station: true,
    stationHealth: 0.5,
    kind: "repair",
    goal: 0.9,
    waves: 0,
    firstWave: 10000,
  };
  const s = new Simulation(mission);
  s.asteroids = [];
  const station = s.buildings.find((b) => b.type === "station");
  const home = s.addBuilding("repair", 150, 120, true);
  s.drones = [
    {
      id: 999,
      homeId: home.id,
      targetId: station.id,
      x: station.x,
      y: station.y,
      hp: 60,
      energy: 80,
      returning: false,
      launchCooldown: 0,
    },
  ];
  const missing = station.maxHp - station.hp;
  assert.equal(station.repairXpDebt, missing);
  tick(s, 1);
  const p = freshProgress();
  assert.ok(Math.abs(bankExperience(p, s).xp - 2) < 1e-8);
  const restored = new Simulation(mission, "normal", s.snapshot());
  assert.equal(bankExperience(p, restored).xp, 0);
  assert.ok(
    Math.abs(
      restored.buildings.find((b) => b.id === station.id).repairXpDebt -
        (missing - 20),
    ) < 1e-8,
  );
});
