import { skillBonus } from "./progression-balance.js";
import {
  BRANCHES,
  TECHNOLOGIES,
  TECH_BY_ID,
  normalizeResearch,
  researchBudget,
  researchEligibility,
  earnsFieldIntel,
} from "./research.js";
import { BASE_STATS, experienceBudget, masteryBudget } from "./experience.js";
import { towerMasteryView } from "./tower-view.js";
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export function researchView(
  progress,
  selectedId,
  icon,
  { inGame = false, mission = null, page = "tech", tower = "laser" } = {},
) {
  const r = normalizeResearch(progress.research),
    budget = researchBudget(progress),
    xp = experienceBudget(progress),
    mastery = masteryBudget(progress),
    canEarn = !mission || earnsFieldIntel(mission),
    selected = TECH_BY_ID[selectedId] || TECHNOLOGIES[0],
    branch = BRANCHES.find((b) => b.id === selected.branch),
    owned = r.owned.includes(selected.id),
    eligible = researchEligibility(progress, selected.id);
  const status = (t) =>
    r.owned.includes(t.id)
      ? "ACTIVE"
      : researchEligibility(progress, t.id).ok
        ? "AVAILABLE"
        : t.requires.some((id) => !r.owned.includes(id))
          ? "LOCKED"
          : "NEED INTEL";
  const techCard = (t, index) =>
    `<button class="tech-node tech-${index} ${r.owned.includes(t.id) ? "owned equipped" : ""} ${selected.id === t.id ? "selected" : ""} ${status(t) === "LOCKED" ? "locked" : ""}" data-tech="${t.id}" aria-pressed="${selected.id === t.id}" aria-label="${escape(t.name)} — ${status(t)}"><span class="tech-state">${r.owned.includes(t.id) ? "◈" : "◇"} ${status(t)}</span><strong>${escape(t.name)}</strong><span class="tech-effect">${escape(t.effect)}</span><span class="tech-price">${t.cost} INTEL</span></button>`;
  const sources = `<section class="progression-sources"><div><span class="small-label">RARE-SHIP INTEL</span><strong>Elite ships +2 · Motherships +3</strong><p>Gold-marked elite ships arrive every third wave. Destroy them to recover Intel.</p></div><div><span class="small-label">COMMAND EXPERIENCE</span><strong>Mine · Fight · Repair</strong><p>5 minerals, 20 enemy hull damage, or 10 damage repairs earn 2 XP.</p></div><div><span class="small-label">TOWER MASTERY</span><strong>Kill · Build · Upgrade · Repair</strong><p>20 XP per ship destroyed, 2 XP per 10 minerals in completed construction or upgrades, and 2 XP per 10 damage repaired.</p></div>${!canEarn ? '<p class="testing-note">Classic: persistent upgrades and progression rewards are disabled.</p>' : ""}</section>`;
  const stats = `<section class="base-stats-panel"><div class="xp-overview"><div><div class="eyebrow">COMMAND LEVEL ${xp.level}</div><h3>Strengthen the fundamentals.</h3><p>Every level grants one stat point. Your technology tree and base stats stack, and apply immediately to modern operations.</p></div><strong>${xp.available}<small> UNASSIGNED POINT${xp.available === 1 ? "" : "S"}</small></strong><div class="xp-progress"><span>${Math.floor(xp.into)} / ${xp.needed} XP to level ${xp.level + 1}</span><div class="intel-meter"><i style="width:${(100 * xp.into) / xp.needed}%"></i></div><small>${Math.floor(xp.xp).toLocaleString()} lifetime XP · ${xp.spent} points invested</small></div></div><div class="base-stat-grid">${BASE_STATS.map(
    (stat) => {
      const rank = xp.ranks[stat.id] || 0;
      return `<article class="base-stat-card"><header>${icon(stat.icon, 30)}<div><h3>${stat.name}</h3><span>RANK ${rank} / ${stat.max}</span></div></header><strong>${skillBonus(stat, rank)}%<small> ${stat.unit.replace("% ", "")}</small></strong><p>${stat.effect} per rank.</p><div class="stat-ranks" style="grid-template-columns:repeat(${stat.max},1fr)" aria-label="Rank ${rank} of ${stat.max}">${Array.from({ length: stat.max }, (_, i) => `<i class="${i < rank ? "filled" : ""}"></i>`).join("")}</div><button class="secondary" data-action="stat-buy" data-id="${stat.id}" ${rank >= stat.max || !xp.available ? "disabled" : ""}>${rank >= stat.max ? "Maximum rank" : `Improve ${stat.name} · 1 point`}</button></article>`;
    },
  ).join(
    "",
  )}</div><p class="stat-note">Repair XP counts restored combat damage and damaged mission objectives. Recycling, upgrading hulls, and docking drone maintenance do not generate XP. Classic disables persistent bonuses.</p></section>`;
  const tree = `<div class="tech-tree">${BRANCHES.map(
    (b) =>
      `<section class="tech-branch" style="--branch:${b.color}"><header><span>${icon(b.icon, 24)}</span><div><h3>${b.name}</h3><p>${b.subtitle}</p></div></header><div class="branch-graph"><svg class="tech-connectors" viewBox="0 0 200 922" preserveAspectRatio="none" aria-hidden="true"><path d="M100 90 V101 H48 V112 M100 101 H152 V112 M48 226 V237 H152 V226 M100 237 V248 M100 338 V360 M100 450 V461 H48 V472 M100 461 H152 V472 M48 586 V597 H152 V586 M100 597 V608 M100 698 V720 M100 810 V832" /></svg>${TECHNOLOGIES.filter(
        (t) => t.branch === b.id && !t.sideBranch,
      )
        .map(techCard)
        .join("")}</div>${
        TECHNOLOGIES.some((t) => t.branch === b.id && t.sideBranch)
          ? `<div class="tech-side-research"><div class="small-label">NETWORK AUTOMATION · REQUIRES FIELD COUPLERS</div>${TECHNOLOGIES.filter(
              (t) => t.branch === b.id && t.sideBranch,
            )
              .map(techCard)
              .join("")}</div>`
          : ""
      }</section>`,
  ).join("")}</div>
  <aside class="tech-detail" style="--branch:${branch.color}"><button class="quiet research-tree-back" data-action="tech-tree-top">↑ Back to technologies</button><div class="eyebrow">${branch.name} / TIER ${selected.tier + 1}</div><div class="detail-emblem">${icon(branch.icon, 50)}</div>${selected.tag ? `<span class="tech-tag">${selected.tag}</span>` : ""}<h3>${selected.name}</h3><div class="detail-effect">${selected.effect}</div><p>${selected.detail}</p><div class="tech-requirements"><div class="small-label">PREREQUISITES</div>${selected.requires.length ? selected.requires.map((id) => `<button class="prerequisite ${r.owned.includes(id) ? "met" : ""}" data-tech="${id}">${r.owned.includes(id) ? "✓" : "◇"} ${TECH_BY_ID[id].name}</button>`).join("") : "<span>Entry-level technology · available immediately</span>"}</div><div class="tech-cost"><span>RESEARCH COST</span><strong>${selected.cost} Intel</strong></div>
  ${owned ? '<div class="technology-active">✓ Active permanently · no equipment limit</div>' : `<button class="primary" data-action="tech-buy" data-id="${selected.id}" ${eligible.ok ? "" : "disabled"}>Research · ${selected.cost} Intel <span>↗</span></button>${!eligible.ok ? `<p class="tech-reason">${escape(eligible.reason)}</p>` : ""}`}
  <p class="research-scope">${selected.modifiers.startingMinerals ? "LAUNCH ONLY · Freight adds minerals when a new operation begins." : inGame ? "LIVE UPGRADE · Research applies immediately to existing and new structures. Your previous pause state is preserved." : "Every purchased technology stays active. Research with I during modern operations; Classic disables persistent bonuses."}</p></aside>`;
  return `<div class="screen-shade research-shade"><section class="research-window"><header class="research-header"><div><div class="eyebrow">${inGame ? "OPERATION PAUSED / LIVE RESEARCH" : "EXPEDITION SCIENCE DIVISION"}</div><h2>Build a better frontier.</h2><p>Discover breakthroughs. Develop your command.</p></div><div class="research-wallet"><strong>${budget.available}<span> INTEL</span></strong><small>${r.owned.length} / ${TECHNOLOGIES.length} TECHNOLOGIES ACTIVE</small></div><div class="research-wallet xp-wallet"><strong>${xp.level}<span> LEVEL</span></strong><small>${xp.available} STAT POINT${xp.available === 1 ? "" : "S"} AVAILABLE</small></div><div class="research-wallet mastery-wallet"><strong>${mastery.level}<span> MASTERY</span></strong><small>${mastery.available} TOWER POINT${mastery.available === 1 ? "" : "S"} AVAILABLE</small></div><button class="secondary" data-action="research-back">${inGame ? "← Return to operation" : "← Command"}</button></header>
  <nav class="progression-tabs"><button class="tab ${page === "tech" ? "active" : ""}" data-progression="tech">Technology tree · ${TECHNOLOGIES.length}</button><button class="tab ${page === "stats" ? "active" : ""}" data-progression="stats">Base stats${xp.available ? ` · ${xp.available} point${xp.available === 1 ? "" : "s"}` : ""}</button><button class="tab ${page === "towers" ? "active" : ""}" data-progression="towers">Tower mastery${mastery.available ? ` · ${mastery.available} points` : ""}</button><span>All upgrades stay active together.</span></nav>
  <div class="research-body ${page !== "tech" ? "stats-body" : ""}">${sources}${page === "stats" ? stats : page === "towers" ? towerMasteryView(mastery, tower, icon) : tree}</div>
  <footer class="research-footer"><div><strong>Three paths. One stronger outpost.</strong><span>Intel unlocks technology · Command XP improves base stats · Mastery XP improves towers</span></div>${page === "tech" ? `<button class="quiet" data-action="tech-reset" ${!r.owned.length ? "disabled" : ""}>Respec · refund ${budget.spent} Intel</button>` : `<span>${canEarn ? "XP and Intel persist after a loss." : "Classic · no progression rewards"}</span>`}</footer></section></div>`;
}
