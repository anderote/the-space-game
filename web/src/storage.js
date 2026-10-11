import {
  normalizeResearch,
  researchBudget,
  normalizeIntel,
  intelActivity,
  earnsFieldIntel,
} from "./research.js";
const KEY = "the-space-game-v2";
export function freshProgress() {
  return {
    version: 2,
    research: { owned: [], active: [] },
    intel: { mined: 0, kills: 0 },
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
    return {
      ...freshProgress(),
      ...p,
      research: normalizeResearch(p.research, researchBudget(p).earned),
      intel: normalizeIntel(p.intel),
      completed: p.completed || {},
      challenges: p.challenges || {},
      settings: normalizeSettings(p.settings),
    };
  } catch {
    return freshProgress();
  }
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
// Save the profile and snapshot together: a resumed operation must not credit
// the same mining or combat twice. Partial progress carries across operations.
export function bankIntel(progress, sim) {
  if (!earnsFieldIntel(sim.mission)) return 0;
  const before = intelActivity(progress).earned;
  progress.intel = normalizeIntel(progress.intel);
  const credit = sim.intelCredit;
  progress.intel.mined += Math.max(0, sim.mined - credit.mined);
  progress.intel.kills += Math.max(0, sim.combatKills - credit.kills);
  credit.mined = Math.max(credit.mined, sim.mined);
  credit.kills = Math.max(credit.kills, sim.combatKills);
  const earned = intelActivity(progress).earned - before;
  credit.earned += earned;
  return earned;
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
