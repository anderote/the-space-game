// Command experience is separate from the Intel technology economy.
import {
  normalizeTowerRanks,
  towerPoints,
  TOWER_BY_ID,
} from "./tower-skills.js";
export const XP_RATES = { mining: 0.2, combat: 0.05, repair: 0.1 };
export const BASE_STATS = [
  {
    id: "armor",
    name: "Armor",
    icon: "battery",
    effect: "2% less incoming hull damage",
    perRank: 2,
    unit: "% damage reduction",
    max: 20,
  },
  {
    id: "fabrication",
    name: "Clock speed",
    icon: "relay",
    effect: "+5% construction, mining and solar cycle speed",
    perRank: 5,
    unit: "% clock speed",
    max: 20,
  },
  {
    id: "harvest",
    name: "Harvesting",
    icon: "miner",
    effect: "+5% minerals per mining cycle",
    perRank: 5,
    unit: "% extraction",
    max: 20,
  },
  {
    id: "firepower",
    name: "Firepower",
    icon: "laser",
    effect: "+3% damage for all player weapons",
    perRank: 3,
    unit: "% weapon damage",
    max: 20,
  },
  {
    id: "repair",
    name: "Repair efficiency",
    icon: "repair",
    effect: "+5% drone repair throughput",
    perRank: 5,
    unit: "% repair speed",
    max: 20,
  },
  {
    id: "power",
    name: "Power output",
    icon: "solar",
    effect: "+5% solar generation",
    perRank: 5,
    unit: "% generation",
    max: 20,
  },
  {
    id: "economy",
    name: "Efficient fabrication",
    icon: "relay",
    effect: "1% cheaper buildings and upgrades",
    perRank: 1,
    unit: "% construction discount",
    max: 20,
  },
];
const safe = (n) => (Number.isFinite(n) ? Math.min(1e12, Math.max(0, n)) : 0);
export function normalizeRanks(value = {}, budget = Infinity) {
  const ranks = {};
  for (const stat of BASE_STATS) {
    const rank = Math.min(stat.max, Math.floor(safe(value?.[stat.id])), budget);
    if (rank) ranks[stat.id] = rank;
    budget -= rank;
  }
  return ranks;
}
export function experienceLevel(xp) {
  // First point at 100 XP, then 150, 200, 250... for each subsequent level.
  return 1 + Math.floor((Math.sqrt(5625 + 100 * safe(xp)) - 75) / 50);
}
const threshold = (level) => 25 * (level - 1) ** 2 + 75 * (level - 1);
export function normalizeExperience(value = {}) {
  const xp = safe(value?.xp);
  const ranks = normalizeRanks(value?.ranks, experienceLevel(xp) - 1);
  // Old mastery purchases retain their ranks, funded by a one-time migration.
  const legacyTowers = normalizeTowerRanks(
    value?.towers,
    experienceLevel(xp) - 1 - Object.values(ranks).reduce((a, b) => a + b, 0),
  );
  const masteryXp =
    value?.masteryXp === undefined
      ? threshold(towerPoints(legacyTowers) + 1)
      : safe(value.masteryXp);
  return {
    xp,
    ranks,
    masteryXp,
    towers: normalizeTowerRanks(value?.towers, experienceLevel(masteryXp) - 1),
  };
}
export function experienceBudget(progress) {
  const e = normalizeExperience(progress.experience);
  const level = experienceLevel(e.xp);
  const spent = Object.values(e.ranks).reduce((a, b) => a + b, 0);
  return {
    ...e,
    level,
    spent,
    available: level - 1 - spent,
    into: e.xp - threshold(level),
    needed: threshold(level + 1) - threshold(level),
  };
}
export function masteryBudget(progress) {
  const e = normalizeExperience(progress.experience),
    level = experienceLevel(e.masteryXp),
    spent = towerPoints(e.towers);
  return {
    ...e,
    xp: e.masteryXp,
    level,
    spent,
    available: level - 1 - spent,
    into: e.masteryXp - threshold(level),
    needed: threshold(level + 1) - threshold(level),
  };
}
export const MASTERY_RATES = { kill: 10, construction: 0.1, repair: 0.1 };

export function buyBaseStat(progress, id) {
  const stat = BASE_STATS.find((s) => s.id === id);
  if (!stat) return { ok: false, reason: "Unknown base stat" };
  progress.experience = normalizeExperience(progress.experience);
  const rank = progress.experience.ranks[id] || 0;
  if (rank >= stat.max) return { ok: false, reason: "Maximum rank reached" };
  if (experienceBudget(progress).available < 1)
    return { ok: false, reason: "Earn another level to gain a stat point" };
  progress.experience.ranks[id] = rank + 1;
  return { ok: true };
}
export function buyTowerSkill(progress, type, id) {
  const skill = TOWER_BY_ID[type]?.skills.find((s) => s.id === id);
  if (!skill) return { ok: false, reason: "Unknown tower skill" };
  progress.experience = normalizeExperience(progress.experience);
  const ranks = progress.experience.towers[type] || {};
  const rank = ranks[id] || 0;
  if (rank >= skill.max) return { ok: false, reason: "Maximum rank reached" };
  if (masteryBudget(progress).available < 1)
    return {
      ok: false,
      reason: "Earn another mastery level to gain a tower point",
    };
  progress.experience.towers[type] = { ...ranks, [id]: rank + 1 };
  return { ok: true };
}
export function applyBaseStats(rules, values) {
  const ranks = normalizeRanks(values);
  rules.armor = (ranks.armor || 0) * 0.02;
  const clock = 1 + (ranks.fabrication || 0) * 0.05;
  rules.buildSpeed *= clock;
  rules.miningSpeed = clock;
  rules.generationSpeed = clock;
  rules.constructionCost = 1 - (ranks.economy || 0) * 0.01;
  rules.miningYield *= 1 + (ranks.harvest || 0) * 0.05;
  for (const key of ["laserDamage", "thelDamage", "missileDamage"])
    rules[key] *= 1 + (ranks.firepower || 0) * 0.03;
  rules.repairRate *= 1 + (ranks.repair || 0) * 0.05;
  rules.generation *= 1 + (ranks.power || 0) * 0.05;
  return rules;
}
