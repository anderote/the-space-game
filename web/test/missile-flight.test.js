import test from "node:test";
import assert from "node:assert/strict";
import {
  advanceMissile,
  sweptHit,
  MISSILE_HULL,
  POINT_DEFENSE,
} from "../src/missile-flight.js";
import { Simulation } from "../src/engine.js";
import { skirmish, CLASSIC } from "../src/content.js";
const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
function lab(classic = false) {
  const s = new Simulation(
    classic
      ? { ...CLASSIC[0], waves: 0 }
      : { ...skirmish(42, "sandbox"), waves: 0 },
  );
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.nextWave = Infinity;
  s.addBuilding("solar", 0, 0, true);
  s.networkDirty = true;
  return s;
}
const missile = (targetId, extra = {}) => ({
  id: 900,
  x: 100,
  y: 200,
  targetId,
  damage: 20,
  splash: 20,
  speed: 160,
  life: 8,
  hp: MISSILE_HULL,
  friendly: true,
  angle: 0,
  ...extra,
});
test("missiles accelerate, obey turn limits and preserve velocity through steering", () => {
  const p = missile(0);
  advanceMissile(p, { x: -200, y: 200 }, 0.025);
  assert.ok(Math.abs(p.angle) <= 1.6 * 0.025 + 1e-9);
  assert.ok(p.vx > 0);
  assert.ok(p.x > 100);
  const speed = Math.hypot(p.vx, p.vy);
  assert.ok(Math.abs(speed - 62.5) < 1e-8);
  for (let i = 0; i < 200; i++) advanceMissile(p, { x: -200, y: 200 }, 0.025);
  assert.ok(Math.hypot(p.vx, p.vy) <= 160 + 1e-8);
  assert.ok(p.trail.length <= 8);
});
test("swept hull contact catches fast crossings and excludes near misses", () => {
  assert.equal(
    sweptHit({ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 50, y: 0 }, 5),
    true,
  );
  assert.equal(
    sweptHit({ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 50, y: 10 }, 5),
    false,
  );
});
test("a target behind an inertial missile can be missed; exhausted fuel cannot inflict a late hit", () => {
  const s = lab();
  const e = s.spawnEnemy("fighter", 0);
  e.x = 75;
  e.y = 200;
  const p = missile(e.id, { life: 0.2 });
  s.projectiles.push(p);
  const hp = e.hp;
  tick(s, 0.1);
  assert.ok(p.x > 100);
  assert.equal(e.hp, hp);
  tick(s, 0.15);
  assert.equal(s.projectiles.length, 0);
  assert.equal(e.hp, hp);
  const expired = missile(e.id, { x: e.x, y: e.y, life: 0.01 });
  s.projectiles.push(expired);
  tick(s, 0.025);
  assert.equal(e.hp, hp);
});
test("both point-defense classes shoot hostile-to-them missiles with range and cadence limits, granting no player XP", () => {
  for (const type of Object.keys(POINT_DEFENSE)) {
    const s = lab();
    const guard = s.spawnEnemy(type, 0);
    guard.x = 200;
    guard.y = 200;
    if (type === "mothership") guard.escortLaunched = true;
    const target = s.spawnEnemy("fighter", 0);
    target.x = 900;
    target.y = 200;
    const p = missile(target.id, { x: 220, y: 200, speed: 10 });
    s.projectiles.push(p);
    tick(s, 0.025);
    assert.equal(p.hp, 10);
    assert.ok(p.life > 0);
    const saved = new Simulation(s.mission, "normal", s.snapshot());
    tick(s, 0.1);
    tick(saved, 0.1);
    assert.equal(p.hp, 10);
    tick(s, POINT_DEFENSE[type].interval);
    tick(saved, POINT_DEFENSE[type].interval);
    assert.equal(s.projectiles.length, 0);
    assert.equal(saved.projectiles.length, 0);
    assert.equal(s.xpEarned, 0);
    assert.equal(s.masteryEarned, 0);
    assert.ok(s.effects.some((e) => e.type === "beam" || e.type === "hit"));
  }
});
test("point defense ignores distant and friendly-to-enemy projectiles and stays disabled in Classic", () => {
  for (const classic of [false, true]) {
    const s = lab(classic);
    const guard = s.spawnEnemy("ring", 0);
    guard.x = 200;
    guard.y = 200;
    const target = s.spawnEnemy("fighter", 0);
    target.x = 900;
    target.y = 200;
    const p = missile(target.id, { x: classic ? 220 : 500, y: 200, speed: 10 });
    s.projectiles.push(p);
    const hostile = {
      id: 901,
      x: 220,
      y: 200,
      targetId: s.buildings[0].id,
      speed: 10,
      life: 8,
      hp: 20,
      friendly: false,
      angle: 0,
    };
    s.projectiles.push(hostile);
    tick(s, 0.1);
    assert.equal(p.hp, 20);
    assert.equal(hostile.hp, 20);
  }
});
test("inertial missiles retain velocity, fuel, target and trail across save and resume", () => {
  const s = lab();
  const e = s.spawnEnemy("fighter", 0);
  e.x = 700;
  e.y = 500;
  s.projectiles.push(missile(e.id));
  tick(s, 0.5);
  const copy = new Simulation(s.mission, "normal", s.snapshot());
  tick(s, 0.5);
  tick(copy, 0.5);
  assert.deepEqual(copy.projectiles, s.projectiles);
  assert.deepEqual(copy.enemies, s.enemies);
});
