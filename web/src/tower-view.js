import { skillBonus } from "./progression-balance.js";
import { TOWER_TYPES, TOWER_BY_ID, towerPoints } from "./tower-skills.js";
export function towerMasteryView(xp, selectedId, icon) {
  const tower = TOWER_BY_ID[selectedId] || TOWER_BY_ID.laser;
  const ranks = xp.towers[tower.id] || {};
  return `<section class="base-stats-panel tower-mastery-panel">
    <div class="xp-overview"><div><div class="eyebrow">TOWER MASTERY / MASTERY LEVEL ${xp.level}</div><h3>Make every structure your own.</h3><p>Spend mastery points on a building class. Bonuses improve existing and future structures, stack with research, and persist across games. Basic laser and Pulser have separate specializations. Missile ordnance and Fighter craft improve the units themselves.</p></div><strong>${xp.available}<small> MASTERY POINTS</small></strong></div>
    <div class="xp-progress"><span>${Math.floor(xp.into)} / ${xp.needed} mastery XP to level ${xp.level + 1}</span><div class="intel-meter"><i style="width:${(100 * xp.into) / xp.needed}%"></i></div><small>${Math.floor(xp.xp)} lifetime mastery XP</small></div><div class="tower-mastery-layout"><nav class="tower-choices" aria-label="Choose a building specialization">${TOWER_TYPES.map((t) => `<button class="tower-choice ${t.id === tower.id ? "active" : ""}" data-tower-select="${t.id}" aria-pressed="${t.id === tower.id}" style="--branch:${t.color}">${icon(t.icon, 26)}<span>${t.name}<small>${towerPoints({ [t.id]: xp.towers[t.id] || {} })} POINTS INVESTED</small></span></button>`).join("")}</nav>
    <section class="tower-specialization" style="--branch:${tower.color}"><header><div>${icon(tower.icon, 36)}<h3>${tower.name}</h3></div><span>${["missile_round", "fighter_craft"].includes(tower.id) ? "UNIT SPECIALIZATION · NEW LAUNCHES" : "CLASS SPECIALIZATION"}</span></header><div class="base-stat-grid">${tower.skills
      .map((s) => {
        const rank = ranks[s.id] || 0;
        return `<article class="base-stat-card"><header><div><h3>${s.name}</h3><span>RANK ${rank} / ${s.max}</span></div></header><strong>${skillBonus(s, rank)}${s.unit === "%" ? "%" : ""}<small> ${s.unit === "%" ? "BONUS" : s.unit}</small></strong><p>${s.effect} per rank. ${s.detail || ""}</p><div class="stat-ranks" style="grid-template-columns:repeat(${s.max},1fr)" aria-label="${tower.name} ${s.name}: rank ${rank} of ${s.max}">${Array.from({ length: s.max }, (_, i) => `<i class="${i < rank ? "filled" : ""}"></i>`).join("")}</div><button class="secondary" data-action="tower-stat-buy" data-tower="${tower.id}" data-id="${s.id}" ${rank >= s.max || !xp.available ? "disabled" : ""}>${rank >= s.max ? "Maximum rank" : `Improve ${s.name} · 1 point`}</button></article>`;
      })
      .join("")}</div></section></div>
    <p class="stat-note">Tower specializations use their own mastery points, separate from base stats. Armor reduces hull damage; shields draw power for absorbed hits. Faster weapons and miners keep their normal cost per cycle. Bigger stores and drone reserves charge normally. Unit upgrades apply to newly manufactured missiles and fighters. Existing units keep their original stats.</p>
  </section>`;
}
