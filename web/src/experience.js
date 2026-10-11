// Command experience is separate from the Intel technology economy.
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
    name: "Build speed",
    icon: "relay",
    effect: "+5% construction and upgrade speed",
    perRank: 5,
    unit: "% build speed",
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
  return { xp, ranks: normalizeRanks(value?.ranks, experienceLevel(xp) - 1) };
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
export function applyBaseStats(rules, values) {
  const ranks = normalizeRanks(values);
  rules.armor = (ranks.armor || 0) * 0.02;
  rules.buildSpeed *= 1 + (ranks.fabrication || 0) * 0.05;
  rules.miningYield *= 1 + (ranks.harvest || 0) * 0.05;
  for (const key of ["laserDamage", "thelDamage", "missileDamage"])
    rules[key] *= 1 + (ranks.firepower || 0) * 0.03;
  rules.repairRate *= 1 + (ranks.repair || 0) * 0.05;
  rules.generation *= 1 + (ranks.power || 0) * 0.05;
  return rules;
}
