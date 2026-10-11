export class Sound {
  constructor() {
    this.enabled = true;
    this.context = null;
    this.lastShot = 0;
  }
  unlock() {
    if (!this.context) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.context = new AudioContext();
    }
    if (this.context.state === "suspended") this.context.resume();
  }
  play(type) {
    if (!this.enabled || !this.context) return;
    const c = this.context,
      t = c.currentTime;
    if (type === "shot" && t - this.lastShot < 0.12) return;
    if (type === "shot") this.lastShot = t;
    const presets = {
      build: [460, 720, 0.1, 0.03],
      upgrade: [440, 880, 0.24, 0.035],
      recycle: [320, 140, 0.12, 0.03],
      shot: [200, 70, 0.1, 0.012],
      explosion: [65, 22, 0.38, 0.045],
      wave: [180, 160, 0.42, 0.035],
      won: [430, 860, 0.65, 0.05],
      lost: [180, 50, 0.8, 0.04],
      click: [420, 510, 0.045, 0.018],
    };
    const p = presets[type];
    if (!p) return;
    const o = c.createOscillator(),
      g = c.createGain();
    o.type =
      type === "explosion" ? "sawtooth" : type === "shot" ? "triangle" : "sine";
    o.frequency.setValueAtTime(p[0], t);
    o.frequency.exponentialRampToValueAtTime(p[1], t + p[2]);
    g.gain.setValueAtTime(p[3], t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + p[2]);
    o.connect(g);
    g.connect(c.destination);
    o.start(t);
    o.stop(t + p[2]);
  }
}
