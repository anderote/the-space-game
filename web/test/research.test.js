import test from "node:test";
import assert from "node:assert/strict";
import {
  TECHNOLOGIES,
  TECH_BY_ID,
  normalizeResearch,
  researchBudget,
  buyResearch,
  resetResearch,
  researchLoadout,
  researchRules,
} from "../src/research.js";
import { Simulation, stats } from "../src/engine.js";
import {
  CAMPAIGN,
  CLASSIC,
  CHALLENGES,
  skirmish,
  BUILDINGS,
} from "../src/content.js";
import {
  freshProgress,
  recordVictory,
  loadProgress,
  saveProgress,
} from "../src/storage.js";
const tick = (s, t) => {
  for (let i = 0; i < t * 40; i++) s.update(0.025);
};
const rich = () => {
  const p = freshProgress();
  p.intel.rare = 1000;
  return p;
};
function lab(ids = []) {
  const s = new Simulation(
    { ...skirmish(47, "sandbox"), kind: "test" },
    "normal",
    null,
    ids,
  );
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.networkDirty = true;
  return s;
}
const add = (s, type, x = 0, y = 0) => s.addBuilding(type, x, y, true);
test("research graph has four branches and an acyclic automation side research", () => {
  const seen = new Set();
  for (const t of TECHNOLOGIES) {
    assert.ok(
      t.requires.every((id) => seen.has(id)),
      t.id,
    );
    assert.ok(t.cost > 0);
    seen.add(t.id);
  }
  assert.equal(seen.size, 41);
  for (const branch of ["power", "industry", "weapons", "support"])
    assert.equal(
      TECHNOLOGIES.filter((t) => t.branch === branch).length,
      branch === "power" ? 11 : 10,
    );
});
test("starter Intel buys and equips a root exactly once", () => {
  const p = freshProgress();
  assert.equal(researchBudget(p).available, 6);
  assert.equal(buyResearch(p, "solar_cells").ok, true);
  assert.equal(researchBudget(p).available, 4);
  assert.deepEqual(p.research.active, ["solar_cells"]);
  assert.equal(buyResearch(p, "solar_cells").ok, false);
  assert.equal(researchBudget(p).available, 4);
});
test("research requires prerequisites and enough Intel", () => {
  const p = freshProgress();
  assert.equal(buyResearch(p, "storm_shield").ok, false);
  buyResearch(p, "solar_cells");
  buyResearch(p, "deep_storage");
  assert.equal(buyResearch(p, "long_links").ok, false);
  assert.equal(researchBudget(p).available, 0);
});
test("new achievement records do not award rare-ship Intel", () => {
  const p = freshProgress();
  for (const m of [CAMPAIGN[0], CHALLENGES[0], CLASSIC[0]])
    recordVictory(p, m, { lost: 0, time: 0 });
  assert.equal(researchBudget(p).earned, 6);
  assert.equal(p.completed[0].stars, 3);
});

test("endless wave records cannot generate Intel without rare-ship kills", () => {
  const p = freshProgress();
  p.endless = { wave: 200, cleared: 200 };
  assert.equal(researchBudget(p).earned, 6);
});

test("every owned technology stays active with no equipment limit", () => {
  const p = rich();
  for (const t of TECHNOLOGIES)
    assert.equal(buyResearch(p, t.id).ok, true, t.id);
  assert.equal(p.research.owned.length, 41);
  assert.deepEqual(p.research.active, p.research.owned);
  p.research.active = [];
  assert.equal(researchLoadout(p, CAMPAIGN[1]).length, 41);
  const loaded = loadProgress({ getItem: () => JSON.stringify(p) });
  assert.equal(loaded.research.active.length, 41);
});

test("free respec refunds exactly invested Intel", () => {
  const p = rich();
  buyResearch(p, "solar_cells");
  buyResearch(p, "deep_storage");
  const before = researchBudget(p);
  resetResearch(p);
  assert.equal(researchBudget(p).available, before.available + before.spent);
  assert.deepEqual(p.research.active, []);
});
test("old saves migrate without losing stars or inventing equipped research", () => {
  let text = JSON.stringify({
    version: 2,
    completed: { 0: { stars: 3 } },
    challenges: {},
  });
  const store = { getItem: () => text, setItem: (_, v) => (text = v) };
  const p = loadProgress(store);
  assert.deepEqual(p.research, { owned: [], active: [] });
  assert.equal(researchBudget(p).earned, 12);
  buyResearch(p, "solar_cells");
  saveProgress(p, store);
  assert.deepEqual(loadProgress(store).research, p.research);
});
test("research sanitization rejects unknown IDs, orphan descendants and duplicate loadout entries", () => {
  assert.deepEqual(
    normalizeResearch({
      owned: ["made_up", "storm_shield", "solar_cells"],
      active: ["made_up", "solar_cells", "solar_cells", "storm_shield"],
    }),
    { owned: ["solar_cells"], active: ["solar_cells"] },
  );
});
test("classic operations ignore every research effect and never mutate shared building definitions", () => {
  const ids = TECHNOLOGIES.map((t) => t.id),
    s = new Simulation(CLASSIC[0], "normal", null, ids);
  assert.deepEqual(s.researchIds, []);
  assert.equal(s.minerals, 500);
  assert.equal(stats(s.buildings[0]).hp, 600);
  assert.equal(stats(s.buildings[0]).link, 90);
  new Simulation(CAMPAIGN[0], "normal", null, ids);
  assert.equal(BUILDINGS.solar.hp, 600);
});
test("research and base stats persist across new games; saved cargo is never regranted", () => {
  const p = rich();
  for (const t of TECHNOLOGIES.filter((t) => t.branch === "industry"))
    buyResearch(p, t.id);
  p.experience = { xp: 250, ranks: { harvest: 2 } };
  const ids = researchLoadout(p, CAMPAIGN[1]);
  const first = new Simulation(
    CAMPAIGN[1],
    "normal",
    null,
    ids,
    p.experience.ranks,
  );
  assert.equal(first.minerals, CAMPAIGN[1].minerals + 900);
  tick(first, 6);
  const saved = new Simulation(CAMPAIGN[1], "normal", first.snapshot());
  assert.equal(saved.minerals, first.minerals);
  assert.deepEqual(saved.statRanks, { harvest: 2 });
  const next = new Simulation(
    CAMPAIGN[2],
    "normal",
    null,
    researchLoadout(p, CAMPAIGN[2]),
    p.experience.ranks,
  );
  assert.deepEqual(next.researchIds, first.researchIds);
  assert.deepEqual(next.statRanks, first.statRanks);
  assert.ok(next.rules.miningYield > 1.7);
});

test("old active snapshots remain unmodified even after buying new research", () => {
  const s = new Simulation(CAMPAIGN[0]),
    snap = s.snapshot();
  delete snap.researchIds;
  const restored = new Simulation(CAMPAIGN[0], "normal", snap, ["hull_weave"]);
  assert.equal(restored.buildings[0].maxHp, 600);
  assert.deepEqual(restored.researchIds, []);
});
test("power tech changes generation, storage, graph reach, and the overdrive hull tradeoff", () => {
  const s = lab([
    "solar_cells",
    "solar_overdrive",
    "deep_storage",
    "long_links",
  ]);
  const sun = add(s, "solar"),
    store = add(s, "battery", 100);
  s.rebuildNetwork();
  assert.equal(stats(sun).hp, 480);
  assert.ok(
    Math.abs(stats(sun).generation - BUILDINGS.solar.generation * 1.68) < 1e-8,
  );
  assert.equal(stats(store).capacity, 280);
  assert.equal(s.links.length, 1);
  assert.equal(stats(sun).link, 105);
});
test("storm shielding retains half solar output", () => {
  const s = lab(["storm_shield"]);
  s.mission.storm = true;
  const sun = add(s, "solar");
  sun.energy = 0;
  s.time = 31;
  tick(s, 0.55);
  assert.ok(Math.abs(sun.energy - 0.45) < 1e-8);
});
test("drill and survey research changes accessible extraction without creating ore", () => {
  const s = lab(["precision_drills", "survey_optics"]);
  add(s, "solar");
  const miner = add(s, "miner", 60);
  s.asteroids = [{ id: 999, x: 115, y: 0, radius: 10, ore: 9, maxOre: 9 }];
  s.rebuildNetwork();
  tick(s, 0.025);
  assert.equal(s.mined, 5);
  tick(s, 4);
  assert.equal(s.mined, 9);
  assert.equal(s.asteroids[0].ore, 0);
  assert.equal(stats(miner).range, 50);
});
test("fabrication research shortens construction without removing its energy requirement", () => {
  function build(ids) {
    const s = lab(ids);
    const sun = add(s, "solar");
    sun.level = 3;
    add(s, "battery", 0, 60).energy = 200;
    s.rebuildNetwork();
    const b = s.build("laser", 60, 0).building;
    tick(s, 3);
    return b.construction;
  }
  assert.ok(build(["rapid_fabrication"]) > build([]));
  const empty = lab(["rapid_fabrication"]);
  const b = empty.build("laser", 100, 0).building;
  tick(empty, 10);
  assert.equal(b.construction, 0);
});
test("salvage improves upgrade recovery without a purchase/recycle profit loop", () => {
  const s = lab(["salvage"]),
    b = add(s, "laser");
  s.upgrade(b.id);
  assert.equal(s.recycle(b.id).refund, 180);
  const fresh = add(s, "laser");
  assert.equal(s.recycle(fresh.id).refund, 100);
});
test("weapon tech changes damage, buffer, range and blast tradeoff", () => {
  const s = lab([
    "focus_lenses",
    "weapon_buffers",
    "missile_guidance",
    "proximity_warheads",
  ]);
  assert.equal(stats(add(s, "laser")).damage, 34.5);
  assert.equal(stats(add(s, "laser")).capacity, 1.5);
  const missile = stats(add(s, "missile"));
  assert.ok(Math.abs(missile.range - 460) < 1e-8);
  assert.equal(missile.damage, 382.5);
  assert.equal(missile.splash, 52);
});
test("hull research applies to player structures and preserves derelict objective hull", () => {
  const s = lab(["hull_weave"]);
  const sun = add(s, "solar"),
    station = add(s, "station");
  assert.equal(sun.maxHp, 690);
  assert.equal(station.maxHp, 1600);
  sun.hp -= 100;
  s.upgrade(sun.id);
  assert.ok(Math.abs(sun.maxHp - sun.hp - 100) < 1e-8);
});
test("autoseal waits after damage and consumes energy while repairing", () => {
  const s = lab(["autoseal"]);
  const sun = add(s, "solar");
  s.rebuildNetwork();
  s.damageBuilding(sun, 100);
  tick(s, 7);
  assert.equal(sun.hp, 500);
  tick(s, 2);
  assert.ok(sun.hp > 500);
  assert.ok(sun.hp < 515);
  assert.ok(sun.energy < 4);
});
test("capacitive armor absorbs damage only when the network can supply its energy", () => {
  const s = lab(["capacitive_armor"]);
  const sun = add(s, "solar");
  sun.energy = 4;
  s.rebuildNetwork();
  s.damageBuilding(sun, 40);
  assert.equal(sun.hp, 570);
  assert.equal(sun.energy, 3);
  sun.energy = 0;
  s.damageBuilding(sun, 40);
  assert.equal(sun.hp, 530);
});
test("drone research increases carried reserves and repair throughput", () => {
  const s = lab(["drone_cells", "repair_tools"]);
  const sun = add(s, "solar"),
    home = add(s, "repair", 60);
  home.droneCharge = 9;
  s.rebuildNetwork();
  s.update(0.025);
  assert.equal(s.drones[0].energy, 120);
  const d = s.drones[0];
  d.hp = 60;
  d.returning = false;
  d.launchCooldown = 0;
  sun.hp = 500;
  d.targetId = sun.id;
  d.x = 0;
  d.y = 0;
  tick(s, 1);
  assert.equal(sun.hp, 525);
  assert.equal(d.energy, 95);
});

test("loaded research cannot exceed earned Intel and invalid difficulty recovers", () => {
  const p = freshProgress();
  p.research = {
    owned: TECHNOLOGIES.map((t) => t.id),
    active: ["solar_overdrive"],
  };
  p.settings.difficulty = "not-a-mode";
  const restored = loadProgress({ getItem: () => JSON.stringify(p) });
  assert.ok(researchBudget(restored).spent <= researchBudget(restored).earned);
  assert.equal(restored.settings.difficulty, "normal");
  assert.ok(!restored.research.owned.includes("solar_overdrive"));
});
