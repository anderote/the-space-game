import { performance } from "node:perf_hooks";
import { Simulation } from "../src/engine.js";
import { skirmish } from "../src/content.js";
import { SpaceRenderer } from "../src/renderer.js";
import * as THREE from "three";
import { collectPowerSegments } from "../src/power-effects.js";
const makeNetwork = () => {
  const s = new Simulation(skirmish(518, "sandbox"));
  s.buildings = [];
  s.links = [];
  s.asteroids = [];
  s.minerals = 100000;
  for (let y = 0; y < 10; y++)
    for (let x = 0; x < 12; x++)
      s.addBuilding(
        x === 0 ? "solar" : x === 11 ? "laser" : "relay",
        x * 60,
        y * 60,
        true,
      );
  s.rebuildNetwork();
  return s;
};
const trials = [];
for (let trial = 0; trial < 6; trial++) {
  const s = makeNetwork();
  const consumers = s.buildings.filter((b) => b.type === "laser");
  const start = performance.now();
  for (let i = 0; i < 1200; i++) {
    for (const b of s.buildings) if (b.type === "solar") b.energy = 4;
    for (const b of consumers) s.requestEnergy(b, 0.5);
    s.update(0.025);
  }
  if (trial) trials.push(performance.now() - start);
}
trials.sort((a, b) => a - b);
const renderer = Object.create(SpaceRenderer.prototype);
renderer.materials = Object.fromEntries(
  ["dark", "hull", "edge", "solar"].map((k) => [
    k,
    new THREE.MeshStandardMaterial(),
  ]),
);
const relay = renderer.structure({ type: "relay", level: 1, x: 0, y: 0 });
const meshCount = (model) => {
  let meshes = 0;
  model.traverse((o) => {
    if (o.isMesh) meshes++;
  });
  return meshes;
};
const solar = renderer.structure({ type: "solar", level: 5, x: 0, y: 0 });
// Ten consumers receive repeated transfers across a shared 20-edge backbone.
const flows = Array.from({ length: 80 }, (_, i) => ({
  path: [...Array.from({ length: 21 }, (_, j) => j + 1), 22 + (i % 10)],
  amount: 0.5,
  life: 0.28,
  maxLife: 0.28,
}));
console.log(
  JSON.stringify({
    networkStructures: 120,
    steps: 1200,
    requests: 12000,
    medianMs: +trials[2].toFixed(1),
    perStepMs: +(trials[2] / 1200).toFixed(3),
    relayMeshes: meshCount(relay),
    sixPetalSolarMeshes: meshCount(solar),
    powerArcsBeforeDeduplication: flows.reduce(
      (n, f) => n + f.path.length - 1,
      0,
    ),
    powerArcsAfterDeduplication: collectPowerSegments(flows).length,
  }),
);
