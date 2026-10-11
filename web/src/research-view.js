import {
  BRANCHES,
  TECHNOLOGIES,
  TECH_BY_ID,
  RESEARCH_CAPACITY,
  normalizeResearch,
  researchBudget,
  researchEligibility,
} from "./research.js";
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export function researchView(progress, selectedId, icon) {
  const r = normalizeResearch(progress.research),
    budget = researchBudget(progress),
    selected = TECH_BY_ID[selectedId] || TECHNOLOGIES[0],
    branch = BRANCHES.find((b) => b.id === selected.branch),
    owned = r.owned.includes(selected.id),
    equipped = r.active.includes(selected.id),
    eligible = researchEligibility(progress, selected.id);
  const status = (t) =>
    r.active.includes(t.id)
      ? "EQUIPPED"
      : r.owned.includes(t.id)
        ? "RESEARCHED"
        : researchEligibility(progress, t.id).ok
          ? "AVAILABLE"
          : t.requires.some((id) => !r.owned.includes(id))
            ? "LOCKED"
            : "NEED INTEL";
  const techCard = (t, index) =>
    `<button class="tech-node tech-${index} ${r.owned.includes(t.id) ? "owned" : ""} ${r.active.includes(t.id) ? "equipped" : ""} ${selected.id === t.id ? "selected" : ""} ${status(t) === "LOCKED" ? "locked" : ""}" data-tech="${t.id}" aria-pressed="${selected.id === t.id}" aria-label="${escape(t.name)} — ${status(t)}"><span class="tech-state">${r.active.includes(t.id) ? "◈" : r.owned.includes(t.id) ? "✓" : status(t) === "LOCKED" ? "◇" : "○"} ${status(t)}</span><strong>${escape(t.name)}</strong><span class="tech-effect">${escape(t.effect)}</span><span class="tech-price">${t.cost} INTEL <span>${t.load} SLOT${t.load > 1 ? "S" : ""}</span></span></button>`;
  return `<div class="screen-shade research-shade"><section class="research-window"><header class="research-header"><div><div class="eyebrow">EXPEDITION SCIENCE DIVISION</div><h2>Build a better frontier.</h2><p>Discover technologies. Configure your next operation.</p></div><div class="research-wallet"><strong>${budget.available}<span> INTEL</span></strong><small>${budget.earned} EARNED · ${budget.spent} INVESTED</small></div><button class="secondary" data-action="research-back">← Command</button></header>
 <div class="research-loadout"><div><span class="small-label">DEPLOYMENT LOADOUT</span><div class="loadout-pips" aria-label="${budget.load} of ${RESEARCH_CAPACITY} slots equipped">${Array.from({ length: RESEARCH_CAPACITY }, (_, i) => `<i class="${i < budget.load ? "filled" : ""}"></i>`).join("")}<b>${budget.load} / ${RESEARCH_CAPACITY}</b></div></div><div class="loadout-chips">${r.active.length ? r.active.map((id) => `<button data-tech="${id}" style="--branch:${BRANCHES.find((b) => b.id === TECH_BY_ID[id].branch).color}">${escape(TECH_BY_ID[id].name)}</button>`).join("") : "<span>Equip researched technologies to specialize your next launch.</span>"}</div></div>
 <div class="research-body"><div class="tech-tree">${BRANCHES.map((b) => {
   const nodes = TECHNOLOGIES.filter((t) => t.branch === b.id);
   return `<section class="tech-branch" style="--branch:${b.color}"><header><span>${icon(b.icon, 24)}</span><div><h3>${b.name}</h3><p>${b.subtitle}</p></div></header><div class="branch-graph"><svg class="tech-connectors" viewBox="0 0 200 450" preserveAspectRatio="none" aria-hidden="true"><path d="M100 90 V101 H48 V112 M100 101 H152 V112 M48 226 V237 H152 V226 M100 237 V248 M100 338 V360" /></svg>${nodes.map(techCard).join("")}</div></section>`;
 }).join("")}</div>
 <aside class="tech-detail" style="--branch:${branch.color}"><button class="quiet research-tree-back" data-action="tech-tree-top">↑ Back to technologies</button><div class="eyebrow">${branch.name} / TIER ${selected.tier + 1}</div><div class="detail-emblem">${icon(branch.icon, 50)}</div>${selected.tag ? `<span class="tech-tag">${selected.tag}</span>` : ""}<h3>${selected.name}</h3><div class="detail-effect">${selected.effect}</div><p>${selected.detail}</p><div class="tech-requirements"><div class="small-label">PREREQUISITES</div>${selected.requires.length ? selected.requires.map((id) => `<button class="prerequisite ${r.owned.includes(id) ? "met" : ""}" data-tech="${id}">${r.owned.includes(id) ? "✓" : "◇"} ${TECH_BY_ID[id].name}</button>`).join("") : "<span>Entry-level technology · available immediately</span>"}</div><div class="tech-cost"><span>RESEARCH COST</span><strong>${selected.cost} Intel</strong><span>LOADOUT WEIGHT</span><strong>${selected.load} / ${RESEARCH_CAPACITY} slots</strong></div>
 ${owned ? `<button class="primary" data-action="tech-toggle" data-id="${selected.id}" ${!equipped && budget.load + selected.load > RESEARCH_CAPACITY ? "disabled" : ""}>${equipped ? "Unequip technology" : "Equip technology"} <span>${equipped ? "−" : "+"}</span></button>${!equipped && budget.load + selected.load > RESEARCH_CAPACITY ? '<p class="tech-reason">Unequip another technology to free loadout slots.</p>' : ""}` : `<button class="primary" data-action="tech-buy" data-id="${selected.id}" ${eligible.ok ? "" : "disabled"}>Research · ${selected.cost} Intel <span>↗</span></button>${!eligible.ok ? `<p class="tech-reason">${escape(eligible.reason)}</p>` : ""}`}
 <p class="research-scope">Applies at launch to Expedition, Challenges, Endless, and Sandbox. Classic uses the original rules. A saved operation keeps its existing loadout.</p></aside></div>
 <footer class="research-footer"><div><strong>Turn experience into possibility.</strong><span>6 starting Intel · 2 per new mission star · 4 per new five-wave Endless milestone</span></div><button class="quiet" data-action="tech-reset" ${!r.owned.length ? "disabled" : ""}>Respec · refund ${budget.spent} Intel</button></footer></section></div>`;
}
