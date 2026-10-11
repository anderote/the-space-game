// Browser-edition extensions requested after the original-stat audit. Keep the
// recovered tiers untouched and append explicit, finite upgrade configurations.
export const MINER_SCALE = 0.75;
export const REPAIR_SCALE = 0.65;
export const STRUCTURE_SCALE = 0.85;
export const ENEMY_SCALE = 0.6;
export const ASTEROID_ORE_MULTIPLIER = 1.5;
export const solarPetals = (level) => Math.max(2, Math.min(6, level + 1));

export function extendStructureUpgrades(buildings) {
  const append = (type, tiers) => {
    const b = buildings[type];
    for (const { cost, ...changes } of tiers) {
      b.stats.push({ ...b.stats.at(-1), ...changes });
      b.upgradeCosts.push(cost);
    }
    b.levels = b.stats.length;
  };
  append("relay", [
    { cost: 40, hp: 180, maxLinks: 8, link: 95 },
    { cost: 80, hp: 300, maxLinks: 10, link: 100 },
    { cost: 140, hp: 450, maxLinks: 12, link: 110 },
  ]);
  append("miner", [
    {
      cost: 200,
      hp: 750,
      rate: 320 / 60,
      range: 40,
      capacity: 1.5,
      miningEnergy: 1.5,
    },
    {
      cost: 350,
      hp: 1050,
      rate: 480 / 60,
      range: 45,
      capacity: 2,
      miningEnergy: 2,
    },
  ]);
  append("solar", [
    { cost: 350, hp: 1250, generation: 4.2 / 0.55, capacity: 20 },
    { cost: 550, hp: 1550, generation: 5.4 / 0.55, capacity: 28 },
  ]);
  append("battery", [
    { cost: 700, hp: 1000, capacity: 1200 },
    { cost: 1000, hp: 1350, capacity: 2000 },
  ]);
  append("repair", [
    { cost: 300, hp: 850, range: 350, rate: 25, capacity: 8 },
    { cost: 500, hp: 1150, range: 400, rate: 30, capacity: 12 },
  ]);
  append("missile", [
    {
      cost: 1400,
      hp: 700,
      range: 660,
      damage: 625,
      salvo: 5,
      splash: 53.2,
      capacity: 8,
    },
  ]);
  append("thel", [
    { cost: 1400, hp: 1300, range: 450, damage: 15, capacity: 25 },
  ]);
  for (const [type, b] of Object.entries(buildings)) {
    b.visualScale =
      type === "solar"
        ? 1
        : type === "miner"
          ? MINER_SCALE
          : type === "repair"
            ? REPAIR_SCALE
            : STRUCTURE_SCALE;
    b.radius *= b.visualScale;
  }
  buildings.relay.description =
    "Extend the energy network. Upgrade from six to twelve connections and reinforce the backbone.";
  buildings.miner.description =
    "Compact mineral extractor. Four levels yield 80 / 200 / 320 / 480 minerals per minute before research.";
  buildings.solar.description =
    "Unfold two to six solar petals across five levels. Each upgrade increases generation and its local energy buffer.";
  buildings.solar.pickRadius = 29;
  buildings.battery.description =
    "Distribute energy and store a surplus. Four levels hold 200 / 600 / 1,200 / 2,000 energy.";
  buildings.repair.description =
    "Four repair drones. Upgrade station range, hull and late-tier repair throughput.";
}
