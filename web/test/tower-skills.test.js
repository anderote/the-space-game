import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { BUILDINGS, CLASSIC, skirmish } from "../src/content.js";
import { freshProgress, loadProgress, saveProgress } from "../src/storage.js";
import {
  buyBaseStat,
  buyTowerSkill,
  experienceBudget,
  normalizeExperience,
} from "../src/experience.js";
import { TOWER_TYPES, normalizeTowerRanks } from "../src/tower-skills.js";
import { researchView } from "../src/research-view.js";
const near = (actual, expected) =>
  assert.ok(Math.abs(actual - expected) < 1e-7, `${actual} versus ${expected}`);
const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
function lab(ranks = {}, towers = {}, ids = []) {
  const s = new Simulation(
    skirmish(731, "sandbox"),
    "normal",
    null,
    ids,
    ranks,
    towers,
  );
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.networkDirty = true;
  s.minerals = 100000;
  return s;
}
function add(s, type, x = 0, y = 0, level = 1) {
  const b = s.addBuilding(type, x, y, true);
  b.level = level;
  b.hp = b.maxHp = stats(b).hp;
  b.energy = stats(b).capacity || 0;
  return b;
}

test("construction discount changes actual build, affordability, branch prices and refunds", () => {
  const s = lab({ economy: 20 });
  add(s, "solar", 0, 0, 5);
  s.rebuildNetwork();
  assert.equal(s.buildingCost("relay"), 16);
  assert.equal(s.buildingCost("solar"), 160);
  s.minerals = 79;
  assert.equal(s.placement("laser", 60, 0).ok, false);
  s.minerals = 80;
  const b = s.build("laser", 60, 0).building;
  assert.equal(s.minerals, 0);
  assert.equal(b.baseCost, 80);
  tick(s, 10);
  assert.equal(b.construction, 1);
  assert.equal(s.upgradeCost(b), 80);
  assert.equal(s.upgradeCost(b, "thel"), 400);
  s.minerals = 400;
  assert.equal(s.upgrade(b.id, "thel").ok, true);
  assert.equal(b.investment, 480);
  assert.equal(b.upgradeSpent, 400);
  assert.equal(s.recycle(b.id).refund, 280);
  assert.equal(s.minerals, 280);
  assert.equal(BUILDINGS.laser.cost, 100);
});

test("buying a discount cannot inflate past purchase refunds or a build/recycle loop", () => {
  const s = lab();
  s.rebuildNetwork();
  const old = s.build("solar", 0, 0).building;
  s.setResearchLoadout([], { economy: 20 });
  assert.equal(old.baseCost, 200);
  assert.equal(s.recycle(old.id).refund, 200);
  const before = s.minerals;
  const next = s.build("solar", 0, 0).building;
  assert.equal(before - s.minerals, 160);
  assert.equal(s.recycle(next.id).refund, 160);
  assert.equal(s.minerals, before);
});

test("Clock speed increases actual mining cycles without doubling yield per cycle", () => {
  const run = (ranks) => {
    const s = lab(ranks);
    add(s, "solar", 0, 0, 5);
    const miner = add(s, "miner", 60, 0);
    s.asteroids = [
      { id: 999, x: 95, y: 0, radius: 10, ore: 1000, maxOre: 1000 },
    ];
    s.rebuildNetwork();
    const configured = stats(miner);
    near(configured.rate * configured.miningInterval, 4);
    tick(s, 15);
    return s.mined;
  };
  assert.ok(run({ fabrication: 4 }) > run({}));
  const speed = lab({ fabrication: 20 });
  near(stats(add(speed, "miner")).miningInterval, 1.5);
  near(stats(speed.buildings[0]).rate * 60, 160);
});

test("Clock speed doubles solar pulse frequency while preserving energy per pulse", () => {
  const run = (ranks, towers = {}) => {
    const s = lab(ranks, towers),
      solar = add(s, "solar");
    s.rebuildNetwork();
    let generated = 0;
    for (let i = 0; i < 440; i++) {
      solar.energy = 0;
      s.update(0.025);
      generated += solar.energy;
    }
    return { generated, configured: stats(solar) };
  };
  const normal = run({}),
    boosted = run({ fabrication: 20 });
  near(boosted.configured.generationInterval, 0.275);
  near(
    boosted.configured.generation * boosted.configured.generationInterval,
    0.9,
  );
  near(boosted.generated, normal.generated * 2);
  const stacked = run(
    { fabrication: 20 },
    { solar: { speed: 20, output: 10 } },
  );
  near(stacked.configured.generationInterval, 0.1375);
  near(
    stacked.configured.generation * stacked.configured.generationInterval,
    1.35,
  );
  near(stacked.generated, normal.generated * 6);
});

test("live Clock and mastery upgrades preserve the elapsed fraction of active cycles", () => {
  const s = lab();
  const sun = add(s, "solar"),
    miner = add(s, "miner", 60, 0);
  sun.generationCooldown = 0.275;
  miner.mineCooldown = 1.5;
  miner.buildCooldown = 0.4;
  const energy = sun.energy;
  s.setResearchLoadout([], { fabrication: 20 }, { miner: { speed: 20 } });
  near(sun.generationCooldown, 0.1375);
  near(miner.mineCooldown, 0.375);
  near(miner.buildCooldown, 0.2);
  assert.equal(sun.energy, energy);
});

test("base stats and tower skills spend independent persistent XP budgets", () => {
  const p = freshProgress();
  p.experience.xp = 250;
  p.experience.masteryXp = 100;
  assert.equal(buyBaseStat(p, "economy").ok, true);
  assert.equal(buyTowerSkill(p, "laser", "damage").ok, true);
  assert.equal(experienceBudget(p).available, 1);
  assert.equal(buyTowerSkill(p, "repair", "repairRate").ok, false);
  assert.equal(buyBaseStat(p, "fabrication").ok, true);
  assert.equal(buyTowerSkill(p, "laser", "unknown").ok, false);
  let saved;
  const store = {
    getItem: () => saved,
    setItem: (_, v) => {
      saved = v;
    },
  };
  saveProgress(p, store);
  const loaded = loadProgress(store);
  assert.deepEqual(loaded.experience.towers, { laser: { damage: 1 } });
  assert.equal(experienceBudget(loaded).spent, 2);
  const clean = normalizeExperience({
    xp: 100,
    ranks: { armor: 1 },
    towers: { solar: { hull: 99 } },
  });
  assert.deepEqual(clean.towers, {});
  assert.deepEqual(
    normalizeTowerRanks({
      laser: { damage: Infinity, shields: -1 },
      madeUp: { damage: 9 },
    }),
    {},
  );
});

test("old Build speed ranks become Clock speed without losing points", () => {
  const old = {
    ...freshProgress(),
    experience: { xp: 1000, ranks: { fabrication: 4, harvest: 1 } },
  };
  const p = loadProgress({ getItem: () => JSON.stringify(old) });
  assert.equal(p.experience.ranks.fabrication, 4);
  assert.equal(experienceBudget(p).spent, 5);
  const s = lab(p.experience.ranks);
  near(s.rules.buildSpeed, 1.2);
  near(s.rules.miningSpeed, 1.2);
  near(s.rules.generationSpeed, 1.2);
});

test("every tower class exposes meaningful skills and finite max-rank stats", () => {
  assert.equal(TOWER_TYPES.length, 9);
  const towers = Object.fromEntries(
    TOWER_TYPES.map((t) => [
      t.id,
      Object.fromEntries(t.skills.map((skill) => [skill.id, skill.max])),
    ]),
  );
  const s = lab({ fabrication: 20, economy: 20 }, towers);
  for (const t of TOWER_TYPES) {
    assert.ok(t.skills.some((skill) => skill.id === "hull"));
    assert.ok(t.skills.some((skill) => skill.id === "shields"));
    const b = add(
      s,
      t.id === "pulser" ? "laser" : t.id,
      0,
      0,
      t.id === "pulser" ? 2 : 1,
    );
    const configured = stats(b);
    for (const value of Object.values(configured))
      if (typeof value === "number") assert.ok(Number.isFinite(value), t.id);
    assert.ok(configured.armor < 1 && configured.shield < 1);
  }
});

test("Basic laser, Pulser, missile and THEL specializations stay independent", () => {
  const s = lab(
    {},
    {
      laser: { damage: 2, fireRate: 4, range: 5, hull: 3 },
      pulser: { damage: 1 },
    },
  );
  const basic = stats(add(s, "laser")),
    pulser = stats(add(s, "laser", 0, 0, 2));
  near(basic.damage, 33);
  near(basic.interval, 1 / 1.12);
  near(basic.range, 103.5);
  near(basic.hp, 230);
  near(pulser.damage, 12.6);
  near(pulser.interval, 0.5);
  near(pulser.range, 110);
  near(stats(add(s, "missile")).damage, 450);
  near(stats(add(s, "thel")).beamDamageMultiplier, 1);
});

test("faster firing increases actual laser output and energy consumption", () => {
  const run = (towers) => {
    const s = lab({}, towers);
    s.diff = { ...s.diff, damage: 0 };
    add(s, "solar", 0, 0, 5);
    add(s, "battery", 0, 60, 4);
    add(s, "laser", 60, 0);
    s.rebuildNetwork();
    const e = s.spawnEnemy("fighter", 0);
    e.x = 90;
    e.y = 0;
    e.hp = e.maxHp = 100000;
    let energy = 0;
    for (let i = 0; i < 200; i++) {
      s.update(0.025);
      energy += s.drawnThisTick;
    }
    return { damage: 100000 - e.hp, energy };
  };
  const normal = run({}),
    boosted = run({ laser: { fireRate: 20 } });
  assert.ok(boosted.damage > normal.damage);
  assert.ok(boosted.energy > normal.energy);
});

test("THEL cycling and damage mastery strengthen the full beam and spend proportionate energy", () => {
  const run = (towers) => {
    const s = lab({}, towers);
    s.diff = { ...s.diff, damage: 0 };
    add(s, "solar", 0, 0, 5);
    add(s, "battery", 0, 60, 4);
    add(s, "thel", 60, 0);
    s.rebuildNetwork();
    const e = s.spawnEnemy("fighter", 0);
    e.x = 90;
    e.y = 0;
    e.hp = e.maxHp = 100000;
    tick(s, 1);
    return 100000 - e.hp;
  };
  near(run({ thel: { damage: 10, fireRate: 10 } }), run({}) * 1.5 * 1.3);
});

test("tower armor and powered shields stack safely and fail when power is unavailable", () => {
  const s = lab({ armor: 20 }, { laser: { armor: 20, shields: 20 } }, [
    "capacitive_armor",
  ]);
  const source = add(s, "solar", 0, 0, 5),
    laser = add(s, "laser", 60, 0);
  s.rebuildNetwork();
  near(stats(laser).armor, 1 - 0.97 ** 20 * 0.98 ** 20);
  near(stats(laser).shield, 0.4);
  const hp = laser.hp;
  s.damageBuilding(laser, 100);
  near(hp - laser.hp, 100 * 0.97 ** 20 * 0.98 ** 20 * 0.6);
  source.energy = 0;
  laser.energy = 0;
  const emptyHp = laser.hp;
  s.damageBuilding(laser, 100);
  near(emptyHp - laser.hp, 100 * 0.97 ** 20 * 0.98 ** 20);
});

test("utility mastery improves relay reach/ports, miner yield, storage and repair reserves", () => {
  const s = lab(
    {},
    {
      relay: { link: 10, ports: 2 },
      miner: { yield: 4, speed: 4, range: 5 },
      battery: { capacity: 10 },
      repair: { repairRate: 10, range: 5, droneEnergy: 10 },
    },
  );
  const relay = stats(add(s, "relay")),
    miner = stats(add(s, "miner")),
    store = stats(add(s, "battery")),
    repair = stats(add(s, "repair"));
  near(relay.link, 117);
  assert.equal(relay.maxLinks, 8);
  near(miner.rate * miner.miningInterval, 4.8);
  near(miner.miningInterval, 2.5);
  near(miner.range, 40.25);
  near(store.capacity, 300);
  near(repair.rate, 30);
  near(repair.range, 230);
  near(repair.droneEnergy, 120);
});

test("live tower upgrades preserve damage percentage, existing energy and paid costs", () => {
  const s = lab();
  const sun = add(s, "solar"),
    store = add(s, "battery", 60, 0),
    repair = add(s, "repair", 0, 60);
  sun.hp /= 2;
  store.energy = 160;
  s.drones = [{ homeId: repair.id, energy: 80 }];
  s.setResearchLoadout(
    [],
    {},
    {
      solar: { hull: 20 },
      battery: { capacity: 20 },
      repair: { droneEnergy: 20 },
    },
  );
  near(sun.hp / sun.maxHp, 0.5);
  assert.equal(store.energy, 160);
  assert.equal(s.drones[0].energy, 80);
  assert.equal(store.baseCost, 300);
  const saved = new Simulation(s.mission, "normal", s.snapshot());
  assert.deepEqual(saved.towerRanks, s.towerRanks);
  assert.deepEqual(saved.statRanks, s.statRanks);
  assert.equal(saved.buildings.find((b) => b.id === store.id).energy, 160);
});

test("live local relay upgrades rebuild new links without bypassing obstruction", () => {
  const s = lab();
  add(s, "solar", -60, 0);
  const relay = add(s, "relay", 0, 0);
  const far = add(s, "battery", 100, 0);
  s.rebuildNetwork();
  assert.equal(s.degree(far.id), 0);
  s.setResearchLoadout([], {}, { relay: { link: 20 }, battery: { link: 20 } });
  assert.ok(s.links.some((l) => l.a === relay.id && l.b === far.id));
  s.asteroids = [{ id: 999, x: 50, y: 0, radius: 15, ore: 100, maxOre: 100 }];
  s.rebuildNetwork();
  assert.equal(s.degree(far.id), 0);
});

test("Classic ignores Clock, discounts and every tower specialization", () => {
  const s = new Simulation(
    CLASSIC[0],
    "normal",
    null,
    [],
    { economy: 20, fabrication: 20 },
    { solar: { output: 20, hull: 20 } },
  );
  assert.equal(s.buildingCost("solar"), 200);
  near(stats(s.buildings[0]).generationInterval, 0.55);
  assert.equal(s.buildings[0].maxHp, 600);
  assert.deepEqual(s.towerRanks, {});
});

test("progression UI exposes Clock, discounts and nine independently selectable tower classes", () => {
  const p = freshProgress();
  p.experience.xp = 1000;
  const base = researchView(p, "solar_cells", () => "", { page: "stats" });
  assert.match(base, /Improve Clock speed · 1 point/);
  assert.match(base, /Improve Efficient fabrication · 1 point/);
  const tower = researchView(p, "solar_cells", () => "", {
    page: "towers",
    tower: "laser",
  });
  assert.match(tower, /Tower mastery/);
  assert.match(tower, /Improve Fire rate · 1 point/);
  assert.match(tower, /Improve Powered shields · 1 point/);
  assert.equal((tower.match(/data-tower-select=/g) || []).length, 9);
});

test("missile firing mastery launches more salvos and still charges five minerals per missile", () => {
  const run = (towers) => {
    const s = lab({}, towers);
    s.diff = { ...s.diff, damage: 0 };
    add(s, "solar", 0, 0, 5);
    add(s, "battery", 0, 60, 4);
    add(s, "missile", 60, 0, 3);
    s.rebuildNetwork();
    const e = s.spawnEnemy("fighter", 0);
    e.x = 350;
    e.y = 0;
    e.hp = e.maxHp = 100000;
    const minerals = s.minerals;
    let shots = 0;
    for (let i = 0; i < 800; i++) {
      s.update(0.025);
      shots += s.events
        .splice(0)
        .filter(
          (event) => event.type === "shot" && event.weapon === "missile",
        ).length;
    }
    assert.equal(minerals - s.minerals, shots * 5);
    return shots;
  };
  assert.ok(run({ missile: { fireRate: 20 } }) > run({}));
});

test("repair mastery improves actual drone healing and reserves without reducing energy per hull", () => {
  const s = lab({}, { repair: { repairRate: 10, droneEnergy: 10 } });
  const target = add(s, "solar", 0, 0, 5),
    home = add(s, "repair", 60, 0);
  s.rebuildNetwork();
  s.damageBuilding(target, 100);
  s.drones = [
    {
      id: 999,
      homeId: home.id,
      targetId: target.id,
      x: 0,
      y: 0,
      hp: 60,
      energy: 120,
      returning: false,
      launchCooldown: 0,
    },
  ];
  const before = target.hp;
  tick(s, 1);
  near(target.hp - before, 30);
  near(s.drones[0].energy, 90);
});
