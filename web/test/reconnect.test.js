import test from "node:test";
import assert from "node:assert/strict";
import { Simulation, stats } from "../src/engine.js";
import { skirmish, CLASSIC } from "../src/content.js";
import { freshProgress, loadProgress, saveProgress } from "../src/storage.js";
import { buyResearch, researchRules } from "../src/research.js";
import { researchView } from "../src/research-view.js";
const lab = (on = false) => {
  const s = new Simulation(
    { ...skirmish(42, "sandbox"), waves: 0 },
    "normal",
    null,
    on ? ["adaptive_grid"] : [],
  );
  s.buildings = [];
  s.asteroids = [];
  s.links = [];
  s.networkDirty = true;
  return s;
};
const tick = (s, n) => {
  for (let i = 0; i < n * 40; i++) s.update(0.025);
};
function orphan(s) {
  const sun = s.addBuilding("solar", 0, 0, true),
    relay = s.addBuilding("relay", 60, 0, true),
    miner = s.addBuilding("miner", 60, 60, true);
  s.links = [
    { a: sun.id, b: relay.id },
    { a: relay.id, b: miner.id },
  ];
  for (const b of s.buildings) b.linkInitialized = true;
  s.rebuildNetwork();
  s.buildings = s.buildings.filter((b) => b !== relay);
  s.rebuildNetwork();
  return { sun, miner };
}
test("Adaptive grid reconnects an old endpoint after relay loss; default cables stay frozen", () => {
  const off = lab(),
    a = orphan(off);
  assert.equal(a.miner.connected, false);
  off.setResearchLoadout(["adaptive_grid"]);
  assert.equal(a.miner.connected, true);
  assert.ok(
    off.links.some(
      (e) => [e.a, e.b].includes(a.miner.id) && [e.a, e.b].includes(a.sun.id),
    ),
  );
  const on = lab(true),
    b = orphan(on);
  assert.equal(b.miner.connected, true);
});
test("automation reroutes a full orphan endpoint away from a powerless relay", () => {
  const s = lab(true),
    sun = s.addBuilding("solar", 0, 0, true),
    orphan = s.addBuilding("relay", 140, 60, true),
    miner = s.addBuilding("miner", 60, 60, true);
  s.links = [{ a: orphan.id, b: miner.id }];
  for (const b of s.buildings) b.linkInitialized = true;
  s.rebuildNetwork();
  assert.equal(miner.connected, true);
  assert.equal(s.degree(miner.id), 1);
  assert.ok(s.links.some((l) => l.a === sun.id && l.b === miner.id));
});
test("automation repairs a whole relay branch without tearing out its internal cables", () => {
  const s = lab(true),
    sun = s.addBuilding("solar", 0, 0, true),
    relay = s.addBuilding("relay", 80, 0, true),
    miner = s.addBuilding("miner", 150, 30, true);
  s.links = [{ a: relay.id, b: miner.id }];
  for (const b of s.buildings) b.linkInitialized = true;
  s.rebuildNetwork();
  assert.equal(relay.connected, true);
  assert.equal(miner.connected, true);
  assert.ok(s.links.some((l) => l.a === relay.id && l.b === miner.id));
  assert.ok(
    s.links.some(
      (l) => [l.a, l.b].includes(sun.id) && [l.a, l.b].includes(relay.id),
    ),
  );
});
test("blocked, distant and unfinished distributors do not gain illegal automatic links", () => {
  for (const kind of ["blocked", "distant", "unfinished"]) {
    const s = lab(true),
      sun = s.addBuilding("solar", 0, 0, true),
      b = s.addBuilding("miner", kind === "distant" ? 300 : 80, 0, true);
    for (const n of s.buildings) n.linkInitialized = true;
    if (kind === "blocked")
      s.asteroids = [
        { id: 999, x: 40, y: 0, radius: 20, ore: 100, maxOre: 100 },
      ];
    if (kind === "unfinished") sun.construction = 0.5;
    s.rebuildNetwork();
    assert.equal(s.degree(b.id), 0, kind);
    assert.equal(s.degree(sun.id), 0, kind);
  }
});
test("full powered distributors keep healthy links and do not sacrifice an existing endpoint", () => {
  const s = lab(true),
    sun = s.addBuilding("solar", 0, 0, true),
    relay = s.addBuilding("relay", 80, 0, true),
    count = stats(relay).maxLinks;
  s.links = [{ a: sun.id, b: relay.id }];
  const wired = [];
  for (let i = 0; i < count - 1; i++) {
    const a = -Math.PI / 2 + (Math.PI * i) / (count - 2),
      b = s.addBuilding("laser", 80 + Math.cos(a) * 70, Math.sin(a) * 70, true);
    wired.push(b);
    s.links.push({ a: relay.id, b: b.id });
  }
  const spare = s.addBuilding("miner", 130, 80, true);
  for (const b of s.buildings) b.linkInitialized = true;
  s.rebuildNetwork();
  assert.equal(s.degree(relay.id), count);
  assert.equal(s.degree(spare.id), 0);
  for (const b of wired) assert.equal(b.connected, true);
});

test("powerless batteries are not donors and two-second retries can recover when a route becomes clear", () => {
  const s = lab(true),
    battery = s.addBuilding("battery", 0, 0, true),
    b = s.addBuilding("miner", 70, 0, true);
  battery.energy = 0;
  for (const n of s.buildings) n.linkInitialized = true;
  s.rebuildNetwork();
  assert.equal(s.degree(b.id), 0);
  battery.energy = 50;
  s.networkDirty = true;
  s.rebuildNetwork();
  assert.equal(s.degree(b.id), 1);
  const x = lab(true),
    sun = x.addBuilding("solar", 0, 0, true),
    miner = x.addBuilding("miner", 80, 0, true);
  x.asteroids = [{ id: 999, x: 40, y: 0, radius: 20, ore: 100, maxOre: 100 }];
  for (const n of x.buildings) n.linkInitialized = true;
  x.rebuildNetwork();
  assert.equal(x.degree(miner.id), 0);
  x.asteroids = [];
  let rebuilds = 0;
  const original = x.rebuildNetwork.bind(x);
  x.rebuildNetwork = () => {
    rebuilds++;
    original();
  };
  tick(x, 2.1);
  assert.equal(miner.connected, true);
  assert.ok(rebuilds <= 2);
  assert.ok(x.links.some((l) => [l.a, l.b].includes(sun.id)));
});
test("research purchase, save/load and restored links retain automation; Classic disables it", () => {
  const p = freshProgress();
  p.intel.rare = 100;
  assert.equal(buyResearch(p, "adaptive_grid").ok, false);
  for (const id of ["solar_cells", "long_links", "adaptive_grid"])
    assert.equal(buyResearch(p, id).ok, true);
  let saved;
  const store = { getItem: () => saved, setItem: (_, v) => (saved = v) };
  saveProgress(p, store);
  const loaded = loadProgress(store);
  assert.equal(researchRules(loaded.research.active).autoReconnect, true);
  const s = lab(true);
  orphan(s);
  const copy = new Simulation(s.mission, "normal", s.snapshot());
  assert.deepEqual(copy.links, s.links);
  assert.equal(copy.rules.autoReconnect, true);
  const classic = new Simulation(CLASSIC[0], "normal", null, ["adaptive_grid"]);
  assert.equal(classic.rules.autoReconnect, false);
  assert.match(
    researchView(p, "adaptive_grid", () => ""),
    /NETWORK AUTOMATION/,
  );
  assert.match(
    researchView(p, "adaptive_grid", () => ""),
    /Adaptive grid/,
  );
});

test("stalled construction can reconnect but must still consume energy and finish its build increments", () => {
  const s = lab(true),
    sun = s.addBuilding("solar", 0, 0, true),
    b = s.addBuilding("miner", 70, 0, false);
  for (const n of s.buildings) n.linkInitialized = true;
  s.rebuildNetwork();
  assert.equal(s.degree(b.id), 1);
  assert.equal(b.construction, 0);
  tick(s, 1);
  assert.ok(b.construction > 0 && b.construction < 1);
  assert.ok(s.links.some((l) => [l.a, l.b].includes(sun.id)));
});
