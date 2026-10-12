export const MODERN_FLEET_MULTIPLIER = 5;
export const MISSILE_HULL = 20;
export const MISSILE_FUEL = 8;
export const POINT_DEFENSE = {
  ring: { range: 100, interval: 1.1, damage: 10 },
  mothership: { range: 160, interval: 0.7, damage: 10 },
};
const wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));
export function advanceMissile(p, target, dt) {
  // Facing follows guidance, while velocity follows thrust with lateral inertia.
  p.angle ??= target ? Math.atan2(target.y - p.y, target.x - p.x) : 0;
  p.vx ??= Math.cos(p.angle) * Math.min(60, p.speed);
  p.vy ??= Math.sin(p.angle) * Math.min(60, p.speed);
  if (target) {
    const desired = Math.atan2(target.y - p.y, target.x - p.x);
    const turn = Math.max(
      -1.6 * dt,
      Math.min(1.6 * dt, wrap(desired - p.angle)),
    );
    p.angle = wrap(p.angle + turn);
  }
  const speed = Math.min(p.speed, Math.hypot(p.vx, p.vy) + 100 * dt);
  const steering = 1 - Math.exp(-3 * dt);
  p.vx += (Math.cos(p.angle) * speed - p.vx) * steering;
  p.vy += (Math.sin(p.angle) * speed - p.vy) * steering;
  // Thrust accelerates along current velocity; steering cannot instantly reverse it.
  const magnitude = Math.hypot(p.vx, p.vy) || 1;
  p.vx *= speed / magnitude;
  p.vy *= speed / magnitude;
  const from = { x: p.x, y: p.y };
  p.trailClock = (p.trailClock || 0) + dt;
  if (p.trailClock >= 0.075) {
    p.trailClock %= 0.075;
    p.trail ??= [];
    p.trail.push(from);
    if (p.trail.length > 8) p.trail.shift();
  }
  p.x += p.vx * dt;
  p.y += p.vy * dt;
  return from;
}
export function sweptHit(from, to, target, radius) {
  const dx = to.x - from.x,
    dy = to.y - from.y;
  const along = Math.max(
    0,
    Math.min(
      1,
      ((target.x - from.x) * dx + (target.y - from.y) * dy) /
        (dx * dx + dy * dy || 1),
    ),
  );
  return (
    Math.hypot(
      target.x - from.x - along * dx,
      target.y - from.y - along * dy,
    ) <= radius
  );
}
