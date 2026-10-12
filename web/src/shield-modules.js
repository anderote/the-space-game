export const SHIELD_MODULE_COSTS = [100, 160, 240];
export const SHIELD_MODULE_FRACTIONS = [0, 0.2, 0.35, 0.5];
export const SHIELD_RECHARGE_DELAY = 5;
export const SHIELD_ENERGY_PER_HP = 0.2;
export function shieldCapacity(b, rules = b.research) {
  if (!rules?.shieldModules || b.type === "station") return 0;
  const level = Math.min(3, Math.max(0, Math.floor(b.shieldLevel || 0)));
  return (b.maxHp || 0) * SHIELD_MODULE_FRACTIONS[level];
}
export function shieldStatus(b, time) {
  const capacity = shieldCapacity(b);
  if (!capacity) return "No rechargeable shield";
  const current = Math.max(0, Math.min(capacity, b.shieldCharge || 0));
  const delay = Math.max(
    0,
    SHIELD_RECHARGE_DELAY - (time - (b.lastDamaged ?? -Infinity)),
  );
  const status =
    b.construction < 1
      ? "INSTALLING"
      : current >= capacity - 1e-6
        ? "CHARGED"
        : delay > 0
          ? `RECHARGE IN ${Math.ceil(delay)}s`
          : b.powered || time - (b.lastShieldRecharge ?? -Infinity) < 0.75
            ? "RECHARGING"
            : "NEEDS POWER";
  return `${Math.floor(current)} / ${Math.round(capacity)} SHIELD · ${status}`;
}
export const enemyDamageMultiplier = (mission) => (mission.classic ? 1 : 0.9);
