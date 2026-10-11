// Modern progression. Classic operations always use the original rules.
export const RESEARCH_CAPACITY = 6;
export const BRANCHES = [
  {
    id: "power",
    name: "Power systems",
    subtitle: "Keep the network alive",
    color: "#8dbfff",
    icon: "solar",
  },
  {
    id: "industry",
    name: "Deep-space industry",
    subtitle: "Build beyond the next rock",
    color: "#edc980",
    icon: "miner",
  },
  {
    id: "weapons",
    name: "Applied ballistics",
    subtitle: "Make every shot count",
    color: "#efa0b6",
    icon: "missile",
  },
  {
    id: "support",
    name: "Field engineering",
    subtitle: "Bring everyone home",
    color: "#95dfbb",
    icon: "repair",
  },
];
const node = (
  id,
  branch,
  tier,
  name,
  cost,
  requires,
  effect,
  detail,
  modifiers,
  extra = {},
) => ({
  id,
  branch,
  tier,
  name,
  cost,
  requires,
  effect,
  detail,
  modifiers,
  load: tier === 3 ? 2 : 1,
  ...extra,
});
export const TECHNOLOGIES = [
  node(
    "solar_cells",
    "power",
    0,
    "Prismatic cells",
    2,
    [],
    "+20% solar generation",
    "A new photovoltaic stack captures more of the stellar spectrum.",
    { generation: 1.2 },
  ),
  node(
    "deep_storage",
    "power",
    1,
    "Dense capacitors",
    4,
    ["solar_cells"],
    "+40% energy-store capacity",
    "Hold a larger reserve for construction, storms, and sustained beams.",
    { storageCapacity: 1.4 },
  ),
  node(
    "long_links",
    "power",
    1,
    "Field couplers",
    4,
    ["solar_cells"],
    "+15 energy-link range",
    "Stretch every connection from 90 to 105 units. Obstructions and relay limits still apply.",
    { linkBonus: 15 },
  ),
  node(
    "storm_shield",
    "power",
    2,
    "Storm shielding",
    6,
    ["deep_storage", "long_links"],
    "50% solar output during storms",
    "Shielded collectors retain half their output through solar interference, up from 20%.",
    { stormOutput: 0.5 },
  ),
  node(
    "solar_overdrive",
    "power",
    3,
    "Stellar overdrive",
    9,
    ["storm_shield"],
    "+40% generation · −20% solar hull",
    "Trade resilience for extraordinary power density. Protect these stations behind the front line.",
    { generation: 1.4, solarHull: 0.8 },
    { tag: "OVERCLOCK" },
  ),
  node(
    "precision_drills",
    "industry",
    0,
    "Resonant drills",
    2,
    [],
    "+25% minerals per mining cycle",
    "Harvest five minerals per basic cycle, or 12.5 when upgraded. Deposits remain finite.",
    { miningYield: 1.25 },
  ),
  node(
    "survey_optics",
    "industry",
    1,
    "Survey optics",
    4,
    ["precision_drills"],
    "+15 mining range",
    "Expand a miner’s reach from 35 to 50 units beyond an asteroid’s edge.",
    { miningRange: 15 },
  ),
  node(
    "rapid_fabrication",
    "industry",
    1,
    "Rapid fabrication",
    4,
    ["precision_drills"],
    "25% faster construction and upgrades",
    "Shorten build intervals. Every construction increment still requires its normal energy.",
    { buildSpeed: 1.25 },
  ),
  node(
    "salvage",
    "industry",
    2,
    "Closed-loop recovery",
    6,
    ["survey_optics", "rapid_fabrication"],
    "Recover 80% of upgrade minerals",
    "Recycling normally returns 50% of upgrade spending. Base refunds and hull-damage penalties remain unchanged.",
    { upgradeRefund: 0.8 },
  ),
  node(
    "expedition_cargo",
    "industry",
    3,
    "Expedition freight",
    9,
    ["salvage"],
    "+300 starting minerals",
    "Bring a larger construction reserve to each new operation. Existing saves receive no extra cargo.",
    { startingMinerals: 300 },
    { tag: "LOGISTICS" },
  ),
  node(
    "focus_lenses",
    "weapons",
    0,
    "Focus lenses",
    2,
    [],
    "+15% laser and Pulser damage",
    "Tighter optical focus improves basic and Pulser damage without increasing shot energy.",
    { laserDamage: 1.15 },
  ),
  node(
    "missile_guidance",
    "weapons",
    1,
    "Predictive guidance",
    4,
    ["focus_lenses"],
    "+15% missile range · +25% speed",
    "Acquire distant targets and close the gap before they can damage the network.",
    { missileRange: 1.15, missileSpeed: 1.25 },
  ),
  node(
    "weapon_buffers",
    "weapons",
    1,
    "Pulse reservoirs",
    4,
    ["focus_lenses"],
    "+50% weapon energy buffers",
    "Larger local reserves keep a weapon firing longer after its supply line is cut.",
    { weaponCapacity: 1.5 },
  ),
  node(
    "beam_coherence",
    "weapons",
    2,
    "Beam coherence",
    6,
    ["missile_guidance", "weapon_buffers"],
    "+25% THEL damage and energy use",
    "Amplify the full sustained beam, including its ramp. Bring enough power to feed it.",
    { thelDamage: 1.25 },
  ),
  node(
    "proximity_warheads",
    "weapons",
    3,
    "Proximity warheads",
    9,
    ["beam_coherence"],
    "+30% blast radius · −15% missile damage",
    "Clear dense formations with a broader blast. Less effective against isolated heavy ships.",
    { missileSplash: 1.3, missileDamage: 0.85 },
    { tag: "AREA DENIAL" },
  ),
  node(
    "hull_weave",
    "support",
    0,
    "Composite hulls",
    2,
    [],
    "+15% structure hull",
    "Reinforce every player-built structure. Mission-critical derelicts keep their original hull.",
    { hull: 1.15 },
  ),
  node(
    "repair_tools",
    "support",
    1,
    "Precision repair",
    4,
    ["hull_weave"],
    "+25% drone repair throughput",
    "Repair 25 hull per second instead of 20, with the same energy cost per hull point.",
    { repairRate: 1.25 },
  ),
  node(
    "drone_cells",
    "support",
    1,
    "Drone endurance",
    4,
    ["hull_weave"],
    "+50% carried drone energy",
    "Increase each drone’s reserve from 80 to 120 so it can stay in the field longer.",
    { droneCapacity: 1.5 },
  ),
  node(
    "autoseal",
    "support",
    2,
    "Autoseal plating",
    6,
    ["repair_tools", "drone_cells"],
    "Powered hull regeneration after 8s",
    "After eight seconds without damage, restore 1% maximum hull per second, capped at 20 HP/s. Costs 0.08 energy per hull.",
    { regeneration: true },
  ),
  node(
    "capacitive_armor",
    "support",
    3,
    "Capacitive armor",
    9,
    ["autoseal"],
    "Absorb 25% incoming damage with power",
    "Divert a quarter of a hit into the local energy system at 0.1 energy per absorbed damage. No energy, no shield.",
    { shield: 0.25 },
    { tag: "BULWARK" },
  ),
];
export const TECH_BY_ID = Object.fromEntries(
  TECHNOLOGIES.map((t) => [t.id, t]),
);
export function normalizeResearch(value = {}, maxSpend = Infinity) {
  const proposed = new Set(Array.isArray(value?.owned) ? value.owned : []),
    owned = [];
  for (const t of TECHNOLOGIES)
    if (
      proposed.has(t.id) &&
      t.cost <= maxSpend &&
      t.requires.every((id) => owned.includes(id))
    ) {
      owned.push(t.id);
      maxSpend -= t.cost;
    }
  const active = [];
  let load = 0;
  for (const id of Array.isArray(value?.active) ? value.active : [])
    if (
      owned.includes(id) &&
      !active.includes(id) &&
      load + TECH_BY_ID[id].load <= RESEARCH_CAPACITY
    ) {
      active.push(id);
      load += TECH_BY_ID[id].load;
    }
  return { owned, active };
}
export function researchBudget(progress) {
  const stars = (collection) =>
    Object.entries(collection || {}).reduce(
      (total, [id, value]) =>
        total +
        (id.startsWith("classic")
          ? 0
          : Math.max(0, Math.min(3, Number(value?.stars) || 0))),
      0,
    );
  const earned =
    6 +
    2 * (stars(progress.completed) + stars(progress.challenges)) +
    4 * Math.floor(Math.max(0, Number(progress.endless?.cleared) || 0) / 5);
  const research = normalizeResearch(progress.research),
    spent = research.owned.reduce((n, id) => n + TECH_BY_ID[id].cost, 0);
  return {
    earned,
    spent,
    available: Math.max(0, earned - spent),
    load: research.active.reduce((n, id) => n + TECH_BY_ID[id].load, 0),
  };
}
export function researchEligibility(progress, id) {
  const t = TECH_BY_ID[id];
  if (!t) return { ok: false, reason: "Unknown technology" };
  const r = normalizeResearch(progress.research);
  if (r.owned.includes(id)) return { ok: false, reason: "Already researched" };
  const missing = t.requires.filter((id) => !r.owned.includes(id));
  if (missing.length)
    return {
      ok: false,
      reason:
        "Requires " + missing.map((id) => TECH_BY_ID[id].name).join(" + "),
    };
  if (researchBudget(progress).available < t.cost)
    return {
      ok: false,
      reason: `Need ${t.cost - researchBudget(progress).available} more Intel`,
    };
  return { ok: true };
}
export function buyResearch(progress, id) {
  const check = researchEligibility(progress, id);
  if (!check.ok) return check;
  progress.research = normalizeResearch(progress.research);
  progress.research.owned.push(id);
  if (researchBudget(progress).load + TECH_BY_ID[id].load <= RESEARCH_CAPACITY)
    progress.research.active.push(id);
  return { ok: true, equipped: progress.research.active.includes(id) };
}
export function toggleResearch(progress, id) {
  progress.research = normalizeResearch(progress.research);
  const r = progress.research,
    t = TECH_BY_ID[id];
  if (!t || !r.owned.includes(id))
    return { ok: false, reason: "Research this technology first" };
  if (r.active.includes(id)) {
    r.active = r.active.filter((x) => x !== id);
    return { ok: true };
  }
  if (researchBudget(progress).load + t.load > RESEARCH_CAPACITY)
    return {
      ok: false,
      reason: `Needs ${t.load} loadout slot${t.load > 1 ? "s" : ""}. Unequip another technology first.`,
    };
  r.active.push(id);
  return { ok: true };
}
export function resetResearch(progress) {
  progress.research = { owned: [], active: [] };
}
export function researchLoadout(progress, mission) {
  return mission.classic ? [] : normalizeResearch(progress.research).active;
}
export function researchRules(ids = []) {
  const r = {
    generation: 1,
    storageCapacity: 1,
    linkBonus: 0,
    stormOutput: 0.2,
    solarHull: 1,
    miningYield: 1,
    miningRange: 0,
    buildSpeed: 1,
    upgradeRefund: 0.5,
    startingMinerals: 0,
    laserDamage: 1,
    missileRange: 1,
    missileSpeed: 1,
    weaponCapacity: 1,
    thelDamage: 1,
    missileSplash: 1,
    missileDamage: 1,
    hull: 1,
    repairRate: 1,
    droneCapacity: 1,
    regeneration: false,
    shield: 0,
  };
  for (const id of new Set(ids)) {
    const tech = TECH_BY_ID[id];
    if (!tech) continue;
    for (const [key, value] of Object.entries(tech.modifiers)) {
      if (["linkBonus", "miningRange", "startingMinerals"].includes(key))
        r[key] += value;
      else if (
        ["stormOutput", "upgradeRefund", "regeneration", "shield"].includes(key)
      )
        r[key] = value;
      else r[key] *= value;
    }
  }
  return r;
}
export function applyResearchStats(s, type, r) {
  if (!r || type === "station") return s;
  s.hp *= r.hull * (type === "solar" ? r.solarHull : 1);
  s.link += r.linkBonus;
  if (type === "solar") s.generation *= r.generation;
  if (type === "battery") s.capacity *= r.storageCapacity;
  if (type === "miner") {
    s.range += r.miningRange;
    s.rate *= r.miningYield;
  }
  if (["laser", "thel", "missile"].includes(type))
    s.capacity *= r.weaponCapacity;
  if (type === "laser") s.damage *= r.laserDamage;
  if (type === "missile") {
    s.range *= r.missileRange;
    s.damage *= r.missileDamage;
    s.splash *= r.missileSplash;
  }
  if (type === "repair") s.rate *= r.repairRate;
  return s;
}
