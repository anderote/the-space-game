// Authored campaign pacing and formations. Bearings use world coordinates:
// zero is east, pi/2 north. Stateless bearings keep previews and spawns identical.
export const approachAngle = (mission, wave) =>
  (((mission.seed * 17 + wave * 137) % 360) * Math.PI) / 180;
export function bearingLabel(angle) {
  const names = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"];
  return names[((Math.round(angle / (Math.PI / 4)) % 8) + 8) % 8];
}
const group = (type, count, offset = 0) => ({ type, count, offset });
const F = (n, o = 0) => group("fighter", n, o),
  S = (n, o = 0) => group("swarm", n, o),
  R = (n, o = 0) => group("ring", n, o),
  B = (n, o = 0) => group("bomber", n, o),
  X = (n, o = 0) => group("suicide", n, o),
  M = (n, o = 0) => group("mothership", n, o);
const profiles = [
  {
    time: 210,
    goal: 600,
    budget: 500,
    gap: 45,
    formations: [[F(2)], [F(3)], [S(5)], [F(4), S(3)]],
    theme: "Prospector raids",
  },
  {
    time: 270,
    goal: 1200,
    budget: 700,
    gap: 48,
    formations: [
      [F(3)],
      [S(6)],
      [F(3), F(2, Math.PI)],
      [F(4), S(5)],
      [R(1), F(4)],
    ],
    theme: "Outer-deposit ambushes",
  },
  {
    time: 330,
    gap: 48,
    formations: [
      [F(4)],
      [S(8)],
      [R(1), F(4)],
      [F(4), S(6, Math.PI)],
      [R(2), S(6)],
      [F(7), R(2)],
    ],
    theme: "Raider escalation",
  },
  {
    time: 390,
    gap: 48,
    formations: [
      [F(4)],
      [R(2)],
      [S(10)],
      [B(2), F(5)],
      [R(2), F(5, Math.PI)],
      [B(3), S(8)],
      [R(3), B(2), F(6)],
    ],
    theme: "Energy siege",
  },
  {
    time: 420,
    gap: 52,
    formations: [
      [F(4)],
      [S(8)],
      [R(2), F(4)],
      [B(2), F(4)],
      [F(5), S(8, Math.PI)],
      [R(3), B(2)],
      [B(3), F(7), S(6)],
    ],
    theme: "Rescue corridor",
  },
  {
    time: 450,
    gap: 48,
    formations: [
      [S(8)],
      [S(12)],
      [F(5), S(8)],
      [S(8), S(8, Math.PI)],
      [R(2), S(12)],
      [B(3), S(10)],
      [X(3), S(14)],
      [R(3), S(18)],
    ],
    theme: "Swarm fronts",
  },
  {
    time: 480,
    gap: 52,
    formations: [
      [F(5)],
      [R(2), F(4)],
      [B(3)],
      [M(1), F(6)],
      [S(12), R(2)],
      [B(3), X(3, Math.PI)],
      [R(3), F(6)],
      [M(1), B(3), S(10)],
    ],
    goal: 2,
    theme: "Capital pursuit",
  },
  {
    time: 510,
    goal: 5000,
    gap: 50,
    formations: [
      [F(5)],
      [S(10)],
      [B(3)],
      [R(3), F(5)],
      [F(6), B(2, Math.PI)],
      [X(4), S(10)],
      [R(3), S(12)],
      [B(4), F(7)],
      [M(1), R(2), F(6)],
    ],
    theme: "Fractured perimeter",
  },
  {
    time: 540,
    gap: 52,
    formations: [
      [F(6)],
      [B(3)],
      [S(12)],
      [R(3), F(5)],
      [X(4), B(2)],
      [F(6), F(6, Math.PI)],
      [M(1), S(10)],
      [R(4), B(3)],
      [M(1), B(3), X(4)],
    ],
    theme: "Jump-drive blockade",
  },
  {
    time: 570,
    gap: 51,
    formations: [
      [F(6)],
      [S(12)],
      [B(3), R(2)],
      [X(4), F(5)],
      [R(4)],
      [B(4), S(10, Math.PI)],
      [S(16), X(4)],
      [M(1), F(6)],
      [R(4), B(4)],
      [M(1), S(14), X(4)],
    ],
    theme: "Storm hunters",
  },
  {
    time: 600,
    goal: 6500,
    gap: 54,
    formations: [
      [F(6)],
      [R(3)],
      [B(3), S(10)],
      [X(4), F(6)],
      [R(3), B(3, Math.PI)],
      [M(1), S(10)],
      [S(18)],
      [B(4), X(4)],
      [R(4), F(8)],
      [M(1), B(4), S(12)],
    ],
    theme: "Reserve interdiction",
  },
  {
    time: 660,
    gap: 50,
    formations: [
      [F(7)],
      [R(3), S(10)],
      [B(4), F(5)],
      [M(1), F(7)],
      [X(5), S(12)],
      [R(4), B(3)],
      [F(8), S(12, Math.PI)],
      [M(1), B(4)],
      [R(4), X(5)],
      [S(20), B(3)],
      [R(4), B(4), F(7)],
      [M(1), R(3), X(5)],
    ],
    theme: "Three capital offensives",
  },
];
export function expandExpedition(m, id) {
  const p = profiles[id];
  return {
    ...m,
    goal: p.goal ?? (["survive", "defend"].includes(m.kind) ? p.time : m.goal),
    minerals: p.budget ?? m.minerals,
    firstWave: id === 0 ? 65 : 55,
    waveGap: p.gap,
    waves: p.formations.length,
    minDuration: p.time,
    requireWaves: true,
    par: p.time + 120,
    waveTheme: p.theme,
    brief:
      m.brief +
      " " +
      p.theme +
      ": complete the objective and defeat every incoming wave.",
    wavePlan: p.formations.map((groups, i) => ({
      name: `${p.theme} ${i + 1}`,
      groups,
      gap: p.gap + (i % 3 === 1 ? 10 : 0),
      angle: approachAngle(m, i + 1),
    })),
  };
}
