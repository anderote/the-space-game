import { BUILDINGS, ENEMIES, DIFFICULTIES } from "./content.js";
import { researchRules, applyResearchStats } from "./research.js";
import { ASTEROID_ORE_MULTIPLIER } from "./structure-upgrades.js";
import { XP_RATES, normalizeRanks } from "./experience.js";
export const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
export function rng(seed) {
  let n = seed >>> 0;
  const next = () => {
    n = (n + 0x6d2b79f5) >>> 0;
    let t = n;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  next.state = () => n;
  next.restore = (value) => {
    n = value >>> 0;
  };
  return next;
}
export function segmentDistance(p, a, b) {
  const dx = b.x - a.x,
    dy = b.y - a.y;
  const t = Math.max(
    0,
    Math.min(
      1,
      ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1),
    ),
  );
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
}
// Decorative panels and tips may overlap; the central construction hull cannot.
export const placementRadius = (type) => BUILDINGS[type].radius * 0.82;
export const linkClearance = (type) =>
  Math.max(2, BUILDINGS[type].radius * 0.35);
export const asteroidRadius = (a) =>
  a.radius * (0.72 + 0.28 * Math.min(1, a.ore / (a.maxOre || a.ore || 1)));
const statCache = new WeakMap();
export function stats(b) {
  const cached = statCache.get(b);
  if (
    cached &&
    cached.type === b.type &&
    cached.level === b.level &&
    cached.research === b.research
  )
    return cached.value;
  const d = BUILDINGS[b.type],
    i = b.level - 1;
  const level = d.stats?.[i];
  const value = applyResearchStats(
    {
      ...d,
      hp: d.hp * (1 + i * 0.5),
      range: (d.range || 0) * (1 + i * 0.15),
      damage: (d.damage || 0) * (1 + i * 0.55),
      rate: (d.rate || 0) * (1 + i * 0.6),
      generation: (d.generation || 0) * (1 + i * 0.65),
      capacity: (d.capacity || 0) * (1 + i),
      interval: d.interval || 1,
      ...level,
    },
    b.type,
    b.research,
  );
  statCache.set(b, {
    type: b.type,
    level: b.level,
    research: b.research,
    value,
  });
  return value;
}
const relays = (b) => ["relay", "solar", "battery"].includes(b.type);
export class Simulation {
  constructor(
    mission,
    difficulty = "normal",
    snapshot = null,
    researchIds = [],
    statRanks = {},
  ) {
    this.researchIds = mission.classic
      ? []
      : [...(snapshot ? snapshot.researchIds || [] : researchIds)];
    this.statRanks = mission.classic
      ? {}
      : normalizeRanks(snapshot?.statRanks || statRanks);
    this.rules = researchRules(this.researchIds, this.statRanks);
    this.mission = mission;
    this.difficulty = difficulty;
    this.diff = DIFFICULTIES[difficulty] || DIFFICULTIES.normal;
    this.random = rng(mission.seed);
    this.buildings = [];
    this.asteroids = [];
    this.enemies = [];
    this.projectiles = [];
    this.drones = [];
    this.effects = [];
    this.links = [];
    this.groups = [];
    this.flows = [];
    this.adjacency = new Map();
    this.events = [];
    this.uid = 0;
    this.time = 0;
    this.wave = 0;
    this.nextWave = mission.firstWave;
    this.minerals =
      Math.floor(mission.minerals * this.diff.resources) +
      this.rules.startingMinerals;
    this.mined = 0;
    this.kills = 0;
    this.combatKills = 0;
    this.intelCollected = 0;
    this.intelCredit = { rare: 0, earned: 0 };
    this.xpEarned = 0;
    this.xpCredit = 0;
    this.bossKills = 0;
    this.lost = 0;
    this.spent = 0;
    this.status = "playing";
    this.speed = 1;
    this.paused = false;
    this.minersOn = true;
    this.missilesOn = true;
    this.networkDirty = true;
    this.lowPowerTime = 0;
    this.income = 0;
    this.generation = 0;
    this.consumption = 0;
    this.energy = 0;
    this.capacity = 0;
    this.waveAnnounce = 0;
    if (snapshot) {
      this.restore(snapshot);
      return;
    }
    this.generateField();
    if (mission.classic && mission.kind === "mine")
      this.mission = {
        ...mission,
        goal: this.asteroids.reduce((v, a) => v + a.ore, 0) * 0.5,
      };
    this.addBuilding("solar", 0, 0, true);
    if (!mission.classic) this.addBuilding("relay", 65, 0, true);
    if (mission.station) {
      const b = this.addBuilding("station", 150, 75, true);
      b.hp = b.maxHp * mission.stationHealth;
      b.repairXpDebt = b.maxHp - b.hp;
    }
    if (mission.id !== 0 && !mission.classic) {
      this.addBuilding("miner", 45, 52, true);
      if (mission.waves > 0) this.addBuilding("laser", -52, 42, true);
    }
    this.rebuildNetwork();
  }
  setResearchLoadout(ids, ranks = this.statRanks) {
    const oldLinkBonus = this.rules.linkBonus;
    this.researchIds = this.mission.classic ? [] : [...new Set(ids)];
    this.statRanks = this.mission.classic ? {} : normalizeRanks(ranks);
    this.rules = researchRules(this.researchIds, this.statRanks);
    for (const b of this.buildings) {
      // Preserve damage percentage: swapping hull modifiers cannot heal a ship.
      const health = b.hp / b.maxHp;
      b.research = this.rules;
      const configured = stats(b);
      b.maxHp = configured.hp;
      b.hp = Math.min(1, health) * b.maxHp;
      b.repairXpDebt = Math.min(b.repairXpDebt || 0, b.maxHp - b.hp);
      b.energy = Math.min(b.energy, configured.capacity || 0);
      if (oldLinkBonus !== this.rules.linkBonus) b.linkInitialized = false;
    }
    for (const d of this.drones)
      d.energy = Math.min(d.energy, 80 * this.rules.droneCapacity);
    // Capacity upgrades must charge normally. Freight is a launch benefit only.
    this.rebuildNetwork();
    this.energy = this.buildings.reduce((total, b) => total + b.energy, 0);
    this.capacity = this.buildings.reduce(
      (total, b) => total + (stats(b).capacity || 0),
      0,
    );
    this.generation =
      this.buildings.reduce(
        (total, b) =>
          total + (b.construction >= 1 ? stats(b).generation || 0 : 0),
        0,
      ) * (this.storm ? this.rules.stormOutput : 1);
  }
  generateField() {
    const add = (x, y, r, ore) =>
      this.asteroids.push({
        id: ++this.uid,
        x,
        y,
        radius: r,
        ore: ore * ASTEROID_ORE_MULTIPLIER,
        maxOre: ore * ASTEROID_ORE_MULTIPLIER,
        rotation: this.random() * 6.28,
        seed: Math.floor(this.random() * 999999),
      });
    if (this.mission.classic) {
      const m = this.mission.classicMap;
      if (!m) return;
      const rotation = this.random() * Math.PI;
      for (let i = 0; i < m.asteroidCount; i++) {
        for (let attempt = 0; attempt < 120; attempt++) {
          const size =
              m.sizeIndexMin +
              this.random() * (m.sizeIndexMax - m.sizeIndexMin),
            r = size + 5;
          let x = (this.random() * 2 - 1) * m.fieldScale,
            y = (this.random() * 2 - 1) * 55;
          const xx = x * Math.cos(rotation) - y * Math.sin(rotation),
            yy = x * Math.sin(rotation) + y * Math.cos(rotation);
          if (
            Math.hypot(xx, yy) > r + 28 &&
            this.asteroids.every(
              (a) => distance({ x: xx, y: yy }, a) > a.radius + r + 14,
            )
          ) {
            add(xx, yy, r, Math.round((5 + size) * 52));
            break;
          }
        }
      }
      return;
    }
    add(57, 100, 24, 1100);
    add(-98, -48, 29, 1400);
    add(190, -70, 36, 1900);
    for (let i = 3; i < this.mission.asteroids; i++) {
      for (let tries = 0; tries < 70; tries++) {
        const a = this.random() * Math.PI * 2,
          rad = 170 + this.random() * this.mission.world * 0.38,
          x = Math.cos(a) * rad,
          y = Math.sin(a) * rad,
          r = 14 + this.random() * 30;
        if (
          this.asteroids.every(
            (o) => distance({ x, y }, o) > r + o.radius + 48,
          ) &&
          (!this.mission.station ||
            distance({ x, y }, { x: 150, y: 75 }) > r + 80)
        ) {
          add(x, y, r, Math.round(500 + r * 37));
          break;
        }
      }
    }
  }
  addBuilding(type, x, y, free = false) {
    const d = BUILDINGS[type];
    const b = {
      id: ++this.uid,
      type,
      x,
      y,
      level: 1,
      hp: d.hp,
      maxHp: d.hp,
      energy: free ? (d.capacity || 0) * 0.7 : 0,
      powered: false,
      connected: false,
      cooldown: 0,
      angle: 0,
      activity: 0,
      investment: d.cost,
      constructionUnits: free ? 10 : 0,
      constructionTarget: 10,
      buildCooldown: 0,
      buildEnergy: 0,
      group: -1,
      beamTime: 0,
      beamTarget: null,
      baseCost: d.cost,
      upgradeSpent: 0,
      droneCooldown: 0,
      construction: free ? 1 : 0,
    };
    b.research = this.rules;
    const configured = stats(b);
    b.hp = b.maxHp = configured.hp;
    b.energy = free ? (configured.capacity || 0) * 0.7 : 0;
    this.buildings.push(b);
    this.networkDirty = true;
    return b;
  }
  blocked(a, b) {
    return (
      this.asteroids.some(
        (o) => o.ore > 0 && segmentDistance(o, a, b) < asteroidRadius(o) * 0.88,
      ) ||
      this.buildings.some(
        (o) =>
          o.id !== a.id &&
          o.id !== b.id &&
          segmentDistance(o, a, b) < linkClearance(o.type),
      )
    );
  }
  canLink(a, b) {
    return relays(a) || relays(b)
      ? distance(a, b) < Math.min(stats(a).link, stats(b).link) &&
          !this.blocked(a, b)
      : false;
  }
  placement(type, x, y) {
    if (!BUILDINGS[type]) return { ok: false, reason: "Unknown structure" };
    const d = stats({ type, level: 1, research: this.rules });
    if (!this.mission.unlocked.includes(type))
      return { ok: false, reason: "Unavailable in this mission" };
    if (this.status !== "playing")
      return { ok: false, reason: "Mission has ended" };
    if (this.minerals < d.cost)
      return { ok: false, reason: `Need ${d.cost} minerals` };
    if (Math.hypot(x, y) > this.mission.world * 0.68)
      return { ok: false, reason: "Outside the sector boundary" };
    if (
      this.buildings.some(
        (b) =>
          distance({ x, y }, b) <
          placementRadius(type) + placementRadius(b.type),
      )
    )
      return { ok: false, reason: "Too close to another structure" };
    if (
      this.asteroids.some(
        (a) =>
          a.ore > 0 &&
          distance({ x, y }, a) <
            asteroidRadius(a) * 0.88 + placementRadius(type),
      )
    )
      return { ok: false, reason: "Asteroid obstructs construction" };
    const byId = new Map(this.buildings.map((b) => [b.id, b]));
    if (
      this.links.some((l) => {
        const a = byId.get(l.a),
          b = byId.get(l.b);
        return a && b && segmentDistance({ x, y }, a, b) < linkClearance(type);
      })
    )
      return {
        ok: false,
        reason: "An existing energy link crosses this location",
      };
    const ghost = { type, x, y, id: -1, level: 1, research: this.rules };
    const candidates = this.buildings.filter(
      (b) =>
        relays(b) &&
        b.connected &&
        b.construction >= 1 &&
        this.degree(b.id) < stats(b).maxLinks &&
        this.canLink(ghost, b),
    );
    const ore = this.asteroids.filter(
      (a) => a.ore > 0 && distance({ x, y }, a) - a.radius <= d.range,
    );
    if (type === "miner" && !ore.length)
      return { ok: false, reason: "No asteroid within mining range" };
    return {
      ok: true,
      links: candidates,
      ore,
      powered: candidates.length > 0,
      warning: candidates.length ? "" : "No power route — blueprint will wait",
    };
  }
  build(type, x, y) {
    const check = this.placement(type, x, y);
    if (!check.ok) return check;
    this.minerals -= BUILDINGS[type].cost;
    this.spent += BUILDINGS[type].cost;
    const b = this.addBuilding(type, x, y);
    this.rebuildNetwork();
    this.emit("build", { x, y });
    return { ok: true, building: b, warning: check.warning };
  }
  degree(id) {
    return this.links.filter((e) => e.a === id || e.b === id).length;
  }
  rebuildNetwork() {
    this.networkDirty = false;
    this.energyRoutes = new Map();
    const byId = new Map(this.buildings.map((b) => [b.id, b]));
    this.byId = byId;
    const degrees = new Map();
    const links = [];
    const insert = (a, b) => {
      if (
        (degrees.get(a.id) || 0) >= stats(a).maxLinks ||
        (degrees.get(b.id) || 0) >= stats(b).maxLinks
      )
        return;
      links.push({ a: a.id, b: b.id });
      degrees.set(a.id, (degrees.get(a.id) || 0) + 1);
      degrees.set(b.id, (degrees.get(b.id) || 0) + 1);
    };
    for (const edge of this.links) {
      const a = byId.get(edge.a),
        b = byId.get(edge.b);
      if (a && b && this.canLink(a, b)) insert(a, b);
    }
    const pairs = [];
    for (let i = 0; i < this.buildings.length; i++)
      for (let j = i + 1; j < this.buildings.length; j++) {
        const a = this.buildings[i],
          b = this.buildings[j];
        if (a.type === "station" || b.type === "station") continue;
        if (
          (!a.linkInitialized || !b.linkInitialized) &&
          !links.some(
            (l) =>
              (l.a === a.id && l.b === b.id) || (l.a === b.id && l.b === a.id),
          ) &&
          this.canLink(a, b)
        )
          pairs.push({ a, b, d: distance(a, b) });
      }
    pairs.sort((a, b) => a.d - b.d);
    for (const { a, b } of pairs) insert(a, b);
    this.links = links;
    this.adjacency = new Map(this.buildings.map((b) => [b.id, []]));
    for (const l of links) {
      this.adjacency.get(l.a).push(l.b);
      this.adjacency.get(l.b).push(l.a);
    }
    for (const b of this.buildings) b.linkInitialized = true;
    this.groups = [];
    const visited = new Set();
    for (const b of this.buildings) {
      if (visited.has(b.id) || b.type === "station") continue;
      const group = {
        members: [],
        energy: 0,
        capacity: 0,
        generation: 0,
        demand: 0,
      };
      const queue = [b];
      visited.add(b.id);
      while (queue.length) {
        const n = queue.pop();
        n.group = this.groups.length;
        group.members.push(n);
        const s = stats(n);
        n.maxHp = s.hp;
        group.capacity += s.capacity || 0;
        group.generation += n.construction >= 1 ? s.generation || 0 : 0;
        for (const e of links) {
          const id = e.a === n.id ? e.b : e.b === n.id ? e.a : null;
          if (id && !visited.has(id)) {
            visited.add(id);
            queue.push(byId.get(id));
          }
        }
      }
      const hasSupply = group.members.some(
        (n) => n.type === "solar" || n.type === "battery",
      );
      for (const n of group.members) n.connected = hasSupply;
      this.groups.push(group);
    }
  }
  upgradeCost(b, branch) {
    if (branch === "thel" && b.type === "laser" && b.level === 1)
      return BUILDINGS.thel.upgradeCosts?.[0] || 250;
    if (b.level >= BUILDINGS[b.type].levels) return Infinity;
    return (
      BUILDINGS[b.type].upgradeCosts?.[
        b.type === "thel" ? b.level : b.level - 1
      ] ?? Math.round(BUILDINGS[b.type].cost * (b.level === 1 ? 1.5 : 2))
    );
  }
  upgrade(id, branch = null) {
    const b = this.buildings.find((o) => o.id === id);
    if (!b) return { ok: false, reason: "Select a structure first" };
    if (b.construction < 1)
      return { ok: false, reason: "Wait for construction to finish" };
    if (
      branch === "thel" &&
      (!this.mission.thel || b.type !== "laser" || b.level !== 1)
    )
      return {
        ok: false,
        reason:
          "THEL requires a basic level-one laser and unlocked heavy weapons",
      };
    if (branch === "pulser" && (b.type !== "laser" || b.level !== 1))
      return {
        ok: false,
        reason:
          "P converts a basic level-one laser; use U or Space for further upgrades",
      };
    const cost = this.upgradeCost(b, branch);
    if (!Number.isFinite(cost)) return { ok: false, reason: "Fully upgraded" };
    if (this.minerals < cost)
      return { ok: false, reason: `Need ${cost} minerals` };
    this.minerals -= cost;
    this.spent += cost;
    b.investment += cost;
    b.upgradeSpent = (b.upgradeSpent || 0) + cost;
    const oldMax = b.maxHp;
    const oldLink = stats(b).link;
    if (branch === "thel") {
      b.type = "thel";
      b.level = 1;
    } else b.level++;
    const s = stats(b);
    b.maxHp = s.hp;
    b.hp = Math.min(s.hp, b.hp + s.hp - oldMax);
    if (s.link !== oldLink || b.type === "relay") b.linkInitialized = false;
    const more =
      b.type === "miner" || b.type === "laser"
        ? 5
        : b.type === "missile"
          ? 20
          : b.type === "thel" && b.level === 3
            ? 20
            : 10;
    b.constructionUnits = b.constructionTarget || 10;
    b.constructionTarget = (b.constructionTarget || 10) + more;
    b.construction = b.constructionUnits / b.constructionTarget;
    b.buildEnergy = 0;
    b.buildCooldown = 0;
    b.upgrading = true;
    this.networkDirty = true;
    this.emit("upgrade", { x: b.x, y: b.y });
    return { ok: true };
  }
  recycle(id) {
    const index = this.buildings.findIndex((b) => b.id === id);
    if (index < 0) return { ok: false, reason: "Select a structure first" };
    const b = this.buildings[index];
    if (b.type === "station")
      return {
        ok: false,
        reason: "Mission-critical station cannot be recycled",
      };
    let refund = Math.floor(
      (((b.baseCost ?? BUILDINGS[b.type].cost) +
        (b.upgradeSpent || 0) * this.rules.upgradeRefund) *
        b.hp) /
        b.maxHp,
    );
    this.buildings.splice(index, 1);
    if (b.type === "miner") {
      const exhausted = this.buildings.filter(
        (n) =>
          n.type === "miner" &&
          !this.asteroids.some(
            (a) => a.ore > 0 && distance(n, a) - a.radius <= stats(n).range,
          ),
      );
      for (const n of exhausted) {
        refund += Math.floor(
          (((n.baseCost ?? 45) +
            (n.upgradeSpent || 0) * this.rules.upgradeRefund) *
            n.hp) /
            n.maxHp,
        );
        this.buildings = this.buildings.filter((o) => o.id !== n.id);
      }
    }
    this.minerals += refund;
    this.networkDirty = true;
    this.emit("recycle", { x: b.x, y: b.y });
    return { ok: true, refund };
  }
  emit(type, data = {}) {
    this.events.push({ type, ...data });
    if (this.events.length > 60) this.events.shift();
  }
  effect(type, x, y, extra = {}) {
    this.effects.push({
      type,
      x,
      y,
      life: type === "explosion" ? 0.7 : 0.18,
      maxLife: type === "explosion" ? 0.7 : 0.18,
      ...extra,
    });
  }
  spawnEnemy(type, angle = null, rare = false) {
    const d = ENEMIES[type];
    const a = angle ?? this.random() * Math.PI * 2,
      r = this.mission.classic ? 2500 : this.mission.world * 0.5;
    const endurance =
      this.mission.kind === "endless"
        ? 1 + Math.max(0, this.wave - 5) * 0.1
        : 1;
    const e = {
      id: ++this.uid,
      type,
      x: Math.cos(a) * r,
      y: Math.sin(a) * r,
      hp: d.hp * this.diff.hp * endurance,
      maxHp: d.hp * this.diff.hp * endurance,
      shield: d.shield || 0,
      cooldown: this.random(),
      spawnCooldown: 8,
      angle: a + Math.PI,
      intelValue: !this.mission.classic
        ? type === "mothership"
          ? 3
          : rare
            ? 2
            : 0
        : 0,
    };
    if (rare && !this.mission.classic) {
      e.hp *= 1.6;
      e.maxHp = e.hp;
      e.rare = true;
    }
    this.enemies.push(e);
    return e;
  }
  callWave() {
    if (this.status !== "playing") return;
    this.wave++;
    this.waveAnnounce = 5;
    this.nextWave =
      this.time + Math.max(18, this.mission.waveGap - this.wave * 0.5);
    if (this.mission.classic) {
      const record = (this.mission.miningWaves ||
          this.mission.scheduledWaves)?.[this.wave - 1],
        types = [
          "",
          "fighter",
          "bomber",
          "suicide",
          "ring",
          "swarm",
          "mothership",
        ];
      this.spawnQueue ??= [];
      if (record) {
        this.waveRotation ??= Math.floor(this.random() * 360);
        const [, type, count, spread, hp, angle] = record;
        for (let i = 0; i < Math.ceil(count * this.diff.count); i++)
          this.spawnQueue.push({
            type: types[type],
            angle:
              ((angle +
                this.waveRotation +
                spread / 2 -
                Math.floor(this.random() * spread)) *
                Math.PI) /
              180,
            hp: hp || 1,
          });
        if (this.mission.scheduledWaves)
          this.nextWave =
            this.mission.scheduledWaves[this.wave]?.[0] ?? Infinity;
      } else if (this.mission.timedWaves) {
        const count = this.wave === 6 ? 10 : 5;
        for (let i = 0; i < count; i++)
          this.spawnQueue.push({
            type: "mothership",
            angle: this.random() * Math.PI * 2,
            hp: 2,
          });
        this.nextWave = this.mission.timedWaves[this.wave] ?? Infinity;
      } else {
        const a = this.random() * Math.PI * 2;
        for (let i = 0; i < 4 + this.wave * 2; i++)
          this.spawnEnemy(
            types[
              1 + ((i + this.wave) % Math.min(5, 1 + Math.floor(this.wave / 3)))
            ],
            a + (this.random() - 0.5) * 0.6,
          );
      }
      this.emit("wave", { wave: this.wave });
      return;
    }
    const tier = this.mission.enemyTier;
    const count = Math.min(
      100,
      Math.ceil(
        (2 + this.wave * (this.mission.swarm ? 2.8 : 1.3)) * this.diff.count,
      ),
    );
    const a = this.random() * Math.PI * 2;
    for (let i = 0; i < count; i++) {
      const type = this.mission.swarm
        ? "swarm"
        : tier >= 4 && i % 7 === 0
          ? "suicide"
          : tier >= 3 && i % 5 === 0
            ? "bomber"
            : tier >= 2 && i % 4 === 0
              ? "ring"
              : this.wave > 3 && i % 3 === 0
                ? "swarm"
                : "fighter";
      this.spawnEnemy(
        type,
        a + (this.random() - 0.5) * 0.5,
        i === 0 && this.wave % 3 === 0,
      );
    }
    if (this.mission.boss && this.wave === Math.min(3, this.mission.waves))
      for (let n = 0; n < (this.mission.bossCount || 1); n++)
        this.spawnEnemy("mothership", a + n * 0.8);
    if (this.mission.kind === "endless" && this.wave % 5 === 0)
      this.spawnEnemy("mothership", a);
    this.emit("wave", { wave: this.wave });
  }
  requestEnergy(consumer, amount, solarOnly = false) {
    if (!consumer || amount <= 0) return 0;
    const byId = this.byId || new Map(this.buildings.map((b) => [b.id, b]));
    // Routes depend on topology, not energy balances. Keep current supply and
    // construction checks below so caching never makes disconnected power usable.
    this.energyRoutes ??= new Map();
    let sources = this.energyRoutes.get(consumer.id);
    if (!sources) {
      let stable = true;
      const visited = new Set([consumer.id]);
      const queue = [{ node: consumer, path: [consumer.id] }];
      sources = [];
      for (let head = 0; head < queue.length; head++) {
        const { node, path } = queue[head];
        if (relays(node) && (node.constructionUnits ?? 10) < 10) stable = false;
        if (
          node.id !== consumer.id &&
          (node.type === "solar" || node.type === "battery")
        )
          sources.push({ node, path });
        if (
          node.id !== consumer.id &&
          (!relays(node) || (node.constructionUnits ?? 10) < 10)
        )
          continue;
        for (const id of this.adjacency.get(node.id) || [])
          if (!visited.has(id)) {
            visited.add(id);
            queue.push({ node: byId.get(id), path: [...path, id] });
          }
      }
      // Keep the original farthest-hop supplier priority and stable equal-hop order.
      sources.sort((a, b) => b.path.length - a.path.length);
      // An unfinished relay can begin forwarding within this same fixed step.
      // Revisit these temporary routes until construction makes them stable.
      if (stable) this.energyRoutes.set(consumer.id, sources);
    }
    let received = 0;
    for (const { node, path } of sources) {
      if (
        node.construction < 1 ||
        node.energy <= 0.00001 ||
        (solarOnly && node.type !== "solar")
      )
        continue;
      const taken = Math.min(node.energy, amount - received);
      if (taken <= 0) break;
      node.energy -= taken;
      received += taken;
      const existing = this.flows.find(
        (f) =>
          f.consumer === consumer.id && f.source === node.id && f.life > 0.12,
      );
      if (existing) {
        existing.amount += taken;
        existing.life = 0.28;
        existing.maxLife = 0.28;
      } else
        this.flows.push({
          consumer: consumer.id,
          source: node.id,
          path: [...path].reverse(),
          amount: taken,
          life: 0.28,
          maxLife: 0.28,
        });
      for (const id of path) {
        const b = byId.get(id);
        if (b) b.powerPulse = 1;
      }
      if (received >= amount - 0.00001) break;
    }
    return received;
  }
  useEnergy(consumer, amount) {
    if (!consumer || amount < 0) return false;
    if (amount === 0) return true;
    const capacity = stats(consumer).capacity || Math.max(1, amount);
    if (consumer.energy + 0.000001 < amount) {
      const request = Math.max(
        amount - consumer.energy,
        capacity - consumer.energy,
      );
      consumer.energy += this.requestEnergy(
        consumer,
        request,
        consumer.type === "battery",
      );
    }
    if (consumer.energy + 0.000001 < amount) return false;
    consumer.energy = Math.max(0, consumer.energy - amount);
    this.drawnThisTick = (this.drawnThisTick || 0) + amount;
    return true;
  }
  update(realDt) {
    if (this.paused || this.status !== "playing") return;
    this.accumulator =
      (this.accumulator || 0) + Math.max(0, Math.min(realDt, 0.1)) * this.speed;
    // Fixed simulation steps preserve burst cadence and economy at different display rates.
    while (this.accumulator >= 0.025 - 1e-9 && this.status === "playing") {
      this.accumulator -= 0.025;
      this.step(0.025);
    }
  }
  step(dt) {
    this.time += dt;
    this.waveAnnounce = Math.max(0, this.waveAnnounce - dt);
    if (this.networkDirty) this.rebuildNetwork();
    this.effects = this.effects.filter((e) => (e.life -= dt) > 0);
    const storm = this.mission.storm && this.time % 45 > 30;
    this.storm = storm;
    this.flows = this.flows.filter((f) => (f.life -= dt) > 0).slice(-160);
    this.drawnThisTick = 0;
    for (const b of this.buildings) {
      b.powerPulse = Math.max(0, (b.powerPulse || 0) - dt * 3);
      const st = stats(b);
      if (b.type === "solar" && b.construction >= 1) {
        b.generationCooldown = (b.generationCooldown ?? 0.55) - dt;
        if (b.generationCooldown <= 0) {
          b.generationCooldown += 0.55;
          b.energy = Math.min(
            st.capacity,
            b.energy +
              st.generation * 0.55 * (storm ? this.rules.stormOutput : 1),
          );
        }
      }
    }

    let minedTick = 0;
    for (const b of this.buildings) {
      const s = stats(b),
        g = this.groups[b.group];
      b.activity = Math.max(0, b.activity - dt * 2);
      b.shieldPulse = Math.max(0, (b.shieldPulse || 0) - dt * 3);
      b.powered =
        b.energy > 0.00001 ||
        (!!g &&
          g.members.some(
            (n) =>
              n.construction >= 1 &&
              ["solar", "battery"].includes(n.type) &&
              n.energy > 0.00001,
          ));
      b.cooldown -= dt;
      b.targetId = null;
      if (b.type === "station") continue;
      if (b.construction < 1) {
        b.buildCooldown -= dt;
        if (b.buildCooldown <= 0) {
          const interval =
            b.type === "miner" || b.type === "relay"
              ? 0.05
              : b.type === "laser"
                ? [0.4, 0.35, 0.3, 0.25][Math.min(b.level - 1, 3)]
                : b.type === "solar"
                  ? [0.5, 0.4, 0.3, 0.25, 0.2][Math.min(b.level - 1, 4)]
                  : b.type === "battery"
                    ? b.level === 1
                      ? 0.5
                      : 0.4
                    : b.type === "missile"
                      ? [0.75, 0.5, 0.25, 0.2][Math.min(b.level - 1, 3)]
                      : b.type === "repair"
                        ? b.level === 1
                          ? 0.75
                          : 0.65
                        : 0.4;
          b.buildCooldown = interval / this.rules.buildSpeed;
          if (b.type === "solar" && b.upgrading) b.buildEnergy = 1;
          else
            b.buildEnergy =
              (b.buildEnergy || 0) +
              this.requestEnergy(
                b,
                Math.max(0, 1 - (b.buildEnergy || 0)),
                b.type === "battery",
              );
          const threshold =
            b.type === "relay"
              ? 0.5
              : ["laser", "thel"].includes(b.type)
                ? 0.000001
                : 0.9999;
          if (b.buildEnergy >= threshold) {
            b.buildEnergy = 0;
            b.constructionUnits =
              (b.constructionUnits || 0) + (b.type === "relay" ? 2 : 1);
            b.construction = Math.min(
              1,
              b.constructionUnits / (b.constructionTarget || 10),
            );
            if (b.construction >= 1) {
              b.upgrading = false;
              b.energy = ["miner", "missile"].includes(b.type) ? 1 : b.energy;
              this.networkDirty = true;
            }
          }
        }
        continue;
      }
      if (!b.powered) continue;
      if (
        this.rules.regeneration &&
        b.hp < b.maxHp &&
        this.time - (b.lastDamaged ?? 0) >= 8
      ) {
        const heal = Math.min(b.maxHp - b.hp, b.maxHp * 0.01 * dt, 20 * dt);
        if (this.useEnergy(b, heal * 0.08)) {
          b.hp += heal;
          this.creditRepair(b, heal);
        }
      }
      if (b.type === "miner" && this.minersOn) {
        b.mineCooldown = (b.mineCooldown || 0) - dt;
        const targets = this.asteroids.filter(
          (a) => a.ore > 0 && distance(b, a) - a.radius <= s.range,
        );
        if (
          targets.length &&
          b.mineCooldown <= 0 &&
          this.useEnergy(b, s.miningEnergy || 1)
        ) {
          const target = targets[Math.floor(this.random() * targets.length)],
            mined = Math.min(target.ore, s.rate * 3);
          target.ore -= mined;
          this.minerals += mined;
          this.mined += mined;
          this.xpEarned += mined * XP_RATES.mining;
          minedTick += mined;
          b.mineCooldown = 3;
          b.targetId = target.id;
          b.miningTarget = target.id;
          b.activity = 1;
          b.angle = Math.atan2(target.y - b.y, target.x - b.x);
          if (target.ore <= 0) this.networkDirty = true;
        }
        if (b.activity > 0) b.targetId = b.miningTarget;
      }
      if (b.type === "repair") {
        b.droneCooldown -= dt;
        const count = this.drones.filter(
          (d) => d.homeId === b.id && d.hp > 0,
        ).length;
        if (count < 4 && b.droneCooldown <= 0) {
          b.droneCooldown = 0.5;
          b.droneCharge =
            (b.droneCharge || 0) +
            this.requestEnergy(b, Math.min(1, 10 - (b.droneCharge || 0)));
        }
        if (count < 4 && (b.droneCharge || 0) >= 9.999) {
          b.droneCharge = 0;
          this.drones.push({
            id: ++this.uid,
            homeId: b.id,
            x: b.x,
            y: b.y,
            energy: 80 * this.rules.droneCapacity,
            hp: 20,
            targetId: null,
            mode: "dock",
            returning: true,
            launchCooldown: 3,
          });
        }
      }
      if (
        ["laser", "thel", "missile"].includes(b.type) &&
        (b.type !== "missile" || this.missilesOn)
      ) {
        const candidates =
          b.type === "laser"
            ? [
                ...this.enemies,
                ...this.projectiles.filter(
                  (p) => !p.friendly && p.interceptable && p.life > 0,
                ),
              ]
            : this.enemies;
        const targets = candidates.filter(
          (e) =>
            (e.hp ?? 20) > 0 &&
            distance(b, e) <= s.range &&
            distance(b, e) >= (s.minRange || 0),
        );
        targets.sort((a, c) => distance(b, a) - distance(b, c));
        let target =
          targets.find((e) => e.id === b.retaliationId) || targets[0];
        if (b.type === "thel") {
          b.acquireCooldown = Math.max(0, (b.acquireCooldown || 0) - dt);
          if (b.acquireCooldown > 0) continue;
          if (b.beamTarget) {
            const held = targets.find((t) => t.id === b.beamTarget);
            if (held) target = held;
            else {
              b.beamTarget = null;
              b.beamTime = 0;
              b.acquireCooldown = 1;
              continue;
            }
          }
        }
        if (!target) {
          b.beamTime = 0;
          b.beamTarget = null;
        }
        if (target) {
          b.angle = Math.atan2(target.y - b.y, target.x - b.x);
          b.targetId = target.id;
          if (b.type === "thel") {
            b.beamTime = b.beamTarget === target.id ? b.beamTime + dt : 0;
            b.beamTarget = target.id;
            const damage =
              (s.damage + (b.beamTime * 20 + 1) / 4) *
              20 *
              dt *
              this.rules.thelDamage;
            if (this.useEnergy(b, damage * 0.05)) {
              this.damageEnemy(target, damage, true);
              b.activity = 1;
              if (b.cooldown <= 0) {
                this.effect("beam", b.x, b.y, {
                  toX: target.x,
                  toY: target.y,
                  color: "#9be9ff",
                  heavy: true,
                });
                b.cooldown = 0.08;
              }
            } else {
              b.beamTime = 0;
              b.beamTarget = null;
              b.acquireCooldown = 1;
            }
            continue;
          }
          if (b.type === "missile") {
            if (b.cooldown <= 0 && !b.salvoRemaining) {
              b.salvoRemaining = s.salvo || 1;
              b.salvoCooldown = 0;
              b.cooldown = s.interval;
            }
            b.salvoCooldown = (b.salvoCooldown || 0) - dt;
            if (
              b.salvoRemaining > 0 &&
              b.salvoCooldown <= 0 &&
              this.minerals >= 5 &&
              this.useEnergy(b, 1)
            ) {
              this.minerals -= 5;
              b.salvoRemaining--;
              b.salvoCooldown = 0.75;
              b.activity = 1;
              this.projectiles.push({
                id: ++this.uid,
                x: b.x,
                y: b.y,
                targetId: target.id,
                lastX: target.x,
                lastY: target.y,
                damage: s.damage,
                splash: s.splash,
                speed: 160 * this.rules.missileSpeed,
                life: 8,
                friendly: true,
                angle: b.angle,
              });
              this.emit("shot", { weapon: "missile" });
            }
          } else {
            if (b.cooldown <= 0) {
              b.burstRemaining = s.burst || 1;
              b.cooldown = s.interval;
              b.burstCooldown = 0;
            }
            b.burstCooldown = (b.burstCooldown || 0) - dt;
            if (
              b.burstRemaining > 0 &&
              b.burstCooldown <= 0 &&
              this.useEnergy(b, s.shotEnergy)
            ) {
              b.burstRemaining--;
              b.burstCooldown = 0.05;
              this.damageEnemy(target, s.damage);
              b.activity = 1;
              this.effect("beam", b.x, b.y, {
                toX: target.x,
                toY: target.y,
                color: "#fff097",
              });
              this.emit("shot", { weapon: "laser" });
            }
          }
        }
      }
    }
    for (const d of this.drones) {
      const home = this.buildings.find((b) => b.id === d.homeId);
      if (!home) {
        d.hp = 0;
        continue;
      }
      const range = stats(home).range,
        maxEnergy = 80 * this.rules.droneCapacity;
      if (d.hp <= 0) continue;
      d.launchCooldown = Math.max(0, (d.launchCooldown || 0) - dt);
      let target = this.buildings.find(
        (b) =>
          b.id === d.targetId && b.hp < b.maxHp && distance(home, b) <= range,
      );
      if (d.energy < 1) d.returning = true;
      if (d.returning && d.hp >= 60 && d.energy >= maxEnergy) {
        d.returning = false;
        d.launchCooldown = 3;
      }
      if (!target && !d.returning && d.energy > 1)
        target = this.buildings
          .filter((b) => b.hp < b.maxHp && distance(home, b) <= range)
          .sort((a, b) => b.maxHp - b.hp - (a.maxHp - a.hp))[0];
      if (d.returning || !target) {
        d.targetId = null;
        d.returning = true;
        const dist = distance(d, home);
        if (dist > 8) {
          const a = Math.atan2(home.y - d.y, home.x - d.x);
          d.x += Math.cos(a) * Math.min(dist, 36 * dt);
          d.y += Math.sin(a) * Math.min(dist, 36 * dt);
          d.mode = "return";
        } else {
          d.mode = "dock";
          d.serviceCooldown = (d.serviceCooldown || 0) - dt;
          if (d.serviceCooldown <= 0) {
            d.serviceCooldown = 0.05;
            if (home.construction >= 1 && d.hp < 60 && this.useEnergy(home, 1))
              d.hp = Math.min(60, d.hp + 3);
            if (
              home.construction >= 1 &&
              d.energy < maxEnergy &&
              this.useEnergy(home, 1)
            )
              d.energy = Math.min(maxEnergy, d.energy + 6);
          }
        }
      } else {
        d.targetId = target.id;
        const dist = distance(d, target);
        if (dist > 50) {
          const a = Math.atan2(target.y - d.y, target.x - d.x);
          d.x += Math.cos(a) * 36 * dt;
          d.y += Math.sin(a) * 36 * dt;
          d.mode = "travel";
        } else if (d.launchCooldown <= 0) {
          const heal = Math.min(
            target.maxHp - target.hp,
            d.energy,
            stats(home).rate * dt,
          );
          target.hp += heal;
          this.creditRepair(target, heal);
          d.energy -= heal;
          d.mode = "repair";
        }
      }
    }
    this.drones = this.drones.filter((d) => d.hp > 0);
    this.income +=
      (minedTick / Math.max(dt, 0.001) - this.income) * Math.min(1, dt * 0.35);
    for (const e of this.enemies) {
      if (e.hp <= 0) continue;
      const d = ENEMIES[e.type];
      e.cooldown -= dt;
      e.spawnCooldown -= dt;
      const targets = this.buildings.filter((b) => b.hp > 0);
      targets.sort((a, b) => distance(e, a) - distance(e, b));
      let target = targets[0];
      if (e.parentId) {
        const ordered = targets.find((b) => b.id === e.orderTarget);
        if (ordered) target = ordered;
      }
      if (!target) continue;
      const dist = distance(e, target);
      e.angle = Math.atan2(target.y - e.y, target.x - e.x);
      if (dist > d.range) {
        e.x += Math.cos(e.angle) * d.speed * dt;
        e.y += Math.sin(e.angle) * d.speed * dt;
      } else if (e.type === "suicide") {
        e.fuse = (e.fuse || 0) + dt;
        if (e.fuse > 3) {
          for (const b of this.buildings) {
            const dd = distance(target, b);
            if (dd < d.splash)
              this.damageBuilding(
                b,
                d.damage *
                  this.diff.damage *
                  (b.id === target.id ? 1 : 1 - dd / d.splash),
              );
          }
          this.effect("explosion", target.x, target.y, {
            size: 80,
            color: d.color,
          });
          e.hp = 0;
        }
      } else if (e.type === "bomber" && e.cooldown <= 0) {
        e.cooldown = d.interval;
        this.projectiles.push({
          id: ++this.uid,
          x: e.x,
          y: e.y,
          targetId: target.id,
          damage: d.damage * this.diff.damage,
          speed: 90,
          life: 10,
          friendly: false,
          interceptable: true,
          hp: 20,
          angle: e.angle,
        });
      } else if (e.type !== "bomber") {
        const dps =
          {
            fighter: 50,
            swarm: 100,
            ring: 12.5,
            mothership: 20,
            child: 20 / 3,
          }[e.type] || 15;
        this.damageBuilding(target, dps * this.diff.damage * dt);
        if (
          ["laser", "thel", "missile"].includes(target.type) &&
          stats(target).range >= d.range
        )
          target.retaliationId = e.id;
        if (e.cooldown <= 0) {
          e.cooldown = 0.12;
          this.effect("beam", e.x, e.y, {
            toX: target.x,
            toY: target.y,
            color: d.color,
          });
        }
      }
      if (e.type === "mothership" && !e.escortLaunched) {
        e.escortLaunched = true;
        for (let n = 0; n < 5; n++) {
          const baby = this.spawnEnemy("child");
          baby.x = e.x + (this.random() - 0.5) * 30;
          baby.y = e.y + (this.random() - 0.5) * 30;
          baby.parentId = e.id;
          baby.orderTarget = target.id;
        }
      }
      if (e.type === "mothership")
        for (const child of this.enemies)
          if (child.parentId === e.id) child.orderTarget = target.id;
    }
    for (const p of this.projectiles) {
      if (p.life <= 0) continue;
      if (p.delay > 0) {
        p.delay -= dt;
        continue;
      }
      p.life -= dt;
      const targets = p.friendly ? this.enemies : this.buildings;
      let target = targets.find((t) => t.id === p.targetId && t.hp > 0);
      if (!target && p.friendly) {
        target = targets
          .filter((t) => t.hp > 0)
          .sort((a, b) => distance(p, a) - distance(p, b))[0];
        if (target) p.targetId = target.id;
      }
      if (!target) {
        p.life = 0;
        continue;
      }
      const dist = distance(p, target);
      p.angle = Math.atan2(target.y - p.y, target.x - p.x);
      if (dist < p.speed * dt + 5) {
        if (p.splash) {
          for (const t of targets) {
            const falloff = 1 - distance(t, target) / p.splash;
            if (falloff > 0)
              this.damageEnemy(
                t,
                (p.damage * falloff) / (target.type === "ring" ? 15 : 1),
                true,
              );
          }
          this.effect("explosion", target.x, target.y, {
            size: p.splash * 0.6,
            color: "#e5b0ed",
          });
        } else {
          this.damageBuilding(target, p.damage);
          this.effect("hit", target.x, target.y, { color: "#fa8b77" });
        }
        p.life = 0;
      } else {
        p.x += Math.cos(p.angle) * p.speed * dt;
        p.y += Math.sin(p.angle) * p.speed * dt;
      }
    }
    this.projectiles = this.projectiles.filter((p) => p.life > 0).slice(-1200);
    const deadParents = new Set(
      this.enemies
        .filter((e) => e.type === "mothership" && e.hp <= 0)
        .map((e) => e.id),
    );
    for (const e of this.enemies) if (deadParents.has(e.parentId)) e.hp = 0;
    for (const e of this.enemies.filter((e) => e.hp <= 0)) {
      this.kills++;
      if (
        e.defeatedByPlayer ||
        this.enemies.some(
          (parent) =>
            parent.id === e.parentId &&
            deadParents.has(parent.id) &&
            parent.defeatedByPlayer,
        )
      )
        this.combatKills++;
      if (e.type === "mothership") this.bossKills++;
      if (e.defeatedByPlayer && e.intelValue) {
        this.intelCollected += e.intelValue;
        this.effect("intel", e.x, e.y, {
          value: e.intelValue,
          life: 1.6,
          maxLife: 1.6,
        });
      }
      this.effect("explosion", e.x, e.y, {
        size: ENEMIES[e.type].radius * 3,
        color: ENEMIES[e.type].color,
      });
      this.emit("explosion", { size: ENEMIES[e.type].radius });
    }
    this.enemies = this.enemies.filter((e) => e.hp > 0);
    for (const b of this.buildings.filter((b) => b.hp <= 0)) {
      this.lost++;
      this.networkDirty = true;
      this.effect("explosion", b.x, b.y, { size: 45, color: "#8edbcc" });
      this.emit("lost", { name: BUILDINGS[b.type].name });
      if (b.type === "station") this.finish("lost");
    }
    this.buildings = this.buildings.filter((b) => b.hp > 0);
    this.energy = 0;
    this.capacity = 0;
    this.generation = 0;
    this.consumption = 0;
    // Stores recharge from solar stations only, after active consumers have requested power.
    for (const b of this.buildings)
      if (b.type === "battery" && b.construction >= 1) {
        b.chargeCooldown = (b.chargeCooldown ?? 1.05) - dt;
        if (b.chargeCooldown <= 0) {
          b.chargeCooldown += 1.05;
          const cap = stats(b).capacity;
          if (b.energy < cap)
            b.energy += this.requestEnergy(b, cap - b.energy, true);
        }
      }
    for (const b of this.buildings) {
      const st = stats(b);
      this.energy += b.energy;
      this.capacity += st.capacity || 0;
      if (b.construction >= 1)
        this.generation +=
          (st.generation || 0) * (storm ? this.rules.stormOutput : 1);
    }
    this.consumption = this.drawnThisTick / Math.max(dt, 0.001);
    if (!this.mission.sandbox && this.wave < this.mission.waves) {
      if (this.mission.miningWaves) {
        const threshold = this.mission.miningWaves[this.wave]?.[0];
        if ((this.mined / this.mission.goal) * 100 >= threshold)
          this.callWave();
      } else if (this.time >= this.nextWave) this.callWave();
    }
    if (this.spawnQueue?.length) {
      const queued = this.spawnQueue.shift(),
        enemy = this.spawnEnemy(queued.type, queued.angle);
      enemy.hp *= queued.hp;
      enemy.maxHp = enemy.hp;
    }
    if (this.wave > 0 && this.enemies.length === 0 && !this.spawnQueue?.length)
      this.clearedWave = this.wave;
    if (!this.buildings.length) this.finish("lost");
    const recoverable =
      this.buildings.some(
        (b) => b.type === "solar" && (b.construction >= 1 || b.upgrading),
      ) || this.energy > 1;
    this.lowPowerTime = recoverable ? 0 : this.lowPowerTime + dt;
    if (this.lowPowerTime > 12 && !this.mission.sandbox) this.finish("lost");
    const m = this.mission;
    const station = this.buildings.find((b) => b.type === "station");
    if (m.kind === "mine" && this.mined >= m.goal) this.finish("won");
    if (
      (m.kind === "survive" || m.kind === "defend") &&
      this.time >= m.goal &&
      this.enemies.length === 0 &&
      !this.spawnQueue?.length
    )
      this.finish("won");
    if (
      m.kind === "boss" &&
      this.bossKills >= m.goal &&
      this.enemies.length === 0
    )
      this.finish("won");
    if (m.kind === "repair" && station && station.hp / station.maxHp >= m.goal)
      this.finish("won");
  }
  damageBuilding(target, amount) {
    if (target.type !== "station") amount *= 1 - this.rules.armor;
    if (
      this.rules.shield &&
      target.type !== "station" &&
      target.construction >= 1
    ) {
      const absorbed = amount * this.rules.shield;
      if (this.useEnergy(target, absorbed * 0.1)) {
        amount -= absorbed;
        target.shieldPulse = 1;
      }
    }
    target.repairXpDebt =
      (target.repairXpDebt || 0) + Math.min(Math.max(0, target.hp), amount);
    target.hp -= amount;
    target.lastDamaged = this.time;
  }
  damageEnemy(target, amount, pierce = false) {
    const wasAlive = target.hp > 0;
    if (!pierce && target.shield > 0) {
      const absorbed = Math.min(target.shield, amount);
      target.shield -= absorbed;
      amount -= absorbed;
    }
    if (!target.interceptable)
      this.xpEarned +=
        Math.min(Math.max(0, target.hp || 0), Math.max(0, amount)) *
        XP_RATES.combat;
    target.hp = (target.hp ?? 20) - amount;
    if (wasAlive && target.hp <= 0) target.defeatedByPlayer = true;
    if (target.interceptable && target.hp <= 0) target.life = 0;
  }
  creditRepair(target, amount) {
    const eligible = Math.min(target.repairXpDebt || 0, amount);
    target.repairXpDebt = Math.max(0, (target.repairXpDebt || 0) - eligible);
    this.xpEarned += eligible * XP_RATES.repair;
  }
  finish(status) {
    if (this.status !== "playing") return;
    this.status = status;
    this.emit(status);
  }
  objectiveProgress() {
    const m = this.mission;
    if (m.kind === "mine") return Math.min(1, this.mined / m.goal);
    if (m.kind === "survive" || m.kind === "defend")
      return Math.min(1, this.time / m.goal);
    if (m.kind === "boss") return Math.min(1, this.bossKills / m.goal);
    if (m.kind === "repair") {
      const b = this.buildings.find((n) => n.type === "station");
      return b ? Math.min(1, b.hp / b.maxHp / m.goal) : 0;
    }
    return 0;
  }
  snapshot() {
    return JSON.parse(
      JSON.stringify({
        missionId: this.mission.id,
        researchIds: this.researchIds,
        statRanks: this.statRanks,
        intelCollected: this.intelCollected,
        xpEarned: this.xpEarned,
        xpCredit: this.xpCredit,
        combatKills: this.combatKills,
        intelCredit: this.intelCredit,
        clearedWave: this.clearedWave || 0,
        mission:
          this.mission.id === "skirmish"
            ? { ...this.mission, waves: null }
            : undefined,
        difficulty: this.difficulty,
        buildings: this.buildings,
        asteroids: this.asteroids,
        enemies: this.enemies,
        projectiles: this.projectiles,
        drones: this.drones,
        spawnQueue: this.spawnQueue || [],
        waveRotation: this.waveRotation,
        randomState: this.random.state(),
        accumulator: this.accumulator || 0,
        links: this.links,
        uid: this.uid,
        time: this.time,
        wave: this.wave,
        nextWave: this.nextWave,
        minerals: this.minerals,
        mined: this.mined,
        kills: this.kills,
        bossKills: this.bossKills,
        lost: this.lost,
        spent: this.spent,
        minersOn: this.minersOn,
        missilesOn: this.missilesOn,
        status: this.status,
      }),
    );
  }
  restore(s) {
    for (const key of [
      "clearedWave",
      "combatKills",
      "intelCredit",
      "intelCollected",
      "xpEarned",
      "xpCredit",
      "buildings",
      "asteroids",
      "enemies",
      "projectiles",
      "drones",
      "links",
      "spawnQueue",
      "waveRotation",
      "accumulator",
      "uid",
      "time",
      "wave",
      "nextWave",
      "minerals",
      "mined",
      "kills",
      "bossKills",
      "lost",
      "spent",
      "minersOn",
      "missilesOn",
      "status",
    ])
      if (s[key] !== undefined) this[key] = s[key];
    // Legacy snapshots start tracking from their current extraction total.
    if (!Number.isFinite(s.intelCredit?.rare))
      this.intelCredit = { rare: this.intelCollected, earned: 0 };
    // Legacy operations start XP tracking now; do not re-credit historic activity.
    if (!Number.isFinite(s.xpCredit)) this.xpCredit = this.xpEarned;
    for (const b of this.buildings) {
      b.research = this.rules;
      b.construction ??= 1;
      b.constructionUnits ??= b.construction * 10;
      b.constructionTarget ??= 10;
      b.buildCooldown ??= 0;
      b.buildEnergy ??= 0;
      b.baseCost ??= BUILDINGS[b.type].cost;
      b.upgradeSpent ??= Math.max(0, b.investment - b.baseCost);
      b.beamTime ??= 0;
      if (b.type === "station") b.repairXpDebt ??= b.maxHp - b.hp;
    }
    if (s.randomState !== undefined) this.random.restore(s.randomState);
    if (this.mission.classic && this.mission.kind === "mine")
      this.mission = {
        ...this.mission,
        goal: this.asteroids.reduce((v, a) => v + a.maxOre, 0) * 0.5,
      };
    this.networkDirty = true;
    this.rebuildNetwork();
  }
}
