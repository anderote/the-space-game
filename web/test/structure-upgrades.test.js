import test from "node:test";
import assert from "node:assert/strict";
import {
  Simulation,
  stats,
  placementRadius,
  linkClearance,
} from "../src/engine.js";
import {
  BUILDINGS,
  BUILD_ORDER,
  CAMPAIGN,
  CLASSIC,
  skirmish,
} from "../src/content.js";
import { SpaceRenderer } from "../src/renderer.js";
import { collectPowerSegments } from "../src/power-effects.js";
import * as THREE from "three";

const tick = (s, seconds) => {
  for (let i = 0; i < seconds * 40; i++) s.update(0.025);
};
function lab() {
  const s = new Simulation(skirmish(518, "sandbox"));
  s.buildings = [];
  s.links = [];
  s.asteroids = [];
  s.minerals = 100000;
  s.networkDirty = true;
  return s;
}
function add(s, type, x, y, level = 1) {
  const b = s.addBuilding(type, x, y, true);
  b.level = level;
  b.hp = b.maxHp = stats(b).hp;
  b.energy = stats(b).capacity || 0;
  return b;
}
for (const type of [...BUILD_ORDER, "thel"]) {
  test(`${type}: every upgrade completes, survives a save, and stops at its cap`, () => {
    const s = lab();
    add(s, "solar", 0, 0, 5);
    const b = add(s, type, 60, 0);
    s.rebuildNetwork();
    const cap = BUILDINGS[type].levels;
    assert.ok(cap >= 4);
    for (let level = 2; level <= cap; level++) {
      const cost = s.upgradeCost(b);
      const before = s.minerals;
      assert.ok(Number.isFinite(cost) && cost > 0);
      assert.equal(s.upgrade(b.id).ok, true);
      assert.equal(s.minerals, before - cost);
      assert.equal(b.level, level);
      assert.ok(b.construction < 1);
      tick(s, 25);
      assert.equal(b.construction, 1, `level ${level} must finish`);
      assert.ok(Number.isFinite(b.buildCooldown));
      assert.equal(b.maxHp, stats(b).hp);
    }
    const saved = new Simulation(s.mission, "normal", s.snapshot());
    const restored = saved.buildings.find((n) => n.id === b.id);
    assert.equal(restored.level, cap);
    assert.equal(restored.construction, 1);
    const before = saved.minerals;
    assert.equal(saved.upgrade(b.id).ok, false);
    assert.equal(saved.minerals, before);
  });
}

test("all four miner tiers extract their advertised yield and consume energy", () => {
  for (const [index, yieldPerCycle] of [4, 10, 16, 24].entries()) {
    const s = lab();
    const solar = add(s, "solar", 0, 0, 5);
    const miner = add(s, "miner", 60, 0, index + 1);
    s.asteroids = [
      { id: 9999, x: 95, y: 0, radius: 10, ore: 100, maxOre: 100 },
    ];
    s.rebuildNetwork();
    const reserve = miner.energy;
    tick(s, 0.025);
    assert.equal(s.mined, yieldPerCycle);
    assert.equal(s.asteroids[0].ore, 100 - yieldPerCycle);
    assert.equal(reserve - miner.energy, [1, 1, 1.5, 2][index]);
    assert.ok(solar.energy >= 0);
    s.setResearchLoadout(["precision_drills"]);
    // A fresh cycle applies the live research multiplier once, at every tier.
    miner.mineCooldown = 0;
    tick(s, 0.025);
    assert.equal(s.mined, yieldPerCycle * 2.25);
  }
});

test("late repair tiers improve real drone healing without creating free energy", () => {
  for (const [level, rate] of [
    [1, 20],
    [2, 20],
    [3, 25],
    [4, 30],
  ]) {
    const s = lab();
    add(s, "solar", 0, 0, 5);
    const home = add(s, "repair", 60, 0, level);
    const target = add(s, "laser", 60, 40);
    target.hp -= 100;
    s.drones = [
      {
        id: 999,
        homeId: home.id,
        targetId: target.id,
        x: 60,
        y: 35,
        hp: 60,
        energy: 80,
        launchCooldown: 0,
        returning: false,
      },
    ];
    s.rebuildNetwork();
    const before = target.hp;
    tick(s, 1);
    assert.ok(Math.abs(target.hp - before - rate) < 1e-6);
    assert.ok(Math.abs(s.drones[0].energy - (80 - rate)) < 1e-6);
  }
});

test("relay upgrades reconnect additional ports up to twelve", () => {
  const s = lab();
  const relay = add(s, "relay", 0, 0);
  for (let i = 0; i < 12; i++) {
    const a = (i * Math.PI) / 6;
    add(s, "laser", Math.cos(a) * 70, Math.sin(a) * 70);
  }
  s.rebuildNetwork();
  assert.equal(s.degree(relay.id), 6);
  for (const expected of [8, 10, 12]) {
    assert.equal(s.upgrade(relay.id).ok, true);
    // This isolated fixture tests topology; construction completion is tested above.
    relay.construction = 1;
    relay.constructionUnits = relay.constructionTarget;
    s.rebuildNetwork();
    assert.equal(s.degree(relay.id), expected);
  }
});

test("placement permits decorative overlap, while hulls and cable cores stay protected", () => {
  const s = lab();
  const solar = add(s, "solar", 0, 0);
  s.rebuildNetwork();
  const edge = placementRadius("solar") + placementRadius("relay");
  assert.equal(s.placement("relay", edge - 0.1, 0).ok, false);
  assert.equal(s.placement("relay", edge + 0.1, 0).ok, true);
  const relay = add(s, "relay", 80, 0);
  s.rebuildNetwork();
  const clearance = linkClearance("relay");
  assert.equal(s.placement("relay", 40, clearance - 0.1).ok, false);
  const placed = s.build("relay", 40, clearance + 0.1);
  assert.equal(placed.ok, true);
  assert.ok(s.links.some((l) => l.a === solar.id && l.b === relay.id));
});

test("asteroid rim placement follows the visible depleted rock", () => {
  const s = lab();
  const a = { id: 99, x: 100, y: 0, radius: 20, ore: 100, maxOre: 100 };
  s.asteroids = [a];
  s.rebuildNetwork();
  const rim = a.x + a.radius * 0.88 + placementRadius("miner");
  assert.equal(s.placement("miner", rim - 0.1, 0).ok, false);
  assert.equal(s.placement("miner", rim + 0.1, 0).ok, true);
  a.ore = 10;
  assert.equal(s.placement("miner", rim - 2, 0).ok, true);
  assert.equal(s.placement("miner", 100, 0).ok, false);
});

test("new fields contain twice the previous ore, with no refill when restoring a save", () => {
  const s = new Simulation(CAMPAIGN[0]);
  assert.deepEqual(
    s.asteroids.slice(0, 3).map((a) => a.ore),
    [3300, 4200, 5700],
  );
  for (const a of s.asteroids.slice(3))
    assert.equal(a.ore, Math.round(500 + a.radius * 37) * 3);
  const classic = new Simulation(CLASSIC[0]);
  for (const a of classic.asteroids)
    assert.equal(a.ore, Math.round(a.radius * 52) * 3);
  // Model an older, partially mined field, not just a new save.
  s.asteroids[0].maxOre = 1100;
  s.asteroids[0].ore = 42;
  const restored = new Simulation(s.mission, "normal", s.snapshot());
  assert.equal(restored.asteroids[0].ore, 42);
  assert.equal(restored.asteroids[0].maxOre, 1100);
});

test("cached supply routes observe depletion, recharge, source type and disconnects", () => {
  const s = lab();
  const solar = add(s, "solar", 0, 0);
  const battery = add(s, "battery", 60, 0);
  const laser = add(s, "laser", 120, 0);
  s.rebuildNetwork();
  solar.energy = 0;
  battery.energy = 2;
  assert.equal(s.requestEnergy(laser, 1, true), 0);
  assert.equal(s.requestEnergy(laser, 2), 2);
  assert.equal(s.requestEnergy(laser, 1), 0);
  solar.energy = 3;
  assert.equal(s.requestEnergy(laser, 2, true), 2);
  assert.equal(solar.energy, 1);
  s.recycle(battery.id);
  s.rebuildNetwork();
  assert.equal(s.requestEnergy(laser, 1), 0);
});

test("shared cables render one loaded arc per edge and expired transfers disappear", () => {
  const flows = [
    { path: [1, 2, 3], amount: 2, life: 0.2, maxLife: 0.28 },
    { path: [1, 2, 4], amount: 3, life: 0.1, maxLife: 0.28 },
    { path: [2, 1], amount: 1, life: 0.28, maxLife: 0.28 },
    { path: [1, 9], amount: 50, life: 0, maxLife: 0.28 },
  ];
  const arcs = collectPowerSegments(flows);
  assert.equal(arcs.length, 3);
  assert.deepEqual(arcs[0], {
    a: 2,
    b: 1,
    amount: 6,
    life: 0.28,
    maxLife: 0.28,
  });
  assert.deepEqual(collectPowerSegments([]), []);
});

function modelRenderer() {
  const renderer = Object.create(SpaceRenderer.prototype);
  renderer.materials = Object.fromEntries(
    ["dark", "hull", "edge", "solar"].map((k) => [
      k,
      new THREE.MeshStandardMaterial(),
    ]),
  );
  return renderer;
}
const modelSize = (model) =>
  new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());

test("solar models contain two through six textured petals without multiplying draw calls", () => {
  const renderer = modelRenderer();
  let onePetalVertices;
  for (let level = 1; level <= 5; level++) {
    const model = renderer.structure({ type: "solar", level, x: 0, y: 0 });
    const panels = model.children.filter(
      (o) => o.material === renderer.materials.solar,
    );
    assert.equal(panels.length, 1);
    const vertices = panels[0].geometry.attributes.position.count;
    onePetalVertices ??= vertices / 2;
    assert.equal(vertices, onePetalVertices * (level + 1));
    assert.equal(model.children.length, level === 1 ? 5 : 6);
    assert.equal(model.scale.x, 1);
    assert.ok(modelSize(model).x > 40);
    for (const mesh of model.children)
      for (const attribute of Object.values(mesh.geometry.attributes))
        assert.ok([...attribute.array].every(Number.isFinite));
  }
});

test("compact structures retain smaller scale and repair uses a low-profile four-port hub", () => {
  const renderer = modelRenderer();
  const repair = renderer.structure({ type: "repair", level: 1, x: 0, y: 0 });
  const relay = renderer.structure({ type: "relay", level: 1, x: 0, y: 0 });
  assert.equal(repair.scale.x, 0.65);
  assert.equal(relay.scale.x, 0.85);
  assert.equal(relay.children.length, 4);
  assert.equal(repair.children.length, 4);
  assert.ok(modelSize(repair).z < 6);
  const miner = renderer.structure({ type: "miner", level: 1, x: 0, y: 0 });
  assert.equal(miner.scale.x, 0.75);
  for (const type of [
    "fighter",
    "swarm",
    "ring",
    "bomber",
    "mothership",
    "suicide",
  ]) {
    const enemy = renderer.enemy({ type, x: 0, y: 0 });
    assert.equal(enemy.scale.x, 0.6);
    assert.ok(modelSize(enemy).length() > 0);
  }
});
