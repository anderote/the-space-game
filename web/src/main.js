import "./style.css";
import {
  BUILDINGS,
  BUILD_ORDER,
  CAMPAIGN,
  CLASSIC,
  CHALLENGES,
  DIFFICULTIES,
  UPGRADES,
  skirmish,
} from "./content.js";
import { Simulation, stats, distance } from "./engine.js";
import { solarPetals } from "./structure-upgrades.js";
import { SpaceRenderer } from "./renderer.js";
import {
  freshProgress,
  normalizeSettings,
  loadProgress,
  saveProgress,
  starsTotal,
  isUnlocked,
  recordVictory,
  bankIntel,
  bankExperience,
  migrateProgression,
  resetProgress,
} from "./storage.js";
import { Sound } from "./audio.js";
import {
  TECHNOLOGIES,
  researchBudget,
  buyResearch,
  resetResearch,
  researchLoadout,
  normalizeResearch,
} from "./research.js";
import {
  experienceBudget,
  masteryBudget,
  buyBaseStat,
  buyTowerSkill,
} from "./experience.js";
import { researchView } from "./research-view.js";
const app = document.querySelector("#app");
const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const fmt = (n) => Math.floor(n).toLocaleString("en-US");
const clock = (s) =>
  `${Math.floor(Math.max(0, s) / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(Math.max(0, s) % 60)
    .toString()
    .padStart(2, "0")}`;
const icon = (type, size = 32) => {
  const paths = {
    relay:
      '<circle cx="16" cy="16" r="3"/><path d="m14 14-9-9m14 9 8-9m-11 14v9"/><circle cx="4" cy="4" r="2"/><circle cx="28" cy="4" r="2"/><circle cx="16" cy="29" r="2"/>',
    miner:
      '<circle cx="15" cy="17" r="7"/><circle cx="15" cy="17" r="3"/><path d="m21 12 8-7M24 5l3 3m-15 17-3 4m10-4 3 4"/>',
    solar:
      '<rect x="2" y="7" width="10" height="18" rx="1"/><rect x="20" y="7" width="10" height="18" rx="1"/><path d="M12 16h8M7 7v18m18-18v18M2 13h10m8 0h10M2 19h10m8 0h10"/><circle cx="16" cy="16" r="3"/>',
    battery:
      '<rect x="5" y="5" width="9" height="23" rx="3"/><rect x="18" y="5" width="9" height="23" rx="3"/><path d="M8 11h3m10 0h3M8 16h3m10 0h3M8 21h3m10 0h3"/>',
    repair:
      '<circle cx="16" cy="16" r="5"/><circle cx="6" cy="6" r="4"/><circle cx="26" cy="6" r="4"/><circle cx="6" cy="26" r="4"/><circle cx="26" cy="26" r="4"/><path d="m9 9 4 4m6 6 4 4m-4-6 4-4m-10 10-4 4"/>',
    laser:
      '<path d="m16 3 12 7v13l-12 7-12-7V10Z"/><path d="m16 10 6 6-6 6-6-6Z"/>',
    missile: '<path d="m16 2 14 10-5 17H7L2 12Z"/><path d="m16 9 6 12H10Z"/>',
    thel: '<path d="m16 3 12 7v13l-12 7-12-7V10Z"/><path d="M11 9v14m10-14v14M7 16h18"/>',
    mark: '<path d="M16 2 29 9v15l-13 7-13-7V9Z"/><path d="m16 8 8 15H8Z"/><circle cx="16" cy="18" r="2"/>',
    station:
      '<circle cx="16" cy="16" r="10"/><circle cx="16" cy="16" r="4"/><path d="M16 1v7m0 16v7M1 16h7m16 0h7"/>',
  };
  return `<svg width="${size}" height="${size}" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[type] || paths.mark}</svg>`;
};
const brand = () =>
  `<span class="brand-mark">${icon("mark")}<strong>THE SPACE GAME</strong></span>`;
let progress = loadProgress(),
  screen = "home",
  tab = "campaign",
  selectedMission = 0,
  sim = null,
  demo = null,
  renderer;
let state = { selected: null, buildType: null, mouse: null, grid: false };
let uiTick = 0,
  saveTick = 0,
  last = performance.now(),
  modalOpen = false,
  pausedBeforeModal = false,
  toastTimer = null,
  pointer = null,
  keys = new Set(),
  resultHandled = false;
let selectedTech = "solar_cells",
  progressionPage = "tech",
  selectedTower = "laser",
  researchReturn = "home",
  pausedBeforeResearch = false;
const sound = new Sound();
try {
  renderer = new SpaceRenderer(
    document.querySelector("#scene"),
    document.querySelector("#overlay"),
  );
} catch (error) {
  app.innerHTML = `<div class="fatal"><div><div class="eyebrow">THE SPACE GAME</div><h1>Your graphics engine is unavailable.</h1><p>This game needs WebGL 2. Enable hardware acceleration in your browser, then reload the page.</p><p>${esc(error.message)}</p><button class="primary" onclick="location.reload()">Try again</button></div></div>`;
  throw error;
}
function applySettings() {
  sound.enabled = progress.settings.sound;
  const qualityChanged = renderer.quality !== progress.settings.quality;
  renderer.quality = progress.settings.quality;
  if (qualityChanged) renderer.resize();
  renderer.reducedMotion = progress.settings.reducedMotion;
  renderer.accent =
    UPGRADES.find((u) => u.id === progress.livery)?.color || "#87ebcc";
  document.documentElement.style.setProperty("--mint", renderer.accent);
}
applySettings();
function demoScene() {
  const m = skirmish(9374, "sandbox");
  m.asteroids = 34;
  demo = new Simulation(m);
  demo.buildings = [];
  demo.links = [];
  for (const [t, x, y, l] of [
    ["solar", 0, 0, 2],
    ["relay", 65, 0, 1],
    ["relay", 105, -65, 1],
    ["relay", 35, -90, 1],
    ["relay", -40, -62, 1],
    ["relay", -65, 45, 1],
    ["solar", -45, 108, 1],
    ["battery", 80, 65, 1],
    ["laser", 140, -15, 2],
    ["laser", 90, -120, 3],
    ["laser", -112, 22, 2],
    ["missile", -40, -115, 1],
    ["repair", 5, 60, 1],
    ["miner", 43, 53, 2],
    ["miner", 155, -78, 2],
    ["thel", -100, 95, 1],
  ]) {
    const b = demo.addBuilding(t, x, y, true);
    b.level = l;
  }
  demo.rebuildNetwork();
  for (const b of demo.buildings) b.powered = true;
  renderer.cameraX = -160;
  renderer.cameraY = 5;
  renderer.zoom = Math.max(1.25, Math.min(2.15, innerHeight / 410));
  renderer.updateCamera();
}
function home() {
  screen = "home";
  modalOpen = false;
  state = { selected: null, buildType: null, mouse: null, grid: false };
  if (sim?.status === "playing") {
    saveActive();
    sim.paused = true;
  }
  demoScene();
  app.innerHTML = `<main class="home"><header class="home-top">${brand()}<span class="connection"><i class="status-dot"></i> NETWORK ONLINE <span style="color:#46606b">/</span> BROWSER EDITION</span></header><div class="home-content"><div class="eyebrow">MINE. CONNECT. DEFEND.</div><h1>THE SPACE<br><span>GAME</span></h1><p class="intro">A foothold in an endless frontier.<br>Build your network. Harvest the belt.<br>Keep the lights on.</p>${progress.active ? `<button class="secondary home-continue" data-action="continue">↳ Resume operation <span style="float:right">${clock(progress.active.time)}</span></button>` : ""}<button class="primary" data-action="campaign">Begin expedition <span>↗</span></button><div class="home-actions"><button class="secondary" data-action="challenges">Challenges</button><button class="secondary" data-action="freeplay">Free play</button></div><button class="secondary home-research" data-action="research"><span>Research division ↗</span><span>${researchBudget(progress).available} INTEL</span></button><div class="home-rule"></div><div class="home-caption">12 NEW SECTORS · 6 CHALLENGES · <button class="link-button" data-action="classic">9 CLASSIC MISSIONS</button></div><p class="touch-note">Best experienced with a mouse and keyboard.</p></div><div class="sector-tag"><div class="eyebrow">LIVE ORBITAL FEED</div><h2>Ceres mining outpost</h2><p>SECTOR 01 / 2.77 AU / SOL SYSTEM</p></div><div class="home-stats"><div><strong>07</strong><span>CORE STRUCTURES</span></div><div><strong>04</strong><span>DIFFICULTY LEVELS</span></div><div><strong>∞</strong><span>POSSIBILITIES</span></div></div><footer class="home-bottom"><span>A new browser recreation of the 2009 game by<br>David Scott &amp; Casual Collective.</span><span><button class="link-button" data-action="controls">Flight manual</button> &nbsp; / &nbsp; <button class="link-button" data-action="settings">Settings</button> &nbsp; / &nbsp; <button class="link-button" data-action="credits">Origins &amp; credits</button></span></footer></main>`;
}
function missionGoal(m) {
  if (m.kind === "mine")
    return m.classic
      ? "Mine 50% of the asteroid field"
      : `Extract ${fmt(m.goal)} minerals`;
  if (m.kind === "survive")
    return `Survive ${clock(m.goal)} and clear the sector`;
  if (m.kind === "defend") return `Protect the station for ${clock(m.goal)}`;
  if (m.kind === "repair")
    return `Restore the station to ${Math.round(m.goal * 100)}% hull`;
  if (m.kind === "boss")
    return `Destroy ${m.goal} mothership${m.goal > 1 ? "s" : ""} and their escorts`;
  return "Build your own story";
}
function researchScreen() {
  const scroll = document.querySelector(".research-body")?.scrollTop || 0;
  screen = "research";
  modalOpen = false;
  keys.clear();
  app.innerHTML = researchView(progress, selectedTech, icon, {
    page: progressionPage,
    tower: selectedTower,
    inGame: researchReturn === "game",
    mission: researchReturn === "game" ? sim.mission : null,
  });
  document.querySelector(".research-body").scrollTop = scroll;
}
function runResearch() {
  if (sim.mission.classic) {
    if (modalOpen) closeModal();
    openModal(
      `<div class="eyebrow">CLASSIC OPERATION</div><h2>Original rules.</h2><p>Classic scenarios use the original mission rules with the expanded building upgrades. They do not earn Intel. Live research is available in modern operations.</p><button class="primary" data-action="close">Return to operation</button>`,
    );
    return;
  }
  pausedBeforeResearch = modalOpen ? pausedBeforeModal : sim.paused;
  saveActive();
  sim.paused = true;
  researchReturn = "game";
  // Show the deployed configuration. A Command respec may have removed owned IDs.
  progress.research = normalizeResearch({
    ...progress.research,
    active: sim.researchIds,
  });
  saveResearchChanges();
  researchScreen();
}
function leaveResearch() {
  if (researchReturn !== "game") {
    researchReturn === "home" ? home() : selector(researchReturn);
    return;
  }
  screen = "game";
  modalOpen = false;
  sim.paused = pausedBeforeResearch;
  keys.clear();
  renderHud();
  document.querySelector('[data-action="run-research"]')?.focus();
}
function saveResearchChanges() {
  if (researchReturn === "game") {
    sim.setResearchLoadout(
      researchLoadout(progress, sim.mission),
      progress.experience.ranks,
      progress.experience.towers,
    );
    saveActive();
  } else saveProgress(progress);
}
function selector(which = "campaign", selection = null) {
  if (which === "research") {
    researchReturn = "campaign";
    researchScreen();
    return;
  }
  screen = "select";
  tab = which;
  modalOpen = false;
  if (selection !== null) selectedMission = selection;
  else if (which === "campaign")
    selectedMission = Math.min(11, Object.keys(progress.completed).length);
  else selectedMission = 0;
  let body = "";
  const total = starsTotal(progress);
  if (which === "campaign" || which === "classic" || which === "challenges") {
    const list =
      which === "campaign"
        ? CAMPAIGN
        : which === "classic"
          ? CLASSIC
          : CHALLENGES;
    selectedMission = Math.min(selectedMission, list.length - 1);
    const m = list[selectedMission];
    const allowed =
      which === "campaign" ? isUnlocked(progress, selectedMission) : true;
    body = `<div class="mission-layout"><div class="mission-list">${list
      .map((mission, i) => {
        const open = which !== "campaign" || isUnlocked(progress, i);
        const saved = (
          which === "campaign" ? progress.completed : progress.challenges
        )[mission.id];
        return `<button class="mission-card ${i === selectedMission ? "selected" : ""} ${!open ? "locked" : ""}" data-mission="${i}" aria-label="${esc(mission.name)}${open ? "" : " — locked"}" aria-pressed="${i === selectedMission}"><span class="index">${String(i + 1).padStart(2, "0")} / ${which === "campaign" ? ["INNER BELT", "OUTER BELT", "THE RIFT", "FAR REACH"][Math.floor(i / 3)] : "CHALLENGE"}</span>${!open ? '<span class="lock">◇</span>' : ""}<strong>${esc(mission.name)}</strong><span class="stars">${saved ? "★".repeat(saved.stars) + "☆".repeat(3 - saved.stars) : open ? "○ ○ ○" : "—"}</span></button>`;
      })
      .join(
        "",
      )}</div><aside class="briefing"><div class="eyebrow">${esc(m.sector)}</div><h3>${esc(m.name)}</h3><p>${esc(m.brief)}</p><div class="objective-label"><span class="small-label">PRIMARY OBJECTIVE</span><br>${esc(missionGoal(m))}</div><div class="research-summary">${m.classic ? "CLASSIC SCENARIO · EXPANDED UPGRADES · RESEARCH DISABLED" : researchLoadout(progress, m).length + " TECHNOLOGIES ACTIVE · COMMAND LEVEL " + experienceBudget(progress).level}</div><label class="field-label">DIFFICULTY<select id="difficulty">${Object.entries(
      DIFFICULTIES,
    )
      .map(
        ([key, d]) =>
          `<option value="${key}" ${progress.settings.difficulty === key ? "selected" : ""}>${d.name}</option>`,
      )
      .join(
        "",
      )}</select></label><p style="font-size:10px">${which === "campaign" ? "Complete a sector to open the next. New structures become available as you progress." : which === "classic" ? "Original budgets, objectives, structure access, and mining-triggered waves. Maps and some combat timing are recreated." : "Standalone scenarios. All challenges are available from the start."}</p><button class="primary" data-action="launch" ${!allowed ? "disabled" : ""}>${allowed ? "Enter sector" : "Complete the previous sector"} <span>↗</span></button></aside></div>`;
  } else if (which === "freeplay") {
    body = `<div class="sandbox-panel"><div class="mode-card"><div class="eyebrow">SURVIVAL / NO TIME LIMIT</div><h3>Endless frontier</h3><div class="eyebrow">PERSONAL BEST / WAVE ${progress.endless?.wave || 0}</div><p>An open field, every structure, and ever larger fleets. A mothership arrives every fifth wave. Build a network that lasts.</p><label class="field-label">SECTOR SEED<input id="endless-seed" type="number" min="1" max="999999" value="4281" /></label><button class="primary" data-mode="endless">Enter the frontier <span>↗</span></button></div><div class="mode-card"><div class="eyebrow">CREATIVE / NO PRESSURE</div><h3>Sandbox</h3><p>A generous mineral reserve and no automatic attacks. Experiment with layouts and call in fleets when ready.</p><label class="field-label">SECTOR SEED<input id="sandbox-seed" type="number" min="1" max="999999" value="8107" /></label><button class="primary" data-mode="sandbox">Create an outpost <span>↗</span></button></div></div>`;
  } else {
    body = `<div class="livery-list">${UPGRADES.map((u) => `<button class="livery ${u.id === progress.livery ? "selected" : ""}" data-livery="${u.id}" ${total < u.need ? "disabled" : ""}><div class="eyebrow">${total >= u.need ? "UNLOCKED" : u.need + " STARS"}</div><div style="color:${u.color}">${icon("mark", 70)}</div><strong>${u.name}</strong><p>${u.description}</p></button>`).join("")}</div>`;
  }
  app.innerHTML = `<div class="screen-shade"><section class="command-window"><header class="window-top"><div><div class="eyebrow">EXPEDITION COMMAND</div><h2>${{ campaign: "Choose your next orbit", classic: "The original nine missions", challenges: "Proving grounds", freeplay: "Beyond the charted belt", unlocks: "Your expedition, your colors" }[which]}</h2></div><nav class="window-tabs">${[
    ["campaign", "Expedition"],
    ["classic", "Classic"],
    ["challenges", "Challenges"],
    ["freeplay", "Free play"],
    ["unlocks", "Unlocks"],
    ["research", "Research"],
  ]
    .map(
      ([t, label]) =>
        `<button class="tab ${t === which ? "active" : ""}" data-tab="${t}">${label}</button>`,
    )
    .join(
      "",
    )}<button class="quiet" data-action="home" aria-label="Close mission select">×</button></nav></header>${body}<footer class="window-footer"><span>★ ${total} / 36 EXPEDITION STARS</span><span>1 star: complete · 2: no structures lost · 3: beat the target time</span></footer></section></div>`;
}
function launch(m, snapshot = null) {
  sim = new Simulation(
    m,
    snapshot?.difficulty || progress.settings.difficulty,
    snapshot,
    researchLoadout(progress, m),
    progress.experience.ranks,
    progress.experience.towers,
  );
  sim.setResearchLoadout(
    researchLoadout(progress, m),
    progress.experience.ranks,
    progress.experience.towers,
  );
  sim.paused = false;
  resultHandled = false;
  screen = "game";
  modalOpen = false;
  state = { selected: null, buildType: null, mouse: null, grid: false };
  renderer.center();
  renderHud();
  saveActive();
  sound.play("build");
}
function renderHud() {
  app.innerHTML = `<div class="hud"><header class="hud-top"><div class="hud-logo">${brand()}<div class="mission-name">${esc(sim.mission.name)} / ${DIFFICULTIES[sim.difficulty].name}</div></div><div class="resource-group"><div class="resource minerals"><div class="small-label">MINERALS</div><strong id="minerals">0</strong><span class="unit">M</span><div class="rate" id="income">+0 / MIN</div></div><div class="resource"><div class="small-label">ENERGY RESERVE</div><strong id="energy">0</strong><span class="unit" id="capacity">/ 0</span><div class="power-meter"><i id="power-bar" style="width:0%"></i></div></div><div class="resource"><div class="small-label">POWER BALANCE</div><strong id="balance">0</strong><span class="unit">E/S</span><div class="rate" id="power-rate">GENERATED / CONSUMED</div></div></div><div class="hud-controls"><button class="speed-btn" data-action="pause" title="Pause simulation; building remains available" aria-label="Pause">Ⅱ</button><button class="speed-btn" data-speed="0.5">½×</button><button class="speed-btn active" data-speed="1">1×</button><button class="speed-btn" data-speed="2">2×</button><button class="icon-btn" data-action="controls" title="Keyboard controls" aria-label="Controls">?</button><button class="icon-btn intel-button" data-action="run-research" aria-label="Research tree" title="Research tree · I"><span>◈ <b id="intel-count">0</b></span><small id="xp-hud">INTEL · I</small></button><button class="icon-btn" data-action="menu" title="Mission menu" aria-label="Mission menu">☰</button></div></header><section class="objective-panel"><div class="eyebrow">${sim.mission.id === "skirmish" ? "OPEN OPERATION" : "MISSION OBJECTIVE"}</div><h3>${esc(sim.mission.name)}</h3><div class="objective-value" id="objective-text"></div><div class="progress-track"><i id="objective-progress" style="width:0%"></i></div><p>${esc(sim.mission.tip)}</p></section><div class="radar-panel"><div class="small-label" id="contact-label">NEXT CONTACT</div><div class="contact-time" id="contact-time"></div><div class="enemy-count" id="enemy-count"></div><div class="time-label" id="elapsed"></div></div><div class="status-strip" id="status-strip"></div><div class="minimap-wrap"><div class="small-label"><span>SECTOR MAP</span><span id="zoom-label">100%</span></div><canvas id="minimap" width="292" height="180" aria-label="Minimap: click to move camera"></canvas></div><div class="bottom-dock"><div class="dock-title"><span>CONSTRUCTION / 1–7</span><span>SHIFT + CLICK TO REPEAT · R TO RECYCLE</span></div><div class="build-deck">${BUILD_ORDER.map((t) => `<button class="build-card" data-build="${t}" title="${BUILDINGS[t].key} · ${BUILDINGS[t].name} · ${BUILDINGS[t].description}" aria-label="Build ${BUILDINGS[t].name}"><span class="shortcut">${BUILDINGS[t].key}</span><span class="cost">${sim.buildingCost(t)}</span>${icon(t)}<span class="name">${BUILDINGS[t].name}</span></button>`).join("")}</div></div><div class="network-toggles"><button class="quiet" data-action="miners" id="miners-toggle">Miners on</button><button class="quiet" data-action="missiles" id="missiles-toggle">Missiles on</button><button class="quiet" data-action="grid" title="Toggle placement grid">Grid</button></div><aside class="inspector" id="inspector"></aside><div class="tutorial-tip" id="tutorial-tip">Select a structure to inspect it. Drag the field to pan. Scroll to zoom.</div></div>`;
  document.querySelector("#minimap").addEventListener("pointerdown", (e) => {
    const r = e.currentTarget.getBoundingClientRect(),
      scale = sim.mission.world * 1.25;
    renderer.cameraX = ((e.clientX - r.left - r.width / 2) / r.height) * scale;
    renderer.cameraY = (-(e.clientY - r.top - r.height / 2) / r.height) * scale;
    renderer.updateCamera();
  });
  updateInspector();
  updateHud();
}
function structureOutput(b) {
  const s = stats(b);
  if (b.type === "solar")
    return `${s.generation.toFixed(1)} E/S · ${solarPetals(b.level)} / 6 PETALS · ${s.generationInterval.toFixed(2)}S / CYCLE`;
  if (b.type === "miner")
    return `${Math.round(s.rate * 60)} MINERALS/MIN · ${s.miningInterval.toFixed(2)}S / CYCLE`;
  if (b.type === "relay")
    return `${s.maxLinks} CONNECTIONS · ${s.link} LINK RANGE`;
  if (b.type === "battery") return `${fmt(s.capacity)} ENERGY CAPACITY`;
  if (b.type === "repair") return `${Math.round(s.rate)} HULL/S PER DRONE`;
  if (b.type === "missile")
    return `${s.salvo} MISSILES · ${fmt(s.damage)} DAMAGE EACH · ${s.interval.toFixed(2)}S / SALVO`;
  if (b.type === "thel")
    return `${fmt(s.damage * 20 * s.beamDamageMultiplier * s.fireRate)} BASE DAMAGE/S + BEAM RAMP`;
  if (b.type === "laser")
    return `${fmt(s.damage)} DAMAGE · ${s.burst} SHOTS/BURST · ${s.interval.toFixed(2)}S / BURST`;
  return "";
}
function updateInspector() {
  const el = document.querySelector("#inspector");
  if (!el) return;
  const b = sim.buildings.find((o) => o.id === state.selected);
  const t = state.buildType;
  if (t) {
    const d = BUILDINGS[t];
    el.innerHTML = `<div class="eyebrow">CONSTRUCTION MODE</div><h3>${icon(t, 20)} ${d.name}</h3><p>${d.description}</p><div class="stats-line">${sim.buildingCost(t)} MINERALS<br>${fmt(stats({ type: t, level: 1, research: sim.rules }).hp)} HULL · ${stats({ type: t, level: 1, research: sim.rules }).link} LINK RANGE</div><p><kbd>SHIFT</kbd> Keep building<br><kbd>ESC</kbd> Cancel placement</p>`;
    return;
  }
  if (b) {
    const d = BUILDINGS[b.type],
      s = stats(b),
      cost = sim.upgradeCost(b),
      refund = Math.floor(
        (((b.baseCost ?? d.cost) +
          (b.upgradeSpent || 0) * sim.rules.upgradeRefund) *
          b.hp) /
          b.maxHp,
      );
    el.innerHTML = `<div class="eyebrow" id="selected-status">${b.type === "station" ? "MISSION CRITICAL" : b.construction < 1 ? "CONSTRUCTION / " + Math.floor(b.construction * 100) + "%" : b.powered ? "SYSTEM ONLINE" : "NO ENERGY"}</div><h3>${d.name}${b.type === "laser" && b.level > 1 ? " / Pulser" : ""} <span style="color:var(--mint)">${"·".repeat(b.level)}</span></h3>${b.type !== "station" ? `<div class="small-label">LEVEL ${b.level} / ${d.levels}</div><div class="stats-line">${structureOutput(b)}</div>` : ""}<div class="stats-line" id="selected-health">${fmt(b.hp)} / ${fmt(b.maxHp)} HULL</div><p>${d.description}</p>${s.range ? `<div class="stats-line">${Math.round(s.range)} RANGE</div>` : ""}${s.armor || s.shield ? `<div class="stats-line">${Math.round(s.armor * 100)}% ARMOR · ${Math.round(s.shield * 100)}% POWERED SHIELD</div>` : ""}${Number.isFinite(cost) ? `<p class="upgrade-preview">NEXT: ${structureOutput({ ...b, level: b.level + 1 })}</p><button class="primary" data-action="upgrade"><kbd>U / SPACE</kbd> Upgrade · ${cost}</button>` : "<p>Maximum configuration</p>"}${b.type === "laser" && b.level === 1 && sim.mission.thel ? `<button class="secondary" data-action="thel"><kbd>T</kbd> THEL · ${sim.upgradeCost(b, "thel")}</button>` : ""}${b.type !== "station" ? `<button class="quiet" data-action="recycle"><kbd>R</kbd> Recycle · +${refund} M</button>` : ""}`;
  } else {
    el.innerHTML = `<div class="eyebrow">NETWORK COMMAND</div><h3>Every connection counts.</h3><p>Build near a powered relay or station. Protect the links that keep your outpost alive.</p><p><kbd>1–7</kbd> Build &nbsp; <kbd>Q / E</kbd> Zoom<br><kbd>SPACE</kbd> Upgrade selection</p>${sim.mission.id === "skirmish" ? '<button class="secondary" data-action="wave">Call the next wave →</button>' : ""}<button class="quiet" data-action="center">Center camera</button>`;
  }
}
function updateHud() {
  if (screen !== "game") return;
  const set = (id, value) => {
    const e = document.getElementById(id);
    if (e) e.textContent = value;
  };
  set(
    "intel-count",
    sim.mission.classic ? "—" : researchBudget(progress).available,
  );
  const intelButton = document.querySelector('[data-action="run-research"]');
  const command = experienceBudget(progress);
  const mastery = masteryBudget(progress);
  set(
    "xp-hud",
    sim.mission.classic
      ? "CLASSIC · I"
      : `LV ${command.level} · ${command.available} SP · ${mastery.available} MP · I`,
  );
  intelButton.title = sim.mission.classic
    ? "Classic · original rules"
    : `Progression · I | Intel from rare ships | Level ${command.level}: ${Math.floor(command.into)}/${command.needed} XP | ${command.available} stat points | Mastery level ${mastery.level}: ${Math.floor(mastery.into)}/${mastery.needed} XP | ${mastery.available} mastery points`;
  set("minerals", fmt(sim.minerals));
  set("income", `+${fmt(sim.income * 60)} / MIN`);
  set("energy", fmt(sim.energy));
  set("capacity", `/ ${fmt(sim.capacity)}`);
  const balance = sim.generation - sim.consumption;
  set("balance", `${balance >= 0 ? "+" : ""}${balance.toFixed(1)}`);
  set(
    "power-rate",
    `${sim.generation.toFixed(1)} IN / ${sim.consumption.toFixed(1)} OUT`,
  );
  const bar = document.getElementById("power-bar");
  if (bar)
    bar.style.width = `${sim.capacity ? (sim.energy / sim.capacity) * 100 : 0}%`;
  let text = missionGoal(sim.mission);
  const m = sim.mission;
  if (m.kind === "mine")
    text = `${fmt(sim.mined)} / ${fmt(m.goal)} M EXTRACTED`;
  if (m.kind === "survive" || m.kind === "defend")
    text =
      sim.time >= m.goal
        ? "CLEAR REMAINING HOSTILES"
        : `${clock(Math.max(0, m.goal - sim.time))} REMAINING`;
  if (m.kind === "repair") {
    const b = sim.buildings.find((b) => b.type === "station");
    text = `${b ? Math.floor((b.hp / b.maxHp) * 100) : 0}% / ${Math.round(m.goal * 100)}% HULL`;
  }
  if (m.kind === "boss")
    text = `${sim.bossKills} / ${m.goal} MOTHERSHIPS DESTROYED`;
  if (m.id === "skirmish")
    text = `${sim.wave} WAVES · ${sim.kills} SHIPS DESTROYED`;
  set("objective-text", text);
  const pr = document.getElementById("objective-progress");
  if (pr) pr.style.width = sim.objectiveProgress() * 100 + "%";
  const noMore = sim.wave >= sim.mission.waves || sim.mission.sandbox;
  set("contact-label", noMore ? "SECTOR STATUS" : "NEXT CONTACT");
  set(
    "contact-time",
    sim.mission.miningWaves && sim.wave < sim.mission.waves
      ? `${sim.mission.miningWaves[sim.wave][0]}% MINED`
      : noMore
        ? sim.enemies.length
          ? "ENGAGED"
          : "CLEAR"
        : clock(sim.nextWave - sim.time),
  );
  set(
    "enemy-count",
    sim.enemies.length
      ? `${sim.enemies.length} HOSTILE SIGNAL${sim.enemies.length > 1 ? "S" : ""}`
      : "NO HOSTILE SIGNALS",
  );
  set("elapsed", `ELAPSED ${clock(sim.time)}`);
  set("zoom-label", `${Math.round(renderer.zoom * 60)}%`);
  set(
    "status-strip",
    sim.storm
      ? `SOLAR INTERFERENCE · GENERATION AT ${Math.round(sim.rules.stormOutput * 100)}%`
      : sim.waveAnnounce > 0
        ? `HOSTILE CONTACT · WAVE ${sim.wave}`
        : sim.energy < 0.4 && sim.time > 5
          ? "ENERGY LOW · ADD SOLAR CAPACITY"
          : "",
  );
  for (const b of document.querySelectorAll("[data-build]")) {
    b.disabled =
      !sim.mission.unlocked.includes(b.dataset.build) ||
      sim.minerals < BUILDINGS[b.dataset.build].cost;
    b.classList.toggle("selected", b.dataset.build === state.buildType);
  }
  for (const b of document.querySelectorAll("[data-speed]"))
    b.classList.toggle("active", !sim.paused && +b.dataset.speed === sim.speed);
  const pause = document.querySelector('[data-action="pause"]');
  if (pause) {
    pause.classList.toggle("active", sim.paused);
    pause.textContent = sim.paused ? "▶" : "Ⅱ";
    pause.setAttribute("aria-label", sim.paused ? "Resume" : "Pause");
  }
  const sel = sim.buildings.find((o) => o.id === state.selected);
  if (state.selected && !sel) {
    state.selected = null;
    updateInspector();
  }
  if (sel) {
    set("selected-health", `${fmt(sel.hp)} / ${fmt(sel.maxHp)} HULL`);
    set(
      "selected-status",
      sel.type === "station"
        ? "MISSION CRITICAL"
        : sel.construction < 1
          ? "CONSTRUCTION / " + Math.floor(sel.construction * 100) + "%"
          : sel.powered
            ? "SYSTEM ONLINE"
            : "NO ENERGY",
    );
    for (const button of document.querySelectorAll(
      '[data-action="upgrade"], [data-action="thel"]',
    ))
      button.disabled =
        sel.construction < 1 ||
        sim.minerals <
          sim.upgradeCost(
            sel,
            button.dataset.action === "thel" ? "thel" : null,
          );
  }
  for (const type of ["miners", "missiles"]) {
    const el = document.getElementById(type + "-toggle");
    if (el) {
      el.textContent = `${type === "miners" ? "Miners" : "Missiles"} ${sim[type + "On"] ? "on" : "off"}`;
      el.classList.toggle("off", !sim[type + "On"]);
    }
  }
  const map = document.getElementById("minimap");
  if (map) renderer.minimap(map, sim);
}
function toast(message) {
  clearTimeout(toastTimer);
  document.querySelector(".toast")?.remove();
  const node = document.createElement("div");
  node.className = "toast";
  node.setAttribute("role", "status");
  node.textContent = message;
  app.append(node);
  toastTimer = setTimeout(() => node.remove(), 3400);
}
function exportSave(filename = "the-space-game-save.json") {
  const blob = new Blob([JSON.stringify(progress, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function saveActive() {
  if (sim && sim.status === "playing") {
    bankIntel(progress, sim);
    bankExperience(progress, sim);
    if (sim.mission.kind === "endless")
      progress.endless = {
        ...progress.endless,
        cleared: Math.max(progress.endless?.cleared || 0, sim.clearedWave || 0),
      };
    progress.active = sim.snapshot();
    if (!saveProgress(progress))
      toast("Storage unavailable. Progress will last for this session only.");
  }
}
function openModal(html) {
  if (screen === "game") {
    pausedBeforeModal = sim.paused;
    sim.paused = true;
  }
  modalOpen = true;
  keys.clear();
  const layer = document.createElement("div");
  layer.className = "modal-layer";
  layer.innerHTML = `<section class="modal" role="dialog" aria-modal="true">${html}</section>`;
  app.append(layer);
  layer.querySelector("button")?.focus();
  updateHud();
}
function closeModal() {
  document.querySelector(".modal-layer")?.remove();
  modalOpen = false;
  if (screen === "game" && sim.status === "playing")
    sim.paused = pausedBeforeModal;
  updateHud();
}
function controls() {
  openModal(
    `<button class="quiet close" data-action="close" aria-label="Close controls">×</button><div class="eyebrow">FLIGHT MANUAL / ORIGINAL CONTROLS</div><h2>Command at your fingertips.</h2><table class="control-table"><tr><td>1 — 7</td><td>Relay · Miner · Solar · Store · Repair · Laser · Missile</td></tr><tr><td>Space / U</td><td>Upgrade the selected structure</td></tr><tr><td>P / T</td><td>Basic laser → Pulser / THEL</td></tr><tr><td>R</td><td>Recycle the selected structure</td></tr><tr><td>Shift + click</td><td>Keep placing the same structure</td></tr><tr><td>Esc / right-click</td><td>Cancel placement or selection</td></tr><tr><td>WASD / arrows</td><td>Pan the camera</td></tr><tr><td>Drag empty space</td><td>Pan the camera</td></tr><tr><td>Q / E / wheel</td><td>Zoom in / out</td></tr><tr><td>Pause button</td><td>Pause time; continue planning and building</td></tr><tr><td>I</td><td>Research tree · pauses the operation (browser addition)</td></tr><tr><td>Home</td><td>Center the camera (browser addition)</td></tr></table><p>Solar stations, energy stores, and relays carry energy through the network. Miners and defenses are endpoints. Relays support six to twelve links with upgrades; asteroids and structures can obstruct them.</p><button class="primary" data-action="close">Return to the field <span>↗</span></button>`,
  );
}
function settings() {
  openModal(
    `<button class="quiet close" data-action="close" aria-label="Close settings">×</button><div class="eyebrow">SYSTEM CONFIGURATION</div><h2>Make yourself at home.</h2><label class="settings-row">Sound effects<input type="checkbox" data-setting="sound" ${progress.settings.sound ? "checked" : ""}></label><label class="settings-row">Graphics<select data-setting="quality"><option value="high" ${progress.settings.quality === "high" ? "selected" : ""}>High · bloom</option><option value="low" ${progress.settings.quality === "low" ? "selected" : ""}>Performance</option></select></label><label class="settings-row">Reduce motion<input type="checkbox" data-setting="reducedMotion" ${progress.settings.reducedMotion ? "checked" : ""}></label><p>Progress and the current operation are saved in this browser. Liveries are cosmetic. Open Research or press I during modern operations to spend Intel and apply technologies immediately. Rare ships award Intel for permanent technology upgrades. Mining, combat and repairs earn XP for base stats. Classic disables persistent bonuses.</p><div class="modal-foot"><button class="secondary" data-action="export">Export save</button><button class="secondary" data-action="import">Import save</button></div><div class="modal-foot"><button class="quiet" data-action="fresh-start">Start fresh · back up progress</button></div><input type="file" id="save-file" accept="application/json" hidden><div class="modal-foot"><button class="primary" data-action="close">Done</button></div>`,
  );
}
function credits() {
  openModal(
    `<button class="quiet close" data-action="close" aria-label="Close credits">×</button><div class="eyebrow">ORIGINS / RESEARCH</div><h2>A small game.<br>A very large universe.</h2><p>The original <em>The Space Game</em> was created by David Scott and Casual Collective in 2009. Its distinctive energy network, asteroid economy, and fast construction controls are the foundation of this independent browser recreation.</p><p>This edition uses newly created models, textures, sound effects, and code. The Expedition and Challenges are newly authored missions. Original shortcuts, structure prices, upgrade branches, ranges, and network rules are documented against archived game evidence. This is a recreation, not an official release or a bit-exact emulation.</p><div class="credits-links"><a href="https://github.com/anderote/the-space-game/blob/master/docs/RESEARCH.md" target="_blank" rel="noopener">Research, screenshots &amp; preservation sources ↗</a><a href="https://github.com/anderote/the-space-game/blob/master/docs/ORIGINAL_MECHANICS.md" target="_blank" rel="noopener">Original mechanics &amp; controls ↗</a><a href="https://github.com/br3nt/the-space-game-launcher" target="_blank" rel="noopener">Preservation launcher for the original games ↗</a></div>`,
  );
}
function menu() {
  saveActive();
  openModal(
    `<div class="eyebrow">OPERATION PAUSED</div><h2>${esc(sim.mission.name)}</h2><p>${esc(missionGoal(sim.mission))}<br>Your operation has been saved.</p><button class="primary" data-action="close" style="width:100%">Resume operation <span>↗</span></button><div class="modal-foot"><button class="secondary" data-action="restart-confirm">Restart sector</button><button class="secondary" data-action="save-exit">Save &amp; exit</button></div><div class="modal-foot"><button class="quiet" data-action="modal-controls">Flight manual</button><button class="quiet" data-action="modal-settings">Settings</button><button class="quiet" data-action="research">Research tree · I</button></div>`,
  );
}
function result() {
  if (resultHandled) return;
  const intelBefore = researchBudget(progress).earned;
  bankIntel(progress, sim);
  bankExperience(progress, sim);
  resultHandled = true;
  const won = sim.status === "won";
  if (sim.mission.kind === "endless") {
    progress.endless = {
      ...progress.endless,
      cleared: Math.max(progress.endless?.cleared || 0, sim.clearedWave || 0),
      wave: Math.max(progress.endless?.wave || 0, sim.wave),
      kills: Math.max(progress.endless?.kills || 0, sim.kills),
      time: Math.max(progress.endless?.time || 0, sim.time),
    };
  }
  const stars = won
    ? recordVictory(progress, sim.mission, { lost: sim.lost, time: sim.time })
    : 0;
  progress.active = null;
  saveProgress(progress);
  const intelGained = researchBudget(progress).earned - intelBefore;
  const fieldIntel = sim.intelCredit.earned;
  openModal(
    `<div class="results"><div class="eyebrow">${won ? "TRANSMISSION / OPERATION COMPLETE" : "TRANSMISSION / SIGNAL LOST"}</div><h2>${won ? "A foothold secured." : "The network went dark."}</h2><p>${won ? esc(sim.mission.name) + " complete. The next sector is waiting." : "Regroup, rethink your network, and return to the belt."}</p>${intelGained > 0 || fieldIntel > 0 ? `<p class="research-summary">${fieldIntel} FIELD INTEL BANKED${intelGained > 0 ? ` · +${intelGained} FINAL REWARD` : ""}<br>${researchBudget(progress).available} Intel available for research</p>` : ""}${won ? `<div class="result-stars">${"★".repeat(stars)}${"☆".repeat(3 - stars)}</div>` : ""}<div class="result-stat-grid"><div><strong>${clock(sim.time)}</strong><span>ELAPSED</span></div><div><strong>${fmt(sim.mined)}</strong><span>MINED</span></div><div><strong>${sim.kills}</strong><span>DESTROYED</span></div></div>${won ? `<p>${sim.lost === 0 ? "★ No structures lost" : "☆ No-loss star missed"} &nbsp; · &nbsp; ${sim.time <= sim.mission.par ? "★ Within target time" : "☆ Target " + clock(sim.mission.par)}</p>` : ""}<div class="modal-foot"><button class="secondary" data-action="retry">Try again</button><button class="primary" data-action="result-next">${won && typeof sim.mission.id === "number" && sim.mission.id < 11 ? "Next sector ↗" : "Mission command ↗"}</button></div></div>`,
  );
}
function pickBuild(type) {
  if (screen !== "game") return;
  if (!sim.mission.unlocked.includes(type)) {
    toast("This structure is unavailable in the current mission.");
    return;
  }
  state.selected = null;
  state.buildType = state.buildType === type ? null : type;
  updateInspector();
  updateHud();
  sound.play("click");
}
function upgrade(branch = null) {
  const result = sim.upgrade(state.selected, branch);
  if (!result.ok) toast(result.reason);
  else {
    sound.play("upgrade");
    updateInspector();
    updateHud();
    saveActive();
  }
}
function recycle() {
  const result = sim.recycle(state.selected);
  if (!result.ok) toast(result.reason);
  else {
    state.selected = null;
    toast(`Structure recycled · +${result.refund} minerals`);
    updateInspector();
    saveActive();
  }
}
app.addEventListener("click", (e) => {
  const button = e.target.closest("button");
  if (!button || button.disabled) return;
  sound.unlock();
  sound.play("click");
  if (button.dataset.towerSelect) {
    selectedTower = button.dataset.towerSelect;
    researchScreen();
    if (innerWidth <= 650)
      document
        .querySelector(".tower-specialization")
        .scrollIntoView({ block: "start" });
    return;
  }
  if (button.dataset.progression) {
    progressionPage = button.dataset.progression;
    researchScreen();
    document.querySelector(".research-body").scrollTop = 0;
    return;
  }
  if (button.dataset.tech) {
    selectedTech = button.dataset.tech;
    researchScreen();
    if (innerWidth <= 650)
      document.querySelector(".tech-detail").scrollIntoView({ block: "start" });
    return;
  }
  if (button.dataset.mission !== undefined) {
    selector(tab, +button.dataset.mission);
    return;
  }
  if (button.dataset.tab) {
    selector(button.dataset.tab);
    return;
  }
  if (button.dataset.build) {
    pickBuild(button.dataset.build);
    return;
  }
  if (button.dataset.speed) {
    sim.speed = +button.dataset.speed;
    sim.paused = false;
    document.querySelector(".paused-banner")?.remove();
    updateHud();
    return;
  }
  if (button.dataset.mode) {
    const mode = button.dataset.mode,
      seed = Math.max(
        1,
        Math.min(
          999999,
          +document.querySelector("#" + mode + "-seed").value || 4281,
        ),
      );
    launch(skirmish(seed, mode));
    return;
  }
  if (button.dataset.livery) {
    progress.livery = button.dataset.livery;
    saveProgress(progress);
    applySettings();
    selector("unlocks");
    return;
  }
  const action = button.dataset.action;
  if (action === "tech-tree-top") {
    document.querySelector(".tech-tree").scrollIntoView({ block: "start" });
    return;
  }
  if (action === "research") {
    if (screen === "game" && sim.status === "playing") {
      runResearch();
      return;
    }
    researchReturn = screen === "select" ? tab : "home";
    if (sim?.status === "playing") {
      saveActive();
      sim.paused = true;
    }
    researchScreen();
    return;
  }
  if (action === "research-back") {
    leaveResearch();
    return;
  }
  if (action === "run-research") {
    runResearch();
    return;
  }
  if (["tech-buy", "stat-buy", "tower-stat-buy"].includes(action)) {
    const result =
      action === "tech-buy"
        ? buyResearch(progress, button.dataset.id)
        : action === "tower-stat-buy"
          ? buyTowerSkill(progress, button.dataset.tower, button.dataset.id)
          : buyBaseStat(progress, button.dataset.id);
    if (!result.ok) {
      toast(result.reason);
      return;
    }
    saveResearchChanges();
    sound.play("upgrade");
    researchScreen();
    toast(
      TECHNOLOGIES.find((t) => t.id === button.dataset.id)?.modifiers
        .startingMinerals
        ? "Freight researched for future launches."
        : "Upgrade applied. Your command is stronger.",
    );
    return;
  }
  if (action === "tech-reset") {
    openModal(
      `<div class="eyebrow">RECONFIGURE THE FRONTIER</div><h2>Try a different path.</h2><p>Refund all ${researchBudget(progress).spent} invested Intel and clear ${researchReturn === "game" ? "your technology tree. Research bonuses will be removed from this operation; XP stats are kept." : "your technology tree. XP stats are kept. Saved operations update when resumed."}</p><div class="modal-foot"><button class="secondary" data-action="close">Keep research</button><button class="primary" data-action="tech-reset-confirm">Refund research</button></div>`,
    );
    return;
  }
  if (action === "tech-reset-confirm") {
    resetResearch(progress);
    saveResearchChanges();
    researchScreen();
    toast("All invested Intel refunded. Choose your next specialization.");
    return;
  }
  if (action === "home" || action === "save-exit") {
    home();
    return;
  }
  if (["campaign", "classic", "challenges", "freeplay"].includes(action)) {
    selector(action);
    return;
  }
  if (action === "continue") {
    const s = progress.active,
      m =
        s.missionId === "skirmish"
          ? { ...s.mission, waves: Infinity }
          : CAMPAIGN.find((m) => m.id === s.missionId) ||
            CLASSIC.find((m) => m.id === s.missionId) ||
            CHALLENGES.find((m) => m.id === s.missionId);
    if (m) launch(m, s);
    else {
      progress.active = null;
      saveProgress(progress);
      home();
    }
    return;
  }
  if (action === "launch") {
    const m = (
      tab === "campaign" ? CAMPAIGN : tab === "classic" ? CLASSIC : CHALLENGES
    )[selectedMission];
    launch(m);
    return;
  }
  if (action === "close") {
    closeModal();
    return;
  }
  if (action === "controls") {
    controls();
    return;
  }
  if (action === "settings") {
    settings();
    return;
  }
  if (action === "credits") {
    credits();
    return;
  }
  if (action === "menu") {
    menu();
    return;
  }
  if (action === "modal-controls" || action === "modal-settings") {
    closeModal();
    action === "modal-controls" ? controls() : settings();
    return;
  }
  if (action === "pause") {
    sim.paused = !sim.paused;
    document.querySelector(".paused-banner")?.remove();
    if (sim.paused) {
      const el = document.createElement("div");
      el.className = "paused-banner";
      el.innerHTML =
        "SIMULATION PAUSED<small>Construction and upgrades remain available</small>";
      app.append(el);
    }
    updateHud();
    return;
  }
  if (action === "upgrade") {
    upgrade();
    return;
  }
  if (action === "thel") {
    upgrade("thel");
    return;
  }
  if (action === "recycle") {
    recycle();
    return;
  }
  if (action === "center") {
    renderer.center();
    return;
  }
  if (action === "miners" || action === "missiles") {
    sim[action + "On"] = !sim[action + "On"];
    updateHud();
    return;
  }
  if (action === "grid") {
    state.grid = !state.grid;
    return;
  }
  if (action === "wave") {
    sim.callWave();
    updateHud();
    return;
  }
  if (action === "restart-confirm") {
    closeModal();
    openModal(
      `<div class="eyebrow">RESTART SECTOR</div><h2>Start this operation again?</h2><p>Your current sector progress will be replaced. Completed missions and unlocks are kept.</p><div class="modal-foot"><button class="secondary" data-action="close">Keep playing</button><button class="primary" data-action="retry">Restart sector</button></div>`,
    );
    return;
  }
  if (action === "retry") {
    launch(sim.mission);
    return;
  }
  if (action === "result-next") {
    if (
      sim.status === "won" &&
      typeof sim.mission.id === "number" &&
      sim.mission.id < 11
    ) {
      selector("campaign", sim.mission.id + 1);
    } else
      selector(
        typeof sim.mission.id === "number"
          ? "campaign"
          : sim.mission.classic
            ? "classic"
            : sim.mission.id === "skirmish"
              ? "freeplay"
              : "challenges",
      );
    return;
  }
  if (action === "export") {
    saveActive();
    exportSave();
    return;
  }
  if (action === "fresh-start") {
    openModal(
      `<div class="eyebrow">A NEW FRONTIER</div><h2>Start fresh.</h2><p>Reset campaign progress, research, Intel, XP, base stats, and the saved operation. A backup is saved locally and downloaded first. Your settings are kept.</p><div class="modal-foot"><button class="secondary" data-action="close">Keep playing</button><button class="primary" data-action="fresh-start-confirm">Back up &amp; start fresh</button></div>`,
    );
    return;
  }
  if (action === "fresh-start-confirm") {
    saveActive();
    try {
      const reset = resetProgress(progress);
      exportSave("the-space-game-before-fresh-start.json");
      progress = reset.progress;
      sim = null;
      state = { selected: null, buildType: null, mouse: null, grid: false };
      selectedTech = "solar_cells";
      progressionPage = "tech";
      applySettings();
      home();
      toast("Fresh start ready. Previous progress is backed up.");
    } catch {
      toast("Backup or reset could not be saved. Progress was kept.");
    }
    return;
  }
  if (action === "import") {
    document.querySelector("#save-file").click();
  }
});
app.addEventListener("change", async (e) => {
  if (e.target.id === "difficulty") {
    progress.settings.difficulty = e.target.value;
    saveProgress(progress);
  }
  if (e.target.dataset.setting) {
    progress.settings[e.target.dataset.setting] =
      e.target.type === "checkbox" ? e.target.checked : e.target.value;
    applySettings();
    saveProgress(progress);
  }
  if (e.target.id === "save-file" && e.target.files[0]) {
    try {
      const value = JSON.parse(await e.target.files[0].text());
      if (
        value.version !== 2 ||
        !value.completed ||
        !value.challenges ||
        typeof value.completed !== "object" ||
        typeof value.challenges !== "object"
      )
        throw new Error("Invalid save format");
      for (const c of [
        ...Object.values(value.completed),
        ...Object.values(value.challenges),
      ])
        if (!Number.isInteger(c.stars) || c.stars < 1 || c.stars > 3)
          throw new Error("Invalid mission record");
      // Import campaign records only; arbitrary simulation snapshots are not trusted.
      progress = migrateProgression({
        ...freshProgress(),
        progressionVersion: value.progressionVersion,
        intel: value.intel,
        experience: value.experience,
        completed: value.completed,
        challenges: value.challenges,
        research: normalizeResearch(
          value.research,
          researchBudget(value).earned,
        ),
        endless: {
          wave: Math.max(0, Math.floor(Number(value.endless?.wave) || 0)),
          cleared: Math.max(0, Math.floor(Number(value.endless?.cleared) || 0)),
          kills: Math.max(0, Number(value.endless?.kills) || 0),
          time: Math.max(0, Number(value.endless?.time) || 0),
        },
        livery: UPGRADES.some((u) => u.id === value.livery)
          ? value.livery
          : "mint",
        settings: normalizeSettings(value.settings),
      });
      saveProgress(progress);
      applySettings();
      sim = null;
      home();
      toast("Campaign progress imported.");
    } catch {
      toast(
        "Could not import this save. Use a valid The Space Game save file.",
      );
    }
  }
});
const canvas = renderer.renderer.domElement;
function position(e) {
  const p = renderer.screenToWorld(e.clientX, e.clientY);
  return { x: Math.round(p.x / 5) * 5, y: Math.round(p.y / 5) * 5 };
}
canvas.addEventListener("pointermove", (e) => {
  if (screen !== "game" || modalOpen) return;
  state.mouse = position(e);
  if (pointer) {
    const dx = e.clientX - pointer.lastX,
      dy = e.clientY - pointer.lastY;
    pointer.distance += Math.hypot(dx, dy);
    if (pointer.distance > 5 && !state.buildType) {
      renderer.pan(dx, dy);
      pointer.dragged = true;
    }
    pointer.lastX = e.clientX;
    pointer.lastY = e.clientY;
  }
});
canvas.addEventListener("pointerdown", (e) => {
  if (screen !== "game" || modalOpen || e.button === 2) return;
  sound.unlock();
  canvas.setPointerCapture(e.pointerId);
  pointer = {
    x: e.clientX,
    y: e.clientY,
    lastX: e.clientX,
    lastY: e.clientY,
    distance: 0,
    dragged: false,
    id: e.pointerId,
  };
  state.mouse = position(e);
});
canvas.addEventListener("pointerup", (e) => {
  if (!pointer) return;
  const dragged = pointer.dragged;
  pointer = null;
  if (screen !== "game" || modalOpen || dragged) return;
  const world = position(e);
  if (state.buildType) {
    const placed = sim.build(state.buildType, world.x, world.y);
    if (placed.ok) {
      sound.play("build");
      if (!e.shiftKey) state.buildType = null;
      if (placed.warning) toast(placed.warning);
      updateInspector();
      saveActive();
    } else toast(placed.reason);
  } else {
    const hit = sim.buildings
      .filter(
        (b) =>
          distance(world, b) <
          (BUILDINGS[b.type].pickRadius || BUILDINGS[b.type].radius) +
            7 / renderer.zoom,
      )
      .sort((a, b) => distance(world, a) - distance(world, b))[0];
    state.selected = hit?.id || null;
    updateInspector();
  }
  updateHud();
});
canvas.addEventListener("pointercancel", () => {
  pointer = null;
});
canvas.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  state.buildType = null;
  state.selected = null;
  if (screen === "game") {
    updateInspector();
    updateHud();
  }
});
canvas.addEventListener(
  "wheel",
  (e) => {
    if (screen !== "game" || modalOpen) return;
    e.preventDefault();
    renderer.setZoom(
      renderer.zoom * Math.exp(-e.deltaY * 0.0015),
      e.clientX,
      e.clientY,
    );
    state.mouse = position(e);
  },
  { passive: false },
);
window.addEventListener("keydown", (e) => {
  if (modalOpen && e.key === "Tab") {
    const items = [
        ...document.querySelectorAll(
          ".modal button:not(:disabled),.modal input:not([hidden]),.modal select,.modal a",
        ),
      ],
      first = items[0],
      last = items.at(-1);
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last?.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first?.focus();
    }
    return;
  }
  if (["INPUT", "SELECT", "TEXTAREA"].includes(e.target.tagName)) return;
  if (e.key === "Escape") {
    e.preventDefault();
    if (modalOpen) {
      if (sim?.status !== "playing" && screen === "game") return;
      closeModal();
    } else if (screen === "game") {
      state.buildType = null;
      state.selected = null;
      updateInspector();
      updateHud();
    } else if (screen === "research") leaveResearch();
    else if (screen === "select") home();
    return;
  }
  if (screen !== "game" || modalOpen) return;
  const k = e.key.toLowerCase();
  if (
    [" ", "arrowup", "arrowdown", "arrowleft", "arrowright", "home"].includes(k)
  )
    e.preventDefault();
  keys.add(k);
  sound.unlock();
  if (e.repeat) return;
  if (/^[1-7]$/.test(k)) {
    pickBuild(BUILD_ORDER[Number(k) - 1]);
    return;
  }
  if (k === "i") {
    runResearch();
    return;
  }
  if (k === "u" || k === " ") {
    upgrade();
    return;
  }
  if (k === "t") {
    upgrade("thel");
    return;
  }
  if (k === "p") {
    upgrade("pulser");
    return;
  }
  if (k === "r") {
    recycle();
    return;
  }
  if (k === "q") renderer.setZoom(renderer.zoom + 0.5);
  if (k === "e") renderer.setZoom(renderer.zoom - 0.5);
  if (k === "home") renderer.center();
  if (k === "?") controls();
});
window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));
window.addEventListener("blur", () => keys.clear());
document.addEventListener("visibilitychange", () => {
  if (document.hidden && screen === "game" && sim.status === "playing") {
    saveActive();
    sim.paused = true;
    updateHud();
  }
  last = performance.now();
});
window.addEventListener("beforeunload", saveActive);
window.addEventListener("resize", () => renderer.resize());
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  if (screen === "game") {
    if (!modalOpen) {
      const speed = 250 * dt;
      if (keys.has("w") || keys.has("arrowup")) renderer.pan(0, speed);
      if (keys.has("s") || keys.has("arrowdown")) renderer.pan(0, -speed);
      if (keys.has("a") || keys.has("arrowleft")) renderer.pan(speed, 0);
      if (keys.has("d") || keys.has("arrowright")) renderer.pan(-speed, 0);
    }
    sim.update(dt);
    renderer.render(sim, state, now);
    for (const event of sim.events.splice(0)) {
      if (event.type === "lost" && event.name) toast(`${event.name} destroyed`);
      sound.play(event.type);
    }
    const earned = bankIntel(progress, sim);
    const experience = bankExperience(progress, sim);
    if (experience.levels > 0) {
      saveActive();
      toast(
        `Command level ${experienceBudget(progress).level} · +${experience.levels} stat point${experience.levels > 1 ? "s" : ""} · Press I`,
      );
    }
    if (experience.masteryLevels > 0) {
      saveActive();
      toast(
        `Mastery level ${masteryBudget(progress).level} · +${experience.masteryLevels} tower points · Press I`,
      );
    }
    if (earned > 0) {
      saveActive();
      toast(
        `+${earned} Intel · ${researchBudget(progress).available} available · Press I to research`,
      );
    }
    if (sim.status !== "playing") result();
    uiTick += dt;
    saveTick += dt;
    if (uiTick > 0.12) {
      updateHud();
      uiTick = 0;
    }
    if (saveTick > 5) {
      saveActive();
      saveTick = 0;
    }
  } else if (screen === "research" && researchReturn === "game") {
    renderer.render(sim, state, now);
  } else {
    demo.update(dt * 0.4);
    demo.events = [];
    renderer.render(demo, { selected: null, buildType: null }, now);
  }
  requestAnimationFrame(frame);
}
home();
requestAnimationFrame(frame);

window.addEventListener("storage", (event) => {
  if (event.key !== "the-space-game-v2" || !event.newValue) return;
  try {
    const next = JSON.parse(event.newValue);
    if (next.resetToken && next.resetToken !== progress.resetToken) {
      sim = null;
      progress = loadProgress();
      applySettings();
      home();
      toast("Progress reset in another tab. Fresh start ready.");
    }
  } catch {
    /* Ignore malformed storage events; normal load sanitization remains. */
  }
});
