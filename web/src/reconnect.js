// Repair only powerless branches; preserve healthy cables and normal placement rules.
const distributor = (b) => ["relay", "solar", "battery"].includes(b.type);
const eligible = (b) => b.hp > 0 && b.type !== "station";
const complete = (b) => eligible(b) && b.construction >= 1;
export function reconnectNetwork(buildings, existing, { canLink, maxLinks }) {
  const byId = new Map(buildings.map((b) => [b.id, b]));
  let links = [...existing];
  const reachable = () => {
    const seen = new Set(),
      queue = buildings.filter(
        (b) =>
          complete(b) &&
          (b.type === "solar" || (b.type === "battery" && b.energy > 0)),
      );
    for (const b of queue) seen.add(b.id);
    for (let i = 0; i < queue.length; i++) {
      const b = queue[i];
      if (!distributor(b) || !complete(b)) continue;
      for (const edge of links) {
        const id = edge.a === b.id ? edge.b : edge.b === b.id ? edge.a : null,
          n = byId.get(id);
        if (n && eligible(n) && !seen.has(id)) {
          seen.add(id);
          queue.push(n);
        }
      }
    }
    return seen;
  };
  let powered = reachable();
  if (
    !powered.size ||
    buildings.every((b) => !eligible(b) || powered.has(b.id))
  )
    return links;
  const degree = (id) =>
    links.reduce((n, l) => n + (l.a === id || l.b === id ? 1 : 0), 0);
  const candidates = [];
  for (let i = 0; i < buildings.length; i++)
    for (let j = i + 1; j < buildings.length; j++) {
      const a = buildings[i],
        b = buildings[j];
      // Powered nodes remain powered throughout this pass; only candidates
      // touching an orphan can help. Avoid geometry scans across healthy grids.
      const aOn = powered.has(a.id),
        bOn = powered.has(b.id);
      if ((aOn && bOn) || (aOn && !distributor(a)) || (bOn && !distributor(b)))
        continue;
      if (eligible(a) && eligible(b) && canLink(a, b))
        candidates.push({
          a,
          b,
          d: Math.hypot(a.x - b.x, a.y - b.y),
          branch: distributor(a) && distributor(b) ? 0 : 1,
        });
    }
  candidates.sort(
    (a, b) =>
      a.branch - b.branch || a.d - b.d || a.a.id - b.a.id || a.b.id - b.b.id,
  );
  let changed = true;
  while (changed) {
    changed = false;
    for (const pair of candidates) {
      const aOn = powered.has(pair.a.id),
        bOn = powered.has(pair.b.id);
      if (aOn === bOn) continue;
      const donor = aOn ? pair.a : pair.b,
        orphan = aOn ? pair.b : pair.a;
      if (
        !distributor(donor) ||
        !complete(donor) ||
        degree(donor.id) >= maxLinks(donor) ||
        maxLinks(orphan) < 1
      )
        continue;
      if (degree(orphan.id) >= maxLinks(orphan)) {
        const old = links
          .filter(
            (e) =>
              (e.a === orphan.id || e.b === orphan.id) &&
              !powered.has(e.a === orphan.id ? e.b : e.a),
          )
          .sort((a, b) => {
            const distance = (e) => {
              const n = byId.get(e.a === orphan.id ? e.b : e.a);
              return Math.hypot(n.x - orphan.x, n.y - orphan.y);
            };
            return distance(b) - distance(a);
          })[0];
        if (!old) continue;
        links = links.filter((e) => e !== old);
      }
      links.push({ a: donor.id, b: orphan.id });
      powered = reachable();
      changed = true;
    }
  }
  return links;
}
