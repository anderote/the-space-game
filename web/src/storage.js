import {
  normalizeResearch,
  researchBudget,
  normalizeIntel,
  legacyIntel,
  earnsFieldIntel,
} from "./research.js";
import { normalizeExperience, experienceLevel } from "./experience.js";
const KEY = "the-space-game-v2";
export function freshProgress() {
  return {
    version: 2,
    progressionVersion: 2,
    research: { owned: [], active: [] },
    intel: { rare: 0, legacy: 0 },
    experience: { xp: 0, masteryXp: 0, ranks: {}, towers: {} },
    completed: {},
    challenges: {},
    livery: "mint",
    settings: {
      sound: true,
      quality: "high",
      reducedMotion: false,
      difficulty: "normal",
    },
    active: null,
  };
}
export function loadProgress(storage = globalThis.localStorage) {
  try {
    const p = JSON.parse(storage.getItem(KEY));
    if (!p || p.version !== 2) return freshProgress();
    return migrateProgression({
      ...freshProgress(),
      ...p,
      research: normalizeResearch(p.research, researchBudget(p).earned),
      completed: p.completed || {},
      challenges: p.challenges || {},
      settings: normalizeSettings(p.settings),
      progressionVersion: p.progressionVersion,
      intel: p.intel,
    });
  } catch {
    return freshProgress();
  }
}
export function migrateProgression(progress) {
  const legacy = progress.progressionVersion !== 2;
  const oldIntel = legacy ? legacyIntel(progress) : 0;
  const oldActivityXp = legacy
    ? Math.max(
        0,
        Number.isFinite(progress.intel?.mined) ? progress.intel.mined : 0,
      ) *
        0.2 +
      Math.max(
        0,
        Number.isFinite(progress.intel?.kills) ? progress.intel.kills : 0,
      ) *
        5
    : 0;
  return {
    ...progress,
    progressionVersion: 2,
    intel: legacy
      ? { rare: 0, legacy: oldIntel }
      : normalizeIntel(progress.intel),
    experience: normalizeExperience(
      legacy ? { xp: oldActivityXp } : progress.experience,
    ),
    research: normalizeResearch(
      progress.research,
      researchBudget(progress).earned,
    ),
  };
}
export function normalizeSettings(value = {}) {
  const defaults = freshProgress().settings;
  return {
    sound: typeof value?.sound === "boolean" ? value.sound : defaults.sound,
    reducedMotion:
      typeof value?.reducedMotion === "boolean"
        ? value.reducedMotion
        : defaults.reducedMotion,
    quality: ["high", "low"].includes(value?.quality)
      ? value.quality
      : defaults.quality,
    difficulty: ["relaxed", "normal", "hard", "extreme"].includes(
      value?.difficulty,
    )
      ? value.difficulty
      : defaults.difficulty,
  };
}
export function saveProgress(progress, storage = globalThis.localStorage) {
  try {
    storage.setItem(KEY, JSON.stringify(progress));
    return true;
  } catch {
    return false;
  }
}
export function resetProgress(progress, storage = globalThis.localStorage) {
  const backupKey = `${KEY}-backup-${Date.now()}`;
  // A durable local backup makes this reset recoverable even if a download fails.
  storage.setItem(backupKey, JSON.stringify(progress));
  const next = freshProgress();
  next.settings = normalizeSettings(progress.settings);
  next.resetToken = backupKey;
  if (!saveProgress(next, storage))
    throw new Error("Could not save fresh progress");
  return { progress: next, backupKey };
}
// Save the profile and snapshot together: a resumed operation must not credit
// the same mining or combat twice. Partial progress carries across operations.
export function bankIntel(progress, sim) {
  if (!earnsFieldIntel(sim.mission)) return 0;
  progress.intel = normalizeIntel(progress.intel);
  const credit = sim.intelCredit;
  const earned = Math.max(0, sim.intelCollected - credit.rare);
  progress.intel.rare += earned;
  credit.rare = Math.max(credit.rare, sim.intelCollected);
  credit.earned += earned;
  return earned;
}
export function bankExperience(progress, sim) {
  if (!earnsFieldIntel(sim.mission))
    return { xp: 0, levels: 0, mastery: 0, masteryLevels: 0 };
  progress.experience = normalizeExperience(progress.experience);
  const before = experienceLevel(progress.experience.xp);
  const masteryBefore = experienceLevel(progress.experience.masteryXp);
  const mastery = Math.max(
    0,
    (sim.masteryEarned || 0) - (sim.masteryCredit || 0),
  );
  progress.experience.masteryXp += mastery;
  sim.masteryCredit = Math.max(sim.masteryCredit || 0, sim.masteryEarned || 0);
  const xp = Math.max(0, sim.xpEarned - sim.xpCredit);
  progress.experience.xp += xp;
  sim.xpCredit = Math.max(sim.xpCredit, sim.xpEarned);
  return {
    xp,
    levels: experienceLevel(progress.experience.xp) - before,
    mastery,
    masteryLevels:
      experienceLevel(progress.experience.masteryXp) - masteryBefore,
  };
}
export function starsTotal(p) {
  return Object.values(p.completed).reduce((s, c) => s + (c.stars || 0), 0);
}
export function isUnlocked(p, index) {
  return index === 0 || Boolean(p.completed[index - 1]);
}
export function recordVictory(p, mission, stats) {
  const stars =
    1 + (stats.lost === 0 ? 1 : 0) + (stats.time <= mission.par ? 1 : 0);
  const collection =
    typeof mission.id === "number" ? p.completed : p.challenges;
  if (mission.id === "skirmish") return 0;
  const old = collection[mission.id];
  collection[mission.id] = {
    stars: Math.max(old?.stars || 0, stars),
    bestTime: Math.min(old?.bestTime || Infinity, stats.time),
    wins: (old?.wins || 0) + 1,
  };
  p.active = null;
  return stars;
}
