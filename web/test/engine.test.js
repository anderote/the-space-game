import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, rng, stats, distance } from "../src/engine.js";
import {
  BUILDINGS,
  BUILD_ORDER,
  CAMPAIGN,
  CLASSIC,
  CHALLENGES,
  skirmish,
} from "../src/content.js";
import {
  freshProgress,
  loadProgress,
  saveProgress,
  recordVictory,
  isUnlocked,
  starsTotal,
} from "../src/storage.js";
const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
function empty() {
  const m = {
    ...skirmish(21, "sandbox"),
    sandbox: false,
    waves: 0,
    kind: "test",
  };
  const s = new Simulation(m);
  s.buildings = [];
  s.links = [];
  s.asteroids = [];
  s.minerals = 100000;
  s.networkDirty = true;
  return s;
}
const add = (s, t, x, y, level = 1) => {
  const b = s.addBuilding(t, x, y, true);
  b.level = level;
  b.hp = b.maxHp = stats(b).hp;
  return b;
};
test("original build palette and prices", () => {
  assert.deepEqual(BUILD_ORDER, [
    "relay",
    "miner",
    "solar",
    "battery",
    "repair",
    "laser",
    "missile",
  ]);
  assert.deepEqual(
    BUILD_ORDER.map((t) => BUILDINGS[t].cost),
    [20, 45, 200, 300, 300, 100, 400],
  );
});
test("seeded generator restores exact random state", () => {
  const a = rng(29);
  a();
  a();
  const state = a.state(),
    expected = a();
  const b = rng(1);
  b.restore(state);
  assert.equal(b(), expected);
});
test("fields are reproducible", () => {
  const a = new Simulation(CAMPAIGN[0]),
    b = new Simulation(CAMPAIGN[0]);
  assert.deepEqual(a.asteroids, b.asteroids);
});
test("all structure links are shorter than original 90-unit bound", () => {
  const s = empty(),
    solar = add(s, "solar", 0, 0);
  s.rebuildNetwork();
  assert.equal(s.placement("relay", 90, 0).powered, false);
  assert.equal(s.placement("relay", 85, 0).powered, true);
  assert.equal(s.degree(solar.id), 0);
});
test("asteroids obstruct power connections", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  s.asteroids = [{ id: 80, x: 40, y: 0, radius: 10, ore: 100 }];
  s.rebuildNetwork();
  assert.equal(s.placement("relay", 80, 0).powered, false);
});
test("a laser is a dead end, not a relay", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  add(s, "laser", 70, 0);
  s.rebuildNetwork();
  assert.equal(s.placement("laser", 140, 0).powered, false);
});
test("energy store can extend the backbone", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  add(s, "battery", 70, 0);
  s.rebuildNetwork();
  assert.equal(s.placement("laser", 140, 0).powered, true);
});
test("existing relay never exceeds six links", () => {
  const s = empty();
  const relay = add(s, "relay", 0, 0);
  for (let i = 0; i < 9; i++) {
    const a = (i * Math.PI * 2) / 9;
    add(s, "laser", Math.cos(a) * 65, Math.sin(a) * 65);
  }
  s.rebuildNetwork();
  assert.equal(s.degree(relay.id), 6);
});
test("new construction cannot overlap an existing link", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  add(s, "relay", 80, 0);
  s.rebuildNetwork();
  assert.equal(s.placement("relay", 40, 0).ok, false);
});
test("energy is isolated by network components", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const a = add(s, "laser", 65, 0),
    b = add(s, "laser", 400, 0);
  b.energy = 0;
  s.rebuildNetwork();
  tick(s, 1);
  assert.equal(a.powered, true);
  assert.equal(b.powered, false);
});
test("destroyed backbone breaks branch power", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const relay = add(s, "relay", 75, 0),
    laser = add(s, "laser", 150, 0);
  s.rebuildNetwork();
  tick(s, 1);
  assert.equal(laser.powered, true);
  s.recycle(relay.id);
  laser.energy = 0;
  tick(s, 1);
  assert.equal(laser.powered, false);
});
test("storage adds capacity, not generation", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  s.rebuildNetwork();
  tick(s, 0.1);
  const generation = s.generation;
  add(s, "battery", 60, 0);
  tick(s, 0.1);
  assert.equal(s.generation, generation);
  assert.equal(s.capacity, 204);
});
test("paused world permits purchases without advancing construction", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  s.rebuildNetwork();
  s.paused = true;
  const { ok, building } = s.build("laser", 60, 0);
  assert.equal(ok, true);
  tick(s, 3);
  assert.equal(building.construction, 0);
  assert.equal(s.time, 0);
  s.paused = false;
  tick(s, 10);
  assert.equal(building.construction, 1);
});
test("finite mining cannot overdraw ore and credits extraction separately from spending", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  add(s, "miner", 45, 0);
  s.asteroids = [{ id: 900, x: 80, y: 0, radius: 12, ore: 7, maxOre: 7 }];
  s.rebuildNetwork();
  const cash = s.minerals;
  tick(s, 15);
  assert.equal(s.asteroids[0].ore, 0);
  assert.ok(Math.abs(s.mined - 7) < 1e-8);
  assert.ok(Math.abs(s.minerals - cash - 7) < 1e-6);
});
test("miners toggle stops extraction", () => {
  const s = new Simulation(CAMPAIGN[1]);
  s.minersOn = false;
  tick(s, 10);
  assert.equal(s.mined, 0);
  s.minersOn = true;
  tick(s, 5);
  assert.ok(s.mined > 0);
});
test("upgrade and recycle original refund math", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const b = add(s, "laser", 60, 0);
  s.rebuildNetwork();
  assert.equal(s.upgrade(b.id).ok, true);
  b.hp = b.maxHp * 0.5;
  assert.equal(s.recycle(b.id).refund, 75);
});
test("THEL retains original branch prices and adds a fourth tier", () => {
  const s = empty();
  s.mission.thel = true;
  const b = add(s, "laser", 0, 0);
  assert.equal(s.upgradeCost(b, "thel"), 500);
  assert.equal(s.upgrade(b.id, "thel").ok, true);
  assert.equal(b.type, "thel");
  assert.equal(s.upgradeCost(b), 800);
  b.construction = 1;
  s.upgrade(b.id);
  assert.equal(s.upgradeCost(b), 1000);
  b.construction = 1;
  s.upgrade(b.id);
  assert.equal(s.upgradeCost(b), 1400);
  b.construction = 1;
  s.upgrade(b.id);
  assert.equal(s.upgradeCost(b), Infinity);
});
test("pulser has three upgrades and preserves the branch", () => {
  const s = empty(),
    b = add(s, "laser", 0, 0);
  for (let i = 0; i < 3; i++) {
    b.construction = 1;
    assert.equal(s.upgrade(b.id, i === 0 ? "pulser" : null).ok, true);
  }
  assert.equal(b.level, 4);
  assert.equal(stats(b).range, 130);
  assert.equal(s.upgrade(b.id).ok, false);
  assert.equal(s.upgrade(b.id, "thel").ok, false);
});
test("missile level three spends minerals for four projectiles", () => {
  const s = empty();
  add(s, "solar", 0, 0, 3);
  const missile = add(s, "missile", 60, 0, 3);
  const battery = add(s, "battery", 0, 60, 2);
  battery.energy = 400;
  s.rebuildNetwork();
  const enemy = s.spawnEnemy("mothership");
  enemy.x = 300;
  enemy.y = 0;
  const before = s.minerals;
  s.update(0.025);
  assert.equal(s.projectiles.filter((p) => p.friendly).length, 1);
  assert.equal(before - s.minerals, 5);
  tick(s, 2.4);
  assert.equal(missile.salvoRemaining, 0);
  assert.equal(before - s.minerals, 20);
  assert.equal(stats(missile).salvo, 4);
});
test("laser intercepts hostile missiles", () => {
  const s = empty();
  add(s, "solar", 0, 0, 3);
  const l = add(s, "laser", 60, 0);
  s.rebuildNetwork();
  s.projectiles.push({
    id: 900,
    x: 100,
    y: 0,
    targetId: l.id,
    damage: 100,
    life: 5,
    speed: 100,
    friendly: false,
    interceptable: true,
  });
  s.update(0.025);
  assert.equal(s.projectiles.length, 0);
  assert.equal(l.hp, l.maxHp);
});
test("THEL ramps sustained damage and consumes energy", () => {
  const s = empty();
  s.mission.thel = true;
  add(s, "solar", 0, 0, 3);
  add(s, "solar", 0, 60, 3);
  const battery = add(s, "battery", -60, 0, 2);
  battery.energy = 600;
  const l = add(s, "thel", 60, 0);
  s.rebuildNetwork();
  const e = s.spawnEnemy("mothership");
  e.x = 150;
  e.y = 0;
  e.hp = e.maxHp = 100000;
  tick(s, 1);
  const first = 100000 - e.hp;
  tick(s, 1);
  const second = 100000 - e.hp - first;
  assert.ok(second > first);
  assert.ok(l.beamTime > 1);
});
test("repair drones heal with energy and no mineral charge", () => {
  const s = empty();
  add(s, "solar", 0, 0, 3);
  add(s, "solar", 0, 65, 3);
  add(s, "repair", 60, 0);
  const b = add(s, "laser", 110, 0);
  b.hp = 50;
  const battery = add(s, "battery", -60, 0, 2);
  battery.energy = 300;
  s.rebuildNetwork();
  const cash = s.minerals;
  tick(s, 25);
  assert.ok(s.drones.length > 0);
  assert.ok(b.hp > 50);
  assert.equal(s.minerals, cash);
});
test("classic mining goal is half initial field", () => {
  const s = new Simulation(CLASSIC[0]);
  assert.equal(
    s.mission.goal,
    s.asteroids.reduce((v, a) => v + a.maxOre, 0) / 2,
  );
  assert.equal(s.buildings.length, 1);
  assert.equal(s.minerals, 500);
  assert.equal(s.mission.unlocked.length, 7);
});
test("classic waves depend on extraction, not clock", () => {
  const s = new Simulation(CLASSIC[0]);
  tick(s, 60);
  assert.equal(s.wave, 0);
  s.mined = s.mission.goal * 0.2;
  s.update(0.025);
  assert.equal(s.wave, 1);
  tick(s, 0.1);
  assert.equal(s.enemies.length, 5);
  s.minerals = 0;
  assert.equal(s.mined, s.mission.goal * 0.2);
});
test("endless keeps progressing and spawns fifth-wave boss", () => {
  const s = new Simulation(skirmish(12));
  s.buildings.forEach((b) => (b.hp = 100000));
  for (let n = 0; n < 10; n++) {
    s.callWave();
    assert.equal(s.status, "playing");
  }
  assert.equal([...s.enemies, ...s.spawnQueue].filter((e) => e.type === "mothership").length, 6);
  assert.equal(s.wave, 10);
  const capital = s.spawnEnemy("mothership", 0);
  assert.ok(capital.hp > 800);
});
test("sandbox does not spawn automatic waves", () => {
  const s = new Simulation(skirmish(10, "sandbox"));
  tick(s, 120);
  assert.equal(s.wave, 0);
  s.callWave();
  assert.equal(s.wave, 1);
});
test("victory is awarded for actual extraction", () => {
  const s = new Simulation(CAMPAIGN[0]);
  s.minerals = 999999;
  s.update(0.025);
  assert.equal(s.status, "playing");
  s.mined = s.mission.goal;
  s.wave = s.mission.waves;
  s.time = s.mission.minDuration;
  s.enemies = [];
  s.update(0.025);
  assert.equal(s.status, "won");
});
test("mission-critical station loss defeats rescue operation", () => {
  const s = new Simulation(CAMPAIGN[4]);
  s.buildings.find((b) => b.type === "station").hp = 0;
  s.update(0.025);
  assert.equal(s.status, "lost");
});
test("snapshot resumes energy, damage, progression and random stream", () => {
  const s = new Simulation(CAMPAIGN[2]);
  tick(s, 12);
  const snapshot = s.snapshot(),
    clone = new Simulation(CAMPAIGN[2], "normal", snapshot);
  assert.equal(clone.time, s.time);
  assert.equal(clone.mined, s.mined);
  assert.deepEqual(clone.buildings, s.buildings);
  s.callWave();
  clone.callWave();
  assert.deepEqual(clone.enemies, s.enemies);
});
test("fresh and malformed saves recover; full and imported progress persist", () => {
  let saved = null;
  const store = {
    getItem: () => saved,
    setItem: (_, s) => {
      saved = s;
    },
  };
  assert.equal(loadProgress(store).version, 2);
  saved = "{bad";
  assert.deepEqual(loadProgress(store), freshProgress());
  const p = freshProgress();
  recordVictory(p, CAMPAIGN[0], { lost: 0, time: 60 });
  saveProgress(p, store);
  assert.equal(starsTotal(loadProgress(store)), 3);
  assert.equal(isUnlocked(p, 1), true);
  assert.equal(isUnlocked(p, 2), false);
});
test("replays preserve best medals and times", () => {
  const p = freshProgress();
  recordVictory(p, CAMPAIGN[0], { lost: 0, time: 60 });
  recordVictory(p, CAMPAIGN[0], { lost: 2, time: 500 });
  assert.equal(p.completed[0].stars, 3);
  assert.equal(p.completed[0].bestTime, 60);
  assert.equal(p.completed[0].wins, 2);
});
test("campaign and challenge fields provide accessible first mining sites", () => {
  for (const m of [...CAMPAIGN, ...CHALLENGES]) {
    const s = new Simulation(m);
    const nearby = s.asteroids.some((a) =>
      s.buildings.some(
        (b) =>
          ["relay", "solar"].includes(b.type) &&
          distance(a, b) < BUILDINGS.miner.range + a.radius + 90,
      ),
    );
    assert.ok(nearby, m.name);
    assert.ok(
      s.buildings.every((b) => b.hp > 0),
      m.name,
    );
  }
});
test("idle fully charged grid emits no fake transfer animations", () => {
  const s = empty();
  const b = add(s, "solar", 0, 0);
  b.energy = 4;
  add(s, "relay", 65, 0);
  s.rebuildNetwork();
  tick(s, 2);
  assert.equal(s.flows.length, 0);
});
test("consumer energy withdrawals trace real source-to-consumer paths", () => {
  const s = empty();
  const sun = add(s, "solar", 0, 0),
    relay = add(s, "relay", 70, 0),
    laser = add(s, "laser", 140, 0);
  laser.energy = 0;
  s.rebuildNetwork();
  assert.equal(s.useEnergy(laser, 0.7), true);
  assert.deepEqual(s.flows[0].path, [sun.id, relay.id, laser.id]);
  assert.equal(s.flows[0].consumer, laser.id);
  assert.ok(relay.powerPulse > 0);
  assert.ok(sun.energy < 4);
});
test("stores never charge from another store", () => {
  const s = empty();
  const a = add(s, "battery", 0, 0),
    b = add(s, "battery", 60, 0);
  a.energy = 100;
  b.energy = 0;
  s.rebuildNetwork();
  tick(s, 5);
  assert.equal(a.energy, 100);
  assert.equal(b.energy, 0);
});
test("pause freezes electrical transfers", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const laser = add(s, "laser", 60, 0);
  laser.energy = 0;
  s.rebuildNetwork();
  s.useEnergy(laser, 0.7);
  const before = JSON.stringify(s.flows);
  s.paused = true;
  tick(s, 2);
  assert.equal(JSON.stringify(s.flows), before);
});

test("unfinished relays block onward power until their construction completes", () => {
  const s = empty();
  const sun = add(s, "solar", 0, 0),
    relay = s.addBuilding("relay", 70, 0),
    laser = add(s, "laser", 140, 0);
  laser.energy = 0;
  s.rebuildNetwork();
  sun.energy = 4;
  assert.equal(s.requestEnergy(laser, 1), 0);
  relay.constructionUnits = 10;
  relay.construction = 1;
  assert.equal(s.requestEnergy(laser, 1), 1);
});
test("energy requests consume farthest-hop supply first and conserve partial receipts", () => {
  const s = empty();
  const near = add(s, "solar", 0, 0),
    relay = add(s, "relay", 70, 0),
    far = add(s, "battery", 140, 0),
    consumer = add(s, "laser", 0, 60);
  s.rebuildNetwork();
  near.energy = 2;
  far.energy = 0.4;
  assert.equal(s.requestEnergy(consumer, 1), 1);
  assert.equal(far.energy, 0);
  assert.ok(Math.abs(near.energy - 1.4) < 1e-9);
  assert.equal(s.flows[0].source, far.id);
});
test("solar upgrade keeps damage and stored energy, permits transit, but supplies nothing", () => {
  const s = empty();
  const other = add(s, "solar", 0, 0),
    sun = add(s, "solar", 70, 0),
    laser = add(s, "laser", 140, 0);
  sun.hp -= 70;
  sun.energy = 3;
  s.rebuildNetwork();
  assert.equal(s.upgrade(sun.id).ok, true);
  assert.equal(sun.maxHp - sun.hp, 70);
  assert.equal(sun.energy, 3);
  assert.equal(s.upgrade(sun.id).ok, false);
  assert.equal(s.requestEnergy(laser, 1), 1);
  assert.equal(sun.energy, 3);
  assert.ok(other.energy < 2.8);
});
test("isolated blueprints are accepted with a power warning", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  s.rebuildNetwork();
  const result = s.build("laser", 400, 0);
  assert.equal(result.ok, true);
  assert.match(result.warning, /No power/);
  tick(s, 5);
  assert.equal(result.building.construction, 0);
});
test("solar generation and store charging occur on distinct rhythms", () => {
  const s = empty();
  const sun = add(s, "solar", 0, 0),
    store = add(s, "battery", 60, 0);
  sun.energy = 0;
  store.energy = 0;
  s.rebuildNetwork();
  tick(s, 0.5);
  assert.equal(sun.energy, 0);
  tick(s, 0.05);
  assert.ok(Math.abs(sun.energy - 0.9) < 1e-8);
  assert.equal(store.energy, 0);
  tick(s, 0.5);
  assert.equal(sun.energy, 0);
  assert.ok(Math.abs(store.energy - 0.9) < 1e-8);
});
test("display frame rate does not change simulated extraction or energy", () => {
  const a = new Simulation(CAMPAIGN[1]),
    b = new Simulation(CAMPAIGN[1]);
  for (let i = 0; i < 600; i++) a.update(1 / 60);
  for (let i = 0; i < 240; i++) b.update(1 / 24);
  assert.equal(a.mined, b.mined);
  assert.equal(a.time, b.time);
  assert.deepEqual(a.buildings, b.buildings);
});
test("ring resistance applies only to a direct missile impact and its entire blast", () => {
  function hit(directRing) {
    const s = empty();
    add(s, "solar", -400, 0);
    const direct = s.spawnEnemy(directRing ? "ring" : "fighter"),
      near = s.spawnEnemy(directRing ? "fighter" : "ring");
    direct.x = 0;
    direct.y = 0;
    near.x = 20;
    near.y = 0;
    direct.hp = near.hp = 1000;
    s.projectiles.push({
      id: 900,
      x: 0,
      y: 0,
      targetId: direct.id,
      damage: 450,
      splash: 40,
      speed: 160,
      life: 8,
      friendly: true,
    });
    s.update(0.025);
    return [1000 - direct.hp, 1000 - near.hp];
  }
  const normal = hit(false),
    ring = hit(true);
  assert.equal(normal[0], 450);
  assert.ok(normal[1] > 200);
  assert.equal(ring[0], 30);
  assert.ok(ring[1] > 14 && ring[1] < 16);
});
test("mothership creates exactly five owned escorts and they die with it", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const mother = s.spawnEnemy("mothership");
  mother.x = 2000;
  s.update(0.025);
  assert.equal(s.enemies.filter((e) => e.parentId === mother.id).length, 5);
  tick(s, 12);
  assert.equal(s.enemies.filter((e) => e.parentId === mother.id).length, 5);
  mother.hp = 0;
  s.update(0.025);
  assert.equal(s.enemies.length, 0);
  assert.equal(s.bossKills, 1);
});
test("self destructor waits for its fuse and centers splash on its target", () => {
  const s = empty();
  const primary = add(s, "solar", 0, 0),
    adjacent = add(s, "battery", 80, 0);
  const e = s.spawnEnemy("suicide");
  e.x = -60;
  e.y = 0;
  tick(s, 2.9);
  assert.equal(primary.hp, 600);
  tick(s, 0.2);
  assert.equal(primary.hp, 573);
  assert.ok(Math.abs(adjacent.hp - 494.6) < 1e-7);
});
test("destroyed missiles cannot hit during the projectile update that follows interception", () => {
  const s = empty();
  add(s, "solar", 0, 0);
  const laser = add(s, "laser", 60, 0);
  s.rebuildNetwork();
  s.projectiles.push({
    id: 900,
    x: 62,
    y: 0,
    targetId: laser.id,
    damage: 100,
    hp: 20,
    life: 5,
    speed: 100,
    friendly: false,
    interceptable: true,
  });
  s.update(0.025);
  assert.equal(laser.hp, laser.maxHp);
  assert.equal(s.projectiles.length, 0);
});
test("pulser interception damages missile HP across successive firing ticks", () => {
  const s = empty();
  add(s, "solar", 0, 0, 3);
  const laser = add(s, "laser", 60, 0, 2);
  s.rebuildNetwork();
  const p = {
    id: 900,
    x: 100,
    y: 0,
    targetId: laser.id,
    damage: 100,
    hp: 20,
    life: 5,
    speed: 1,
    friendly: false,
    interceptable: true,
  };
  s.projectiles.push(p);
  s.update(0.025);
  assert.equal(p.hp, 8);
  tick(s, 0.05);
  assert.equal(s.projectiles.length, 0);
});
test("THEL waits after losing its locked target", () => {
  const s = empty();
  add(s, "solar", 0, 0, 3);
  const l = add(s, "thel", 60, 0);
  s.rebuildNetwork();
  const a = s.spawnEnemy("fighter");
  a.x = 120;
  a.y = 0;
  a.hp = 1000;
  tick(s, 0.1);
  const b = s.spawnEnemy("fighter");
  b.x = 125;
  b.y = 0;
  b.hp = 1000;
  a.hp = 0;
  tick(s, 0.5);
  assert.equal(b.hp, 1000);
  assert.ok(l.acquireCooldown > 0);
  tick(s, 0.75);
  assert.ok(b.hp < 1000);
});
test("repair drones heal their home and begin with a damaged hull", () => {
  const s = empty();
  const sun = add(s, "solar", 0, 0, 3),
    home = add(s, "repair", 60, 0),
    battery = add(s, "battery", 0, 65, 2);
  battery.energy = 500;
  home.hp = 200;
  s.rebuildNetwork();
  home.energy = 0;
  home.droneCharge = 9;
  home.droneCooldown = 0;
  s.update(0.025);
  assert.equal(s.drones.length, 1);
  assert.ok(s.drones[0].hp < 60);
  assert.equal(s.drones[0].mode, "dock");
  tick(s, 25);
  assert.ok(home.hp > 200);
});
test("classic survival schedules preserve recovered timings and skipped minute indices", () => {
  assert.equal(CLASSIC[2].scheduledWaves.length, 9);
  assert.deepEqual(CLASSIC[2].scheduledWaves[0], [70, 1, 10, 10, 0, 0]);
  assert.equal(CLASSIC[8].scheduledWaves.length, 17);
  assert.equal(CLASSIC[8].scheduledWaves[6][0], 490);
  assert.equal(CLASSIC[8].scheduledWaves.at(-1)[0], 1150);
});

test("every named scenario has a finite reproducible field seed", () => {
  for (const m of [...CAMPAIGN, ...CHALLENGES, ...CLASSIC, skirmish(4281)])
    assert.ok(Number.isFinite(m.seed), m.name);
  assert.equal(new Set(CHALLENGES.map((m) => m.seed)).size, CHALLENGES.length);
});
