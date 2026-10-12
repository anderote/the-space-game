import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { skirmish, CAMPAIGN } from "../src/content.js";
import { asteroidReadout, asteroidView } from "../src/asteroid-view.js";
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-6, `${a} != ${b}`);
function lab(level) {
  const s = new Simulation({ ...skirmish(99, "sandbox"), waves: 0 });
  s.buildings = [];
  s.links = [];
  s.asteroids = [];
  s.networkDirty = true;
  const sun = s.addBuilding("solar", 0, 0, true);
  sun.level = 5;
  sun.energy = stats(sun).capacity;
  const miner = s.addBuilding("miner", 60, 0, true);
  miner.level = level;
  for (let i = 0; i < 4; i++)
    s.asteroids.push({
      id: 900 + i,
      x: 85 + i,
      y: 3 * i,
      radius: 5,
      ore: 1000,
      maxOre: 1000,
    });
  s.rebuildNetwork();
  return { s, miner, sun };
}
test("each miner tier extracts simultaneously from 1/2/3/4 distinct asteroids and pays for every beam", () => {
  for (let level = 1; level <= 4; level++) {
    const { s, miner } = lab(level),
      before = s.buildings.reduce((n, b) => n + b.energy, 0),
      spec = stats(miner);
    s.update(0.025);
    assert.equal(miner.miningTargetIds.length, level);
    assert.equal(new Set(miner.miningTargetIds).size, level);
    assert.equal(s.asteroids.filter((a) => a.ore < 1000).length, level);
    near(s.mined, level * spec.rate * spec.miningInterval);
    near(
      before - s.buildings.reduce((n, b) => n + b.energy, 0),
      level * (spec.miningEnergy || 1),
    );
    near(s.xpEarned, s.mined * 0.4);
  }
});
test("limited power or available deposits reduce actual beam count without phantom mining", () => {
  const { s, miner, sun } = lab(4);
  sun.energy = 0;
  miner.energy = 2;
  s.update(0.025);
  assert.equal(miner.miningTargetIds.length, 1);
  near(s.mined, 24);
  const { s: one, miner: b } = lab(4);
  one.asteroids = one.asteroids.slice(0, 1);
  one.asteroids[0].ore = 7;
  one.update(0.025);
  near(one.mined, 7);
  assert.equal(b.miningTargetIds.length, 1);
  near(one.asteroids[0].ore, 0);
  assert.equal(one.networkDirty, true);
});
test("multi-beam target identities and remaining ore survive a saved operation without duplicate rewards", () => {
  const { s, miner } = lab(3);
  s.update(0.025);
  const copy = new Simulation(s.mission, "normal", s.snapshot()),
    b = copy.buildings.find((b) => b.id === miner.id);
  assert.deepEqual(b.miningTargetIds, miner.miningTargetIds);
  assert.deepEqual(copy.asteroids, s.asteroids);
  const mined = copy.mined;
  copy.update(0.025);
  near(copy.mined, mined);
});
test("asteroid inspection reports live depletion, miners in range and active beams, including exhausted deposits", () => {
  const { s, miner } = lab(2);
  s.update(0.025);
  const a = s.asteroids.find((a) => a.id === miner.miningTargetIds[0]);
  const data = asteroidReadout(a, s.buildings, stats);
  assert.equal(data.miners, 1);
  assert.equal(data.active, 1);
  assert.ok(data.remaining < 1000);
  near(data.initial, data.remaining + data.harvested);
  assert.match(asteroidView(a, data, String), /MINERALS REMAINING/);
  a.ore = 0;
  near(asteroidReadout(a, s.buildings, stats).percent, 0);
  assert.match(
    asteroidView(a, asteroidReadout(a, s.buildings, stats), String),
    /0 MINERALS REMAINING/,
  );
  const fresh = new Simulation(CAMPAIGN[0]);
  assert.equal(fresh.asteroids[0].maxOre, 3300);
});
