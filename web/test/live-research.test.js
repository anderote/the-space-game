import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { CAMPAIGN, CLASSIC, skirmish } from "../src/content.js";
import {
  freshProgress,
  bankIntel,
  bankExperience,
  saveProgress,
  loadProgress,
} from "../src/storage.js";
import {
  intelActivity,
  researchBudget,
  normalizeIntel,
  buyResearch,
} from "../src/research.js";
import { researchView } from "../src/research-view.js";
const tick = (s, seconds) => {
  for (let n = 0; n < seconds * 40; n++) s.update(0.025);
};
function lab(mission = CAMPAIGN[1]) {
  const s = new Simulation({ ...mission, firstWave: 10000 });
  s.asteroids = [];
  s.buildings = [];
  s.links = [];
  return s;
}

test("only rare player-defeated ships award Intel, once", () => {
  const s = lab(),
    p = freshProgress();
  s.addBuilding("solar", 0, 0, true);
  s.rebuildNetwork();
  const normal = s.spawnEnemy("fighter", 0);
  const elite = s.spawnEnemy("fighter", 0, true);
  const command = s.spawnEnemy("mothership", 0);
  const selfDestruct = s.spawnEnemy("suicide", 0, true);
  for (const e of [normal, elite, command]) s.damageEnemy(e, 100000, true);
  selfDestruct.hp = 0;
  const projectile = { hp: 20, interceptable: true, life: 5 };
  const xp = s.xpEarned;
  s.damageEnemy(projectile, 30);
  assert.equal(s.xpEarned, xp);
  tick(s, 0.025);
  assert.equal(bankIntel(p, s), 5);
  assert.equal(bankIntel(p, s), 0);
  assert.equal(researchBudget(p).available, 11);
  tick(s, 0.05);
  assert.equal(bankIntel(p, s), 0);
});

test("banking and resuming cannot duplicate rare Intel or XP", () => {
  let saved;
  const store = {
    getItem: () => saved,
    setItem: (_, value) => {
      saved = value;
    },
  };
  const p = freshProgress(),
    s = new Simulation(CAMPAIGN[1]);
  s.intelCollected = 5;
  s.xpEarned = 260;
  assert.equal(bankIntel(p, s), 5);
  assert.deepEqual(bankExperience(p, s), {
    xp: 260,
    levels: 2,
    mastery: 0,
    masteryLevels: 0,
  });
  p.active = s.snapshot();
  saveProgress(p, store);
  const restored = loadProgress(store),
    run = new Simulation(CAMPAIGN[1], "normal", restored.active);
  assert.equal(bankIntel(restored, run), 0);
  assert.deepEqual(bankExperience(restored, run), {
    xp: 0,
    levels: 0,
    mastery: 0,
    masteryLevels: 0,
  });
  run.intelCollected += 2;
  run.xpEarned += 20;
  assert.equal(bankIntel(restored, run), 2);
  assert.equal(bankExperience(restored, run).xp, 20);
  assert.equal(restored.experience.xp, 280);
});

test("legacy snapshots start new tracking now and malformed counters are sanitized", () => {
  const s = new Simulation(CAMPAIGN[1]),
    snap = s.snapshot();
  delete snap.intelCredit;
  delete snap.intelCollected;
  delete snap.xpEarned;
  delete snap.xpCredit;
  const resumed = new Simulation(CAMPAIGN[1], "normal", snap),
    p = freshProgress();
  assert.equal(bankIntel(p, resumed), 0);
  assert.equal(bankExperience(p, resumed).xp, 0);
  resumed.intelCollected = 2;
  assert.equal(bankIntel(p, resumed), 2);
  assert.deepEqual(normalizeIntel({ rare: Infinity, legacy: -10 }), {
    rare: 0,
    legacy: 0,
  });
  assert.deepEqual(normalizeIntel({ rare: "5", legacy: 4.9 }), {
    rare: 0,
    legacy: 4,
  });
});

test("Classic and Sandbox earn no progression; losses retain banked Intel and XP", () => {
  const p = freshProgress();
  for (const m of [CLASSIC[0], skirmish(42, "sandbox")]) {
    const s = new Simulation(m);
    s.intelCollected = 100;
    s.xpEarned = 1000;
    assert.equal(bankIntel(p, s), 0);
    assert.equal(bankExperience(p, s).xp, 0);
  }
  const s = new Simulation(skirmish(42, "endless"));
  s.intelCollected = 2;
  s.xpEarned = 200;
  s.finish("lost");
  assert.equal(bankIntel(p, s), 2);
  assert.equal(bankExperience(p, s).xp, 200);
  assert.equal(researchBudget(p).available, 8);
});

test("real extraction earns XP; recycling and normal mining do not award Intel", () => {
  const s = lab(),
    p = freshProgress();
  const solar = s.addBuilding("solar", 0, 0, true);
  solar.level = 3;
  s.addBuilding("miner", 60, 0, true);
  s.asteroids = [{ id: 999, x: 90, y: 0, radius: 10, ore: 210, maxOre: 210 }];
  s.rebuildNetwork();
  tick(s, 170);
  assert.equal(s.mined, 210);
  assert.equal(bankIntel(p, s), 0);
  assert.ok(Math.abs(bankExperience(p, s).xp - 42) < 1e-8);
  s.recycle(s.buildings.find((b) => b.type === "miner").id);
  assert.equal(bankExperience(p, s).xp, 0);
});

test("field Intel can buy and activate research without restarting the simulation", () => {
  const p = freshProgress(),
    s = lab();
  const solar = s.addBuilding("solar", 0, 0, true);
  s.addBuilding("miner", 60, 0, true);
  s.rebuildNetwork();
  s.intelCollected = 2;
  bankIntel(p, s);
  buyResearch(p, "solar_cells");
  buyResearch(p, "precision_drills");
  const generation = stats(solar).generation,
    miningRate = stats(s.buildings[1]).rate;
  const time = s.time,
    minerals = s.minerals;
  s.setResearchLoadout(p.research.active);
  assert.equal(s.time, time);
  assert.equal(s.minerals, minerals);
  assert.equal(stats(solar).generation, generation * 1.2);
  assert.equal(stats(s.buildings[1]).rate, miningRate * 1.25);
  assert.equal(s.generation, generation * 1.2);
  assert.deepEqual(s.snapshot().researchIds, p.research.active);
});

test("hull and capacity toggles cannot heal structures, recharge storage, or mint freight", () => {
  const s = lab(),
    solar = s.addBuilding("solar", 0, 0, true),
    battery = s.addBuilding("battery", 60, 0, true);
  solar.hp = 300;
  battery.energy = 160;
  const minerals = s.minerals;
  for (let i = 0; i < 4; i++) {
    s.setResearchLoadout([
      "hull_weave",
      "solar_overdrive",
      "deep_storage",
      "expedition_cargo",
    ]);
    assert.ok(Math.abs(solar.hp / solar.maxHp - 0.5) < 1e-9);
    assert.equal(battery.energy, 160);
    assert.equal(s.minerals, minerals);
    s.setResearchLoadout([]);
    assert.ok(Math.abs(solar.hp - 300) < 1e-9);
  }
  s.setResearchLoadout(["deep_storage", "drone_cells"]);
  battery.energy = 260;
  s.drones = [{ energy: 120 }];
  s.setResearchLoadout([]);
  assert.equal(battery.energy, 200);
  assert.equal(s.drones[0].energy, 80);
  s.setResearchLoadout(["deep_storage", "drone_cells"]);
  assert.equal(battery.energy, 200);
  assert.equal(s.drones[0].energy, 80);
});

test("live link research connects eligible structures and removes out-of-range links on unequip", () => {
  const s = lab();
  s.addBuilding("solar", 0, 0, true);
  s.addBuilding("battery", 100, 0, true);
  s.rebuildNetwork();
  assert.equal(s.links.length, 0);
  s.setResearchLoadout(["long_links"]);
  assert.equal(s.links.length, 1);
  s.setResearchLoadout([]);
  assert.equal(s.links.length, 0);
  const c = new Simulation(CLASSIC[0]);
  c.setResearchLoadout(["hull_weave", "solar_cells"]);
  assert.deepEqual(c.researchIds, []);
  assert.equal(c.buildings[0].maxHp, 600);
});

test("research UI shows live operation context, earning progress, and the freight exception", () => {
  const p = freshProgress();
  p.intel = { rare: 5, legacy: 0 };
  p.experience = { xp: 123, ranks: {} };
  const view = researchView(p, "expedition_cargo", () => "", {
    inGame: true,
    mission: CAMPAIGN[1],
  });
  assert.match(view, /OPERATION PAUSED \/ LIVE RESEARCH/);
  assert.match(view, /Return to operation/);
  assert.match(view, /Elite ships \+2 · Motherships \+3/);
  assert.match(view, /40 TECHNOLOGIES ACTIVE/);
  assert.doesNotMatch(view, /LOADOUT WEIGHT|SLOTS|Unequip technology/);
  assert.match(view, /LAUNCH ONLY/);
});
