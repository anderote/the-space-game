import test from "node:test";
import assert from "node:assert/strict";
import { Simulation } from "../src/engine.js";
import {
  CAMPAIGN,
  CHALLENGES,
  CLASSIC,
  BUILD_ORDER,
  ENEMIES,
  skirmish,
} from "../src/content.js";
const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
const lab = () => {
  const s = new Simulation({ ...skirmish(42, "sandbox"), waves: 0 });
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.addBuilding("solar", 0, 0, true);
  s.networkDirty = true;
  return s;
};
test("modern streams quintuple fleets, preserve rare rewards and wait to clear pending arrivals", () => {
  const s = new Simulation(CAMPAIGN[0]);
  s.wave = 2;
  s.callWave();
  s.nextWave = Infinity;
  const expected = s.mission.wavePlan[2].groups.reduce(
    (n, g) => n + g.count * 5,
    0,
  );
  assert.equal(s.enemies.length, 1);
  assert.equal(s.spawnQueue.length, expected - 1);
  assert.equal([...s.enemies, ...s.spawnQueue].filter((e) => e.rare).length, 1);
  const due = s.spawnQueue[0].at;
  s.enemies = [];
  tick(s, Math.max(0, due - 0.05));
  assert.equal(s.enemies.length, 0);
  assert.notEqual(s.clearedWave, 3);
  tick(s, 0.1);
  assert.ok(s.enemies.length > 0);
  assert.equal(s.status, "playing");
});
test("queued arrivals retain exact timing and random state across pause and save", () => {
  const s = lab();
  s.callWave();
  const copy = new Simulation(s.mission, "normal", s.snapshot());
  s.paused = true;
  const time = s.time;
  tick(s, 10);
  assert.equal(s.time, time);
  s.paused = false;
  tick(s, 4);
  tick(copy, 4);
  assert.deepEqual(copy.spawnQueue, s.spawnQueue);
  assert.deepEqual(copy.enemies, s.enemies);
  assert.ok(s.spawnQueue.length > 0);
  tick(s, 40);
  tick(copy, 40);
  assert.equal(s.spawnQueue.length, 0);
  assert.deepEqual(copy.enemies, s.enemies);
});
test("new modern hull is halved, difficulty and elite modifiers still apply; Classic hull stays original", () => {
  const modern = lab();
  assert.equal(modern.spawnEnemy("fighter", 0).hp, ENEMIES.fighter.hp * 0.5);
  assert.equal(
    modern.spawnEnemy("fighter", 0, true).hp,
    ENEMIES.fighter.hp * 0.5 * 1.6,
  );
  const classic = new Simulation(CLASSIC[0]);
  assert.equal(classic.spawnEnemy("fighter", 0).hp, ENEMIES.fighter.hp);
});
test("all modern missions and legacy resumed missions grant the full palette and THEL conversion", () => {
  for (const mission of [
    ...CAMPAIGN,
    ...CHALLENGES,
    skirmish(),
    skirmish(1, "sandbox"),
  ]) {
    assert.deepEqual(mission.unlocked, BUILD_ORDER);
    assert.equal(mission.thel, true);
  }
  const legacy = { ...CAMPAIGN[0], unlocked: ["solar"], thel: false };
  const s = new Simulation(legacy);
  const resumed = new Simulation(legacy, "normal", s.snapshot());
  assert.deepEqual(resumed.mission.unlocked, BUILD_ORDER);
  resumed.minerals = 10000;
  const laser = resumed.addBuilding("laser", 60, 0, true);
  assert.equal(resumed.upgrade(laser.id, "thel").ok, true);
  const classic = new Simulation(CLASSIC[0]);
  assert.deepEqual(classic.mission.unlocked, CLASSIC[0].unlocked);
});
test("friendly missiles repeatedly retarget from their own position without paying again", () => {
  const s = lab();
  const dead = s.spawnEnemy("fighter", 0);
  dead.hp = 0;
  const near = s.spawnEnemy("fighter", 0);
  near.x = 300;
  near.y = 200;
  const far = s.spawnEnemy("fighter", 0);
  far.x = 700;
  far.y = 400;
  const p = {
    id: 900,
    x: 100,
    y: 200,
    targetId: dead.id,
    damage: 20,
    splash: 20,
    speed: 160,
    life: 8,
    friendly: true,
    angle: 0,
  };
  s.projectiles.push(p);
  const minerals = s.minerals;
  tick(s, 0.025);
  assert.equal(p.targetId, near.id);
  near.hp = 0;
  tick(s, 0.025);
  assert.equal(p.targetId, far.id);
  assert.equal(s.minerals, minerals);
  far.hp = 0;
  tick(s, 0.1);
  assert.ok(s.projectiles.includes(p));
  const copy = new Simulation(s.mission, "normal", s.snapshot());
  const fresh = s.spawnEnemy("fighter", 0);
  fresh.x = p.x + 20;
  fresh.y = p.y;
  const other = copy.spawnEnemy("fighter", 0);
  other.x = fresh.x;
  other.y = fresh.y;
  tick(s, 0.2);
  tick(copy, 0.2);
  assert.equal(s.projectiles.length, 0);
  assert.ok(fresh.hp < fresh.maxHp);
  assert.equal(other.hp, fresh.hp);
});
test("searching missiles expire on fuel and hostile missiles do not seek new buildings", () => {
  const s = lab();
  s.projectiles.push({
    id: 900,
    x: 100,
    y: 100,
    targetId: 999,
    life: 0.2,
    speed: 160,
    friendly: true,
    angle: 0,
  });
  s.projectiles.push({
    id: 901,
    x: 100,
    y: 100,
    targetId: 999,
    life: 8,
    speed: 160,
    friendly: false,
    angle: 0,
  });
  tick(s, 0.025);
  assert.equal(s.projectiles.length, 1);
  tick(s, 0.2);
  assert.equal(s.projectiles.length, 0);
});
