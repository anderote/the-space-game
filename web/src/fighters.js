export const FIGHTER_MINERALS = 20;
export function fighterStats(rules) {
  const r = rules.towers?.fighter_craft || {};
  const hp = 80 * (1 + (r.hull || 0) * 0.05) * rules.hull;
  return {
    hp,
    damage: 20 * (1 + (r.damage || 0) * 0.05) * rules.laserDamage,
    interval: 0.6 / (1 + (r.fireRate || 0) * 0.03),
    range: 90 * (1 + (r.range || 0) * 0.03),
    speed: 120 * (1 + (r.speed || 0) * 0.03),
    fuel: 20 * (1 + (r.fuel || 0) * 0.05),
    energy: 24,
    armor: 1 - (1 - rules.armor) * 0.98 ** (r.armor || 0),
    shield: hp * (r.shields || 0) * 0.02,
  };
}
export function damageFighter(f, damage) {
  damage *= 1 - f.config.armor;
  const absorbed = Math.min(f.shieldCharge, damage);
  f.shieldCharge -= absorbed;
  damage -= absorbed;
  f.repairXpDebt = (f.repairXpDebt || 0) + Math.min(f.hp, damage);
  f.hp -= damage;
}
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
function nearestEnemy(sim, center, radius) {
  let target,
    best = radius;
  for (const e of sim.enemies) {
    if (e.hp <= 0) continue;
    const d = distance(center, e);
    if (d < best) {
      best = d;
      target = e;
    }
  }
  return target;
}
function move(f, target, dt, speed = f.config.speed) {
  const desired = Math.atan2(target.y - f.y, target.x - f.x);
  const delta = Math.atan2(
    Math.sin(desired - f.angle),
    Math.cos(desired - f.angle),
  );
  f.angle += Math.max(-2.8 * dt, Math.min(2.8 * dt, delta));
  f.x += Math.cos(f.angle) * speed * dt;
  f.y += Math.sin(f.angle) * speed * dt;
}
export function updateFighters(sim, dt, stats) {
  if (sim.mission.classic) return;
  sim.fighters ??= [];
  for (const home of sim.buildings) {
    if (home.type !== "hangar" || home.hp <= 0 || home.construction < 1)
      continue;
    const s = stats(home);
    home.launchCooldown = Math.max(0, (home.launchCooldown || 0) - dt);
    const owned = sim.fighters.filter((f) => f.homeId === home.id && f.hp > 0);
    if (
      owned.length < s.fighterSlots &&
      home.launchCooldown <= 0 &&
      nearestEnemy(sim, home, s.range)
    ) {
      const config = fighterStats(sim.rules);
      const cost = config.energy + config.shield * 0.2;
      if (sim.minerals >= FIGHTER_MINERALS && sim.useEnergy(home, cost)) {
        sim.minerals -= FIGHTER_MINERALS;
        sim.spent += FIGHTER_MINERALS;
        const target = nearestEnemy(sim, home, s.range);
        sim.fighters.push({
          id: ++sim.uid,
          type: "fighter_craft",
          isFighter: true,
          homeId: home.id,
          x: home.x,
          y: home.y,
          angle: Math.atan2(target.y - home.y, target.x - home.x),
          config,
          repairXpDebt: 0,
          hp: config.hp,
          maxHp: config.hp,
          shieldCharge: config.shield,
          energy: config.energy,
          fuel: config.fuel,
          cooldown: 0,
          mode: "engage",
        });
        home.launchCooldown = s.launchInterval;
        home.activity = 1;
        sim.effect("hit", home.x, home.y, { color: "#8dd4ef" });
      }
    }
  }
  for (const f of sim.fighters) {
    if (f.hp <= 0) continue;
    const home = sim.buildings.find((b) => b.id === f.homeId && b.hp > 0);
    if (!home) {
      f.hp = 0;
      continue;
    }
    const s = stats(home),
      c = f.config;
    f.cooldown = Math.max(0, f.cooldown - dt);
    if (f.mode === "docked") {
      f.x = home.x;
      f.y = home.y;
      if (home.construction < 1) continue;
      const replenish = (key, max, rate, energyPerUnit) => {
        const amount = Math.min(max - f[key], rate * dt);
        if (amount > 0 && sim.useEnergy(home, amount * energyPerUnit)) {
          f[key] += amount;
          if (key === "hp") sim.creditRepair(f, amount);
          home.activity = 0.5;
        }
      };
      replenish("hp", f.maxHp, s.serviceRate, 1);
      replenish("energy", c.energy, s.serviceRate, 1);
      replenish("fuel", c.fuel, s.serviceRate, 0.2);
      replenish("shieldCharge", c.shield, s.serviceRate, 0.2);
      if (
        f.hp >= f.maxHp - 1e-6 &&
        f.energy >= c.energy - 1e-6 &&
        f.fuel >= c.fuel - 1e-6 &&
        f.shieldCharge >= c.shield - 1e-6 &&
        home.launchCooldown <= 0 &&
        nearestEnemy(sim, home, s.range)
      ) {
        f.mode = "engage";
        home.launchCooldown = s.launchInterval;
      }
      continue;
    }
    f.fuel -= dt;
    if (f.fuel <= 0) {
      f.hp = 0;
      continue;
    }
    let target = nearestEnemy(sim, f, s.range);
    if (
      !target ||
      distance(target, home) > s.range * 1.25 ||
      f.hp < f.maxHp * 0.35 ||
      f.energy < 1 ||
      f.fuel < distance(f, home) / c.speed + 2 ||
      home.construction < 1
    )
      f.mode = "return";
    if (f.mode === "return") {
      if (distance(f, home) < Math.max(14, c.speed * dt)) {
        f.mode = "docked";
        f.x = home.x;
        f.y = home.y;
      } else move(f, home, dt);
      continue;
    }
    f.targetId = target.id;
    const range = distance(f, target);
    move(f, target, dt, range < c.range * 0.6 ? c.speed * 0.55 : c.speed);
    if (range <= c.range && f.cooldown <= 0 && f.energy >= 1) {
      f.energy--;
      f.cooldown = c.interval;
      sim.damageEnemy(target, c.damage);
      sim.effect("beam", f.x, f.y, {
        toX: target.x,
        toY: target.y,
        color: "#89efd9",
      });
    }
  }
  for (const f of sim.fighters)
    if (f.hp <= 0)
      sim.effect("explosion", f.x, f.y, { size: 14, color: "#8fc8ef" });
  sim.fighters = sim.fighters.filter((f) => f.hp > 0);
}
