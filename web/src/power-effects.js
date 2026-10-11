// A busy backbone can carry dozens of simultaneous transfers over the same
// edge. Draw one combined arc per edge, preserving direction, load and lifetime.
export function collectPowerSegments(flows) {
  const edges = new Map();
  for (const flow of flows) {
    if (flow.life <= 0) continue;
    for (let i = 1; i < flow.path.length; i++) {
      const a = flow.path[i - 1],
        b = flow.path[i];
      const key = a < b ? `${a}:${b}` : `${b}:${a}`;
      const existing = edges.get(key);
      if (existing) {
        existing.amount += flow.amount;
        if (flow.life > existing.life)
          Object.assign(existing, {
            a,
            b,
            life: flow.life,
            maxLife: flow.maxLife,
          });
      } else
        edges.set(key, {
          a,
          b,
          amount: flow.amount,
          life: flow.life,
          maxLife: flow.maxLife,
        });
    }
  }
  return [...edges.values()];
}
