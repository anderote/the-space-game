import test from "node:test";
import assert from "node:assert/strict";
import { CAMPAIGN, ENEMIES, skirmish } from "../src/content.js";
import { Simulation } from "../src/engine.js";
import { bearingLabel } from "../src/expedition.js";
const wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));
test("all twelve expeditions have longer objectives, varied nonempty waves and viable ore", () => {
  assert.equal(CAMPAIGN.length, 12);
  const fingerprints = new Set();
  for (const m of CAMPAIGN) {
    assert.ok(m.minDuration >= 210);
    assert.ok(m.par > m.minDuration);
    assert.equal(m.wavePlan.length, m.waves);
    assert.ok(m.waves >= 4);
    assert.equal(m.requireWaves, true);
    const types = new Set();
    for (const plan of m.wavePlan) {
      assert.ok(plan.gap >= 45);
      for (const g of plan.groups) {
        assert.ok(ENEMIES[g.type]);
        assert.ok(g.count > 0);
        types.add(g.type);
      }
    }
    assert.ok(types.size >= 2);
    fingerprints.add(JSON.stringify(m.wavePlan.map((p) => p.groups)));
    const s = new Simulation(m);
    if (m.kind === "mine")
      assert.ok(s.asteroids.reduce((sum, a) => sum + a.ore, 0) > m.goal);
    assert.equal(
      s.buildings.some((b) => b.type === "laser"),
      true,
    );
  }
  assert.equal(fingerprints.size, 12);
});
test("every authored wave spawns exactly its groups at the previewed bearings", () => {
  for (const m of CAMPAIGN) {
    const s = new Simulation(m);
    for (const plan of m.wavePlan) {
      s.enemies = [];
      const preview = s.nextWavePreview();
      assert.equal(preview.name, plan.name);
      s.callWave();
      assert.equal(
        s.enemies.length,
        plan.groups.reduce((n, g) => n + g.count, 0),
      );
      let index = 0;
      for (const g of plan.groups)
        for (let i = 0; i < g.count; i++) {
          const e = s.enemies[index++];
          assert.equal(e.type, g.type);
          assert.ok(
            Math.abs(wrap(Math.atan2(e.y, e.x) - plan.angle - g.offset)) <=
              0.151,
          );
        }
      assert.equal(s.nextWave, s.time + plan.gap);
    }
    const wave = s.wave;
    s.callWave();
    assert.equal(s.wave, wave);
    assert.equal(s.nextWavePreview(), null);
  }
});
test("early objectives cannot skip waves or hold time; all objective kinds can finish", () => {
  for (const m of CAMPAIGN) {
    const s = new Simulation(m);
    s.asteroids = [];
    s.mined = m.goal;
    s.bossKills = m.goal;
    const station = s.buildings.find((b) => b.type === "station");
    if (station) station.hp = station.maxHp;
    s.time = m.minDuration + 1;
    s.nextWave = Infinity;
    s.update(0.025);
    assert.equal(s.status, "playing", m.name);
    s.wave = m.waves;
    s.enemies = [s.spawnEnemy("fighter", 0)];
    s.update(0.025);
    assert.equal(s.status, "playing");
    s.enemies = [];
    s.spawnQueue = [];
    s.time = m.minDuration - 1;
    s.update(0.025);
    assert.equal(s.status, "playing");
    s.time = m.minDuration + 1;
    s.update(0.025);
    assert.equal(s.status, "won", m.name);
    assert.equal(s.objectiveProgress(), 1);
  }
});
test("automatic arrivals honor grace period and countdown freezes when paused and resumes from save", () => {
  const s = new Simulation(CAMPAIGN[0]);
  s.update(0.025);
  const p = s.nextWavePreview();
  assert.equal(p.number, 1);
  assert.ok(p.seconds > 64);
  s.paused = true;
  s.update(10);
  assert.deepEqual(s.nextWavePreview(), p);
  s.paused = false;
  const restored = new Simulation(s.mission, "normal", s.snapshot());
  assert.deepEqual(restored.nextWavePreview(), p);
  s.time = s.nextWave - 0.01;
  s.update(0.025);
  assert.equal(s.wave, 1);
  assert.ok(s.enemies.length > 0);
});
test("multi-front waves expose every direction, and endless/sandbox previews match real spawns", () => {
  const s = new Simulation(CAMPAIGN[1]);
  s.wave = 2;
  assert.equal(s.nextWavePreview().directions.length, 2);
  for (const mode of ["endless", "sandbox"]) {
    const x = new Simulation(skirmish(42, mode));
    const p = x.nextWavePreview();
    x.callWave();
    for (const e of x.enemies)
      assert.ok(Math.abs(wrap(Math.atan2(e.y, e.x) - p.angles[0])) <= 0.251);
    assert.equal(p.manual, mode === "sandbox");
  }
  assert.equal(bearingLabel(Math.PI / 2), "N");
  assert.equal(bearingLabel(-Math.PI / 2), "S");
});
test("capital objectives distribute the required motherships across separate late waves", () => {
  for (const m of CAMPAIGN.filter((m) => m.kind === "boss")) {
    const bossWaves = m.wavePlan
      .map((p, i) => ({
        i,
        count: p.groups
          .filter((g) => g.type === "mothership")
          .reduce((n, g) => n + g.count, 0),
      }))
      .filter((p) => p.count);
    assert.equal(
      bossWaves.reduce((n, p) => n + p.count, 0),
      m.goal,
    );
    assert.ok(bossWaves.length >= 2);
    assert.equal(bossWaves.at(-1).i, m.waves - 1);
  }
});
