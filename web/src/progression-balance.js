export const MAX_SKILL_RANK = 50;
// Armor ranks compound on remaining damage rather than reaching immunity.
export const BASE_ARMOR_STEP = 0.03;
export const TOWER_ARMOR_STEP = 0.02;
export function skillBonus(skill, rank) {
  return skill.diminishing
    ? Math.round(100 * (1 - (1 - skill.perRank / 100) ** rank))
    : rank * skill.perRank;
}
