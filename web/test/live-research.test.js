import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { CAMPAIGN, CLASSIC, skirmish } from "../src/content.js";
import {
  freshProgress,
  bankIntel,
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

test("mining and combat pay only at thresholds and partial Intel carries across operations", () => {
  const p = freshProgress(),
    a = new Simulation(CAMPAIGN[0]);
  a.mined = 199.5;
  a.combatKills = 4;
  assert.equal(bankIntel(p, a), 0);
  const b = new Simulation(CAMPAIGN[1]);
  b.mined = 0.5;
  b.combatKills = 1;
  assert.equal(bankIntel(p, b), 2);
  assert.equal(researchBudget(p).available, 8);
  assert.deepEqual(intelActivity(p), { earned: 2, mined: 0, kills: 0 });
  b.mined += 425;
  b.combatKills += 11;
  assert.equal(bankIntel(p, b), 4);
  assert.equal(b.intelCredit.earned, 6);
  assert.deepEqual(intelActivity(p), { earned: 6, mined: 25, kills: 1 });
});

test("banking, saving, loading, and resuming never credit the same activity twice", () => {
  let saved;
  const store = {
    getItem: () => saved,
    setItem: (_, value) => {
      saved = value;
    },
  };
  const p = freshProgress(),
    s = new Simulation(CAMPAIGN[1]);
  s.mined = 260;
  s.combatKills = 6;
  assert.equal(bankIntel(p, s), 2);
  assert.equal(bankIntel(p, s), 0);
  p.active = s.snapshot();
  saveProgress(p, store);
  const restored = loadProgress(store),
    run = new Simulation(CAMPAIGN[1], "normal", restored.active);
  assert.equal(bankIntel(restored, run), 0);
  run.mined += 140;
  run.combatKills += 4;
  assert.equal(bankIntel(restored, run), 2);
  assert.deepEqual(restored.intel, { mined: 400, kills: 10 });
});

test("old snapshots begin tracking at migration and malformed activity is sanitized", () => {
  const s = new Simulation(CAMPAIGN[1]);
  s.mined = 900;
  const snap = s.snapshot();
  delete snap.intelCredit;
  delete snap.combatKills;
  const resumed = new Simulation(CAMPAIGN[1], "normal", snap),
    p = freshProgress();
  assert.equal(bankIntel(p, resumed), 0);
  resumed.mined += 200;
  assert.equal(bankIntel(p, resumed), 1);
  assert.deepEqual(normalizeIntel({ mined: Infinity, kills: -10 }), {
    mined: 0,
    kills: 0,
  });
  assert.deepEqual(normalizeIntel({ mined: "500", kills: 4.9 }), {
    mined: 0,
    kills: 4,
  });
});

test("Classic and Sandbox never award activity Intel; losses retain earned Intel", () => {
  const p = freshProgress();
  for (const m of [CLASSIC[0], skirmish(42, "sandbox")]) {
    const s = new Simulation(m);
    s.mined = 1000;
    s.combatKills = 100;
    assert.equal(bankIntel(p, s), 0);
  }
  const s = new Simulation(skirmish(42, "endless"));
  s.mined = 200;
  s.combatKills = 5;
  s.finish("lost");
  assert.equal(bankIntel(p, s), 2);
  assert.equal(researchBudget(p).available, 8);
});

test("actual extraction earns Intel while recycling refunds do not", () => {
  const s = lab(),
    p = freshProgress();
  const solar = s.addBuilding("solar", 0, 0, true);
  solar.level = 3;
  s.addBuilding("miner", 60, 0, true);
  s.asteroids = [{ id: 999, x: 90, y: 0, radius: 10, ore: 210, maxOre: 210 }];
  s.rebuildNetwork();
  tick(s, 170);
  assert.equal(s.mined, 210);
  assert.equal(bankIntel(p, s), 1);
  const minerals = s.minerals;
  s.recycle(s.buildings.find((b) => b.type === "miner").id);
  assert.ok(s.minerals > minerals);
  assert.equal(bankIntel(p, s), 0);
});

test("player kills count once; self-destructing ships and intercepted missiles do not grant ship Intel", () => {
  const s = lab();
  s.addBuilding("solar", 0, 0, true);
  s.rebuildNetwork();
  for (let i = 0; i < 5; i++) {
    const e = s.spawnEnemy("fighter", 0);
    s.damageEnemy(e, 10000, true);
  }
  const selfDestruct = s.spawnEnemy("suicide", 0);
  selfDestruct.hp = 0;
  const projectile = { hp: 20, interceptable: true, life: 5 };
  s.damageEnemy(projectile, 30);
  tick(s, 0.025);
  assert.equal(s.kills, 6);
  assert.equal(s.combatKills, 5);
  const p = freshProgress();
  assert.equal(bankIntel(p, s), 1);
  tick(s, 0.05);
  assert.equal(bankIntel(p, s), 0);
});

test("field Intel can buy and activate research without restarting the simulation", () => {
  const p = freshProgress(),
    s = lab();
  const solar = s.addBuilding("solar", 0, 0, true);
  s.addBuilding("miner", 60, 0, true);
  s.rebuildNetwork();
  s.mined = 400;
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
  p.intel = { mined: 123, kills: 3 };
  const view = researchView(p, "expedition_cargo", () => "", {
    inGame: true,
    mission: CAMPAIGN[1],
  });
  assert.match(view, /OPERATION PAUSED \/ LIVE RESEARCH/);
  assert.match(view, /Return to operation/);
  assert.match(view, /123 <small>\/ 200 MINED/);
  assert.match(view, /3 <small>\/ 5 SHIPS DEFEATED/);
  assert.match(view, /LAUNCH ONLY/);
});
