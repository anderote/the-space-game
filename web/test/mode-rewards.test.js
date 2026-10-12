import test from "node:test";
import assert from "node:assert/strict";
import { Simulation } from "../src/engine.js";
import { CHALLENGES, skirmish } from "../src/content.js";
import { freshProgress, bankIntel, bankExperience } from "../src/storage.js";
import { researchView } from "../src/research-view.js";
for (const mission of [
  skirmish(42, "endless"),
  skirmish(42, "sandbox"),
  ...CHALLENGES,
]) {
  test(`${mission.name} banks all three real activity rewards once across resume`, () => {
    const p = freshProgress(),
      s = new Simulation(mission);
    const enemy = s.spawnEnemy("mothership", 0);
    s.damageEnemy(enemy, 1e9);
    s.update(0.025);
    const target = s.buildings.find((b) => b.type === "solar");
    s.damageBuilding(target, 10);
    s.creditRepair(target, 10);
    assert.equal(bankIntel(p, s), 3);
    const reward = bankExperience(p, s);
    assert.ok(reward.xp > 0);
    assert.equal(reward.mastery, 22);
    const restored = new Simulation(mission, "normal", s.snapshot());
    assert.equal(bankIntel(p, restored), 0);
    assert.equal(bankExperience(p, restored).xp, 0);
    assert.equal(bankExperience(p, restored).mastery, 0);
    assert.doesNotMatch(
      researchView(p, "solar_cells", () => "", { mission, page: "towers" }),
      /no progression rewards|not earned/,
    );
  });
}
