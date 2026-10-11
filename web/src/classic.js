import reference from "../../docs/research/original-constants.json" with { type: "json" };
import survival from "../../docs/research/original-survival-waves.json" with { type: "json" };
export { reference };
export function applyOriginalStats(buildings, enemies) {
  const src = reference.structures;
  for (const [key, target] of Object.entries({
    relay: "relay",
    miner: "miner",
    solar: "solar",
    storage: "battery",
    repair: "repair",
    missile: "missile",
  })) {
    const d = src[key],
      b = buildings[target];
    b.link = 90;
    b.radius = d.size * 0.65;
    b.maxLinks = ["solar", "storage"].includes(key)
      ? 999
      : key === "relay"
        ? 6
        : 1;
    b.levels = d.levels.length;
    b.hp = d.levels[0].hp;
    b.upgradeCosts = d.levels.slice(1).map((l) => l.upgradeCost);
    b.stats = d.levels.map((l) => ({
      hp: l.hp,
      ...(l.range ? { range: l.range } : {}),
      ...(l.capacity ? { capacity: l.capacity } : {}),
      ...(key === "miner"
        ? {
            rate: l.displayedMineralsPerMinute / 60,
            range: 35,
            drain: 1 / 3,
            capacity: 1,
          }
        : {}),
      ...(key === "solar"
        ? {
            generation: (l.generationPerCycle * 20) / 11,
            capacity: l.energyBuffer,
          }
        : {}),
      ...(key === "missile"
        ? {
            damage: l.damage,
            salvo: l.salvo,
            splash: l.splash,
            range: l.range,
            capacity: l.energyBuffer,
            interval: 10,
            shotEnergy: 1,
            shotMinerals: 5,
          }
        : {}),
      ...(key === "repair" ? { capacity: 5, rate: 20, drain: 20 / 6 } : {}),
    }));
    Object.assign(b, b.stats[0]);
  }
  Object.assign(buildings.laser, {
    hp: 200,
    link: 90,
    radius: 12,
    range: 90,
    maxLinks: 1,
    levels: 4,
    capacity: 1,
    shotEnergy: 2 / 35,
    damage: 30,
    interval: 1,
    burst: 5,
    upgradeCosts: [100, 150, 300],
    stats: [
      {
        hp: 200,
        range: 90,
        damage: 30,
        interval: 1,
        shotEnergy: 2 / 35,
        capacity: 1,
        burst: 5,
      },
      {
        hp: 300,
        range: 110,
        damage: 12,
        interval: 0.5,
        shotEnergy: 5 / 28,
        capacity: 2.5,
        burst: 4,
      },
      {
        hp: 500,
        range: 115,
        damage: 14,
        interval: 0.4,
        shotEnergy: 10 / 28,
        capacity: 5,
        burst: 4,
      },
      {
        hp: 900,
        range: 130,
        damage: 16,
        interval: 0.3,
        shotEnergy: 15 / 28,
        capacity: 7.5,
        burst: 4,
      },
    ],
  });
  Object.assign(buildings.thel, {
    hp: 400,
    link: 90,
    radius: 15,
    range: 200,
    maxLinks: 1,
    levels: 3,
    capacity: 5,
    shotEnergy: 0,
    damage: 1,
    interval: 0.05,
    minRange: 0,
    upgradeCosts: [500, 800, 1000],
    stats: [
      { hp: 400, range: 200, damage: 1, capacity: 5 },
      { hp: 600, range: 290, damage: 5, capacity: 10 },
      { hp: 960, range: 390, damage: 10, capacity: 17.5 },
    ],
  });
  buildings.miner.description =
    "Extract finite asteroid minerals. Upgrade from 80 to 200 minerals per minute.";
  buildings.repair.description =
    "Four drones travel to damaged structures, repair their hull, and return to recharge.";
  buildings.thel.description =
    "A sustained beam that grows stronger while holding its target. Needs ample solar capacity.";
  buildings.battery.description =
    "Distribute energy and store a surplus. Increases reserve capacity, not generation.";
  for (const [t, hp, range] of [
    ["fighter", 200, 70],
    ["swarm", 200, 70],
    ["ring", 200, 60],
    ["bomber", 200, 200],
    ["mothership", 1600, 200],
  ])
    Object.assign(enemies[t], { hp, range });
  Object.assign(enemies.swarm, { damage: 10 });
  Object.assign(enemies.ring, {
    color: "#e7d471",
    shield: 0,
    missileResistance: 15,
  });
  enemies.suicide = {
    name: "Self destructor",
    hp: 200,
    speed: 52,
    damage: 60,
    interval: 1,
    range: 70,
    radius: 11,
    splash: 100,
    color: "#e8a36d",
  };
  enemies.child = {
    name: "Attack fighter",
    hp: 100,
    speed: 48,
    damage: 5,
    interval: 0.7,
    range: 70,
    radius: 7,
    color: "#e599ae",
  };
}
export function makeClassic(buildOrder) {
  return Array.from({ length: 9 }, (_, i) => {
    const n = i + 1,
      p = reference.campaign.mapParameters.find((m) => m.mission === n);
    const mine = reference.campaign.miningMissions.includes(n);
    const waves = reference.campaign.miningWaves[n];
    const scheduled = survival[n]?.filter(
      (row) => row[0] < (n === 3 ? 600 : 1200),
    );
    return {
      id: "classic" + n,
      name: `Mission ${n}`,
      sector: "CLASSIC / 2009 RULESET",
      classic: true,
      kind: mine ? "mine" : n === 6 ? "boss" : "survive",
      goal: mine ? 1 : n === 6 ? 35 : n === 3 ? 600 : 1200,
      brief: mine
        ? "Mine half the asteroid field. Enemy arrivals follow your extraction progress, so every expansion raises the stakes."
        : n === 6
          ? "An empty sector and a heavy starting reserve. Prepare for a sustained mothership assault."
          : `Keep the network alive for ${n === 3 ? "10" : "20"} minutes and clear the remaining attackers.`,
      tip: "All seven structures are available. Space/U upgrades; P creates a pulser; T creates a THEL. Mining progress triggers waves.",
      seed: 100 + n,
      minerals: reference.campaign.cashAfterInitialSolar[i],
      asteroids: p?.asteroidCount || 0,
      world: n === 6 ? 1200 : Math.max(1000, (p?.fieldScale || 300) * 3),
      waves: waves?.length || scheduled?.length || (n === 6 ? 6 : 18),
      firstWave: scheduled?.[0][0] ?? (n === 6 ? 180 : 35),
      waveGap: n === 3 ? 32 : 60,
      enemyTier: Math.min(4, n),
      par: n === 6 ? 600 : n === 3 ? 620 : n === 9 ? 1220 : 900,
      unlocked: buildOrder,
      thel: true,
      miningWaves: waves || null,
      scheduledWaves: scheduled || null,
      timedWaves: n === 6 ? reference.campaign.mission6.waveSeconds : null,
      boss: n === 6,
      bossCount: 35,
      classicMap: p,
    };
  });
}
