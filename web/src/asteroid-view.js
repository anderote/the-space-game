export function asteroidReadout(a, buildings, stats) {
  const remaining = Math.max(0, a.ore),
    initial = Math.max(
      remaining,
      Number.isFinite(a.maxOre) ? a.maxOre : remaining,
    );
  const miners = buildings.filter(
    (b) =>
      b.type === "miner" &&
      b.construction >= 1 &&
      Math.hypot(b.x - a.x, b.y - a.y) - a.radius <= stats(b).range,
  );
  return {
    remaining,
    initial,
    harvested: initial - remaining,
    percent: initial ? (100 * remaining) / initial : 0,
    miners: miners.length,
    active: miners.filter(
      (b) =>
        b.activity > 0 &&
        (b.miningTargetIds || [b.miningTarget]).includes(a.id),
    ).length,
  };
}
export function asteroidView(a, readout, fmt) {
  return `<div class="eyebrow">ASTEROID SURVEY</div><h3>Mineral deposit</h3><div class="ore-count" id="asteroid-remaining">${fmt(readout.remaining)} MINERALS REMAINING</div><div class="progress-track"><i id="asteroid-fill" style="width:${readout.percent}%"></i></div><div class="stats-line" id="asteroid-harvested">${fmt(readout.harvested)} / ${fmt(readout.initial)} MINERALS EXTRACTED</div><div class="stats-line" id="asteroid-miners">${readout.miners} MINERS IN REACH · ${readout.active} ACTIVE BEAMS</div><p>Upgrade nearby miners to work up to four deposits per cycle. Every beam needs energy. Depleted asteroids clear space for new power routes.</p>`;
}
