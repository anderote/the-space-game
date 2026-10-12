import { MAX_SKILL_RANK, TOWER_ARMOR_STEP } from "./progression-balance.js";
import { missilePayloadStats } from "./missile-flight.js";
// XP specializations improve a building class, independently of mineral tiers.
const skill = (id, name, perRank, effect, extra = {}) => ({
  id,
  name,
  perRank,
  effect,
  max: MAX_SKILL_RANK,
  unit: "%",
  ...extra,
});
const hull = skill("hull", "Health", 5, "+5% maximum hull");
const armor = skill("armor", "Armor", 2, "Reduce remaining hull damage by 2%", {
  diminishing: true,
});
const shields = skill(
  "shields",
  "Powered shields",
  1,
  "Absorb 1% of otherwise unshielded damage",
  { detail: "Uses 0.1 energy per absorbed hull point." },
);
const defenses = [hull, armor, shields];
const reach = skill("link", "Link reach", 3, "+3% energy-link range");
const weapons = [
  skill("damage", "Damage", 5, "+5% damage per hit"),
  skill(
    "fireRate",
    "Fire rate",
    3,
    "+3% faster firing cycles; normal energy costs apply",
  ),
  skill("range", "Targeting range", 3, "+3% weapon range"),
  ...defenses,
];
export const TOWER_TYPES = [
  {
    id: "relay",
    name: "Energy relay",
    icon: "relay",
    color: "#8ae8d0",
    skills: [
      reach,
      skill("ports", "Connection ports", 1, "+1 network connection", {
        max: MAX_SKILL_RANK,
        unit: "connections",
      }),
      ...defenses,
    ],
  },
  {
    id: "miner",
    name: "Mineral miner",
    icon: "miner",
    color: "#edc980",
    skills: [
      skill("yield", "Extraction yield", 5, "+5% minerals per cycle"),
      skill(
        "speed",
        "Drill speed",
        5,
        "+5% faster mining cycles; normal energy costs apply",
      ),
      skill("range", "Mining reach", 3, "+3% mining range"),
      ...defenses,
    ],
  },
  {
    id: "solar",
    name: "Solar station",
    icon: "solar",
    color: "#8dbfff",
    skills: [
      skill("output", "Collector output", 5, "+5% energy per generation cycle"),
      skill(
        "speed",
        "Collector clock",
        5,
        "+5% faster solar generation cycles",
      ),
      reach,
      ...defenses,
    ],
  },
  {
    id: "battery",
    name: "Energy store",
    icon: "battery",
    color: "#93a7ed",
    skills: [
      skill(
        "capacity",
        "Storage density",
        5,
        "+5% energy capacity; charges normally",
      ),
      reach,
      ...defenses,
    ],
  },
  {
    id: "repair",
    name: "Repair station",
    icon: "repair",
    color: "#95dfbb",
    skills: [
      skill(
        "repairRate",
        "Repair speed",
        5,
        "+5% drone repair throughput; one energy per healed hull",
      ),
      skill("range", "Service range", 3, "+3% drone dispatch range"),
      skill(
        "droneEnergy",
        "Drone reserves",
        5,
        "+5% carried drone energy; existing drones charge normally",
      ),
      ...defenses,
    ],
  },
  {
    id: "laser",
    name: "Basic laser",
    icon: "laser",
    color: "#efa0b6",
    skills: weapons,
  },
  {
    id: "pulser",
    name: "Pulser",
    icon: "laser",
    color: "#e9b6a0",
    skills: weapons,
  },
  {
    id: "thel",
    name: "THEL beam",
    icon: "thel",
    color: "#9be9ff",
    skills: weapons.map((s) =>
      s.id === "fireRate"
        ? {
            ...s,
            name: "Beam cycling",
            effect: "+3% beam throughput and energy draw",
          }
        : s.id === "damage"
          ? { ...s, effect: "+5% sustained beam damage and energy draw" }
          : s,
    ),
  },
  {
    id: "missile",
    name: "Missile launcher",
    icon: "missile",
    color: "#d7b9ef",
    skills: weapons,
  },
  {
    id: "missile_round",
    name: "Missile ordnance",
    icon: "missile",
    color: "#8dd4ef",
    skills: [
      skill(
        "damage",
        "Warhead damage",
        5,
        "+5% missile damage; stacks with launcher damage",
      ),
      skill(
        "range",
        "Engagement range",
        3,
        "+3% launcher targeting range; stacks with launcher range",
      ),
      skill("splash", "Blast radius", 4, "+4% area-of-effect radius"),
      skill(
        "fuel",
        "Fuel reserves",
        5,
        "+5% flight lifetime from the eight-second baseline",
      ),
      skill("hull", "Missile hull", 5, "+5% missile hull against interception"),
      skill(
        "shields",
        "Missile shields",
        2,
        "Launch with shields equal to 2% of missile hull",
        {
          detail:
            "Shields absorb point-defense hits first, do not recharge, and cost 0.2 launch energy per shield HP.",
        },
      ),
    ],
  },
];
export const TOWER_BY_ID = Object.fromEntries(
  TOWER_TYPES.map((t) => [t.id, t]),
);
export function normalizeTowerRanks(value = {}, budget = Infinity) {
  const towers = {};
  for (const type of TOWER_TYPES) {
    const ranks = {};
    for (const skill of type.skills) {
      const proposed = value?.[type.id]?.[skill.id];
      const rank = Math.min(
        skill.max,
        budget,
        Number.isFinite(proposed) ? Math.floor(Math.max(0, proposed)) : 0,
      );
      if (rank) ranks[skill.id] = rank;
      budget -= rank;
    }
    if (Object.keys(ranks).length) towers[type.id] = ranks;
  }
  return towers;
}
export const towerPoints = (towers) =>
  Object.values(towers).reduce(
    (n, ranks) => n + Object.values(ranks).reduce((sum, rank) => sum + rank, 0),
    0,
  );
export function applyTowerStats(s, type, level, rules) {
  const key = type === "laser" && level > 1 ? "pulser" : type;
  const r = rules.towers?.[key] || {};
  s.hp *= 1 + (r.hull || 0) * 0.05;
  s.armor = 1 - (1 - rules.armor) * (1 - TOWER_ARMOR_STEP) ** (r.armor || 0);
  s.shield = 1 - (1 - rules.shield) * (1 - (r.shields || 0) * 0.01);
  s.link *= 1 + (r.link || 0) * 0.03;
  if (type === "relay") s.maxLinks += r.ports || 0;
  s.range *= 1 + (r.range || 0) * 0.03;
  s.fireRate = 1 + (r.fireRate || 0) * 0.03;
  s.interval /= s.fireRate;
  if (type === "thel")
    s.beamDamageMultiplier = rules.thelDamage * (1 + (r.damage || 0) * 0.05);
  else s.damage *= 1 + (r.damage || 0) * 0.05;
  if (type === "missile") {
    const payload = missilePayloadStats(rules);
    s.damage *= payload.damage;
    s.range *= payload.range;
    s.splash *= payload.splash;
    s.missileHull = payload.hull;
    s.missileShield = payload.shield;
    s.missileFuel = payload.fuel;
    s.launchEnergy = payload.launchEnergy;
  }
  if (type === "miner") {
    const speed = 1 + (r.speed || 0) * 0.05;
    s.rate *= (1 + (r.yield || 0) * 0.05) * speed;
    s.miningInterval /= speed;
  }
  if (type === "solar") {
    const speed = 1 + (r.speed || 0) * 0.05;
    s.generation *= (1 + (r.output || 0) * 0.05) * speed;
    s.generationInterval /= speed;
  }
  if (type === "battery") s.capacity *= 1 + (r.capacity || 0) * 0.05;
  if (type === "repair") {
    s.rate *= 1 + (r.repairRate || 0) * 0.05;
    s.droneEnergy =
      80 * rules.droneCapacity * (1 + (r.droneEnergy || 0) * 0.05);
  }
  return s;
}
