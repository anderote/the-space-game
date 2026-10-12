import test from "node:test";
import assert from "node:assert/strict";
import {
  BASE_STATS,
  buyBaseStat,
  buyTowerSkill,
  experienceBudget,
  masteryBudget,
  normalizeExperience,
} from "../src/experience.js";
import { TOWER_TYPES } from "../src/tower-skills.js";
import { Simulation, stats } from "../src/engine.js";
import { skirmish } from "../src/content.js";
import { freshProgress, bankExperience } from "../src/storage.js";
import { skillBonus } from "../src/progression-balance.js";
test("every global and tower skill reaches rank 50 and uses only its independent point pool", () => {
  assert.ok(BASE_STATS.every((s) => s.max === 50));
  assert.ok(TOWER_TYPES.every((t) => t.skills.every((s) => s.max === 50)));
  const p = freshProgress();
  p.experience.xp = 1e8;
  p.experience.masteryXp = 1e8;
  for (let i = 0; i < 50; i++) {
    assert.equal(buyBaseStat(p, "armor").ok, true);
    assert.equal(buyTowerSkill(p, "laser", "armor").ok, true);
  }
  assert.equal(buyBaseStat(p, "armor").ok, false);
  assert.equal(buyTowerSkill(p, "laser", "armor").ok, false);
  assert.equal(experienceBudget(p).spent, 50);
  assert.equal(masteryBudget(p).spent, 50);
  const saved = normalizeExperience(p.experience);
  assert.deepEqual(saved, p.experience);
});
test("stronger armor remains finite at maximum rank and UI reports actual compounded reduction", () => {
  const s = new Simulation(
      skirmish(1, "sandbox"),
      "normal",
      null,
      [],
      { armor: 50 },
      { laser: { armor: 50 } },
    ),
    b = s.buildings.find((b) => b.type === "laser");
  const reduction = stats(b).armor;
  assert.ok(reduction > 0.9 && reduction < 1);
  const hp = b.hp;
  s.damageBuilding(b, 100);
  assert.ok(b.hp < hp);
  assert.ok(hp - b.hp < 10);
  const a = BASE_STATS.find((s) => s.id === "armor");
  assert.equal(skillBonus(a, 1), 3);
  assert.equal(skillBonus(a, 50), 78);
  const local = TOWER_TYPES.find((t) => t.id === "laser").skills.find(
    (s) => s.id === "armor",
  );
  assert.equal(skillBonus(local, 50), 64);
});
test("new activity earns doubled command/mastery XP while banked history and credits remain unchanged", () => {
  const p = freshProgress();
  p.experience.xp = 250;
  p.experience.masteryXp = 100;
  const s = new Simulation({ ...skirmish(1, "sandbox"), waves: 0 });
  s.xpEarned = 20;
  s.xpCredit = 20;
  s.masteryEarned = 10;
  s.masteryCredit = 10;
  assert.equal(bankExperience(p, s).xp, 0);
  assert.equal(p.experience.xp, 250);
  const e = s.spawnEnemy("fighter", 0);
  s.damageEnemy(e, 1e9);
  const b = s.buildings[0];
  s.damageBuilding(b, 10);
  s.creditRepair(b, 10);
  const reward = bankExperience(p, s);
  assert.equal(reward.xp, 12);
  assert.equal(reward.mastery, 22);
  assert.equal(bankExperience(p, s).mastery, 0);
});
