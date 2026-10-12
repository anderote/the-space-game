import { shieldCapacity } from "./shield-modules.js";
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { collectPowerSegments } from "./power-effects.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { BUILDINGS, ENEMIES } from "./content.js";
import { createNebula, rockMaps, hullTexture } from "./space-materials.js";
import { rng, stats, placementRadius, asteroidRadius } from "./engine.js";
import { ENEMY_SCALE, solarPetals } from "./structure-upgrades.js";
const TAU = Math.PI * 2;
function texture(kind) {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const x = c.getContext("2d"),
    random = rng(767);
  if (kind === "solar") {
    x.fillStyle = "#193d63";
    x.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 8; i++)
      for (let j = 0; j < 12; j++) {
        const l = 22 + random() * 20;
        x.fillStyle = `hsl(213,52%,${l}%)`;
        x.fillRect(i * 32 + 2, j * 22 + 2, 28, 18);
        x.fillStyle = "#7a9cba";
        x.fillRect(i * 32 + 14, j * 22 + 3, 1, 16);
      }
  } else {
    x.fillStyle = "#6b6561";
    x.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 12000; i++) {
      const v = 40 + random() * 115;
      x.fillStyle = `rgba(${v},${v * 0.93},${v * 0.86},${random() * 0.5})`;
      const s = 1 + random() * 5;
      x.fillRect(random() * 256, random() * 256, s, s);
    }
    for (let i = 0; i < 75; i++) {
      const a = random() * 256,
        b = random() * 256,
        r = 2 + random() * 15;
      const g = x.createRadialGradient(a - r / 3, b - r / 3, 0, a, b, r);
      g.addColorStop(0, "#4d474270");
      g.addColorStop(0.7, "#37363065");
      g.addColorStop(1, "#b1a79a15");
      x.fillStyle = g;
      x.beginPath();
      x.arc(a, b, r, 0, TAU);
      x.fill();
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
function nebulaTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 1024;
  const x = c.getContext("2d"),
    random = rng(67261);
  x.fillStyle = "#03080d";
  x.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 80; i++) {
    const a = random() * 1024,
      b = random() * 1024,
      r = 60 + random() * 370;
    const g = x.createRadialGradient(a, b, 0, a, b, r);
    const color =
      i % 3 === 0 ? "35,42,72" : i % 3 === 1 ? "20,63,65" : "29,46,67";
    g.addColorStop(0, `rgba(${color},0.15)`);
    g.addColorStop(1, `rgba(${color},0)`);
    x.fillStyle = g;
    x.fillRect(0, 0, 1024, 1024);
  }
  for (let i = 0; i < 1600; i++) {
    const a = random() * 1024,
      b = random() * 1024,
      v = random();
    x.fillStyle = `rgba(185,211,229,${v * 0.45})`;
    x.beginPath();
    x.arc(a, b, v > 0.985 ? 1.3 : 0.35 + v * 0.4, 0, TAU);
    x.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(4, 4);
  return t;
}
export class SpaceRenderer {
  constructor(container, overlay) {
    this.container = container;
    this.overlay = overlay;
    this.ctx = overlay.getContext("2d");
    this.width = innerWidth;
    this.height = innerHeight;
    this.cameraX = 0;
    this.cameraY = 0;
    this.zoom = 1.35;
    this.objects = new Map();
    this.enemyTemplates = new Map();
    this.sim = null;
    this.accent = "#87ebcc";
    this.reducedMotion = false;
    this.quality = "high";
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.setSize(this.width, this.height);
    this.renderer.setClearColor(0x050b12);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    container.append(this.renderer.domElement);
    this.scene = new THREE.Scene();
    const environment = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.environmentTexture = pmrem.fromScene(environment, 0.04).texture;
    this.scene.environment = this.environmentTexture;
    this.scene.environmentIntensity = 0.5;
    environment.dispose();
    pmrem.dispose();
    this.flashLights = Array.from({ length: 6 }, () => {
      const l = new THREE.PointLight(0xffffff, 0, 130, 2);
      this.scene.add(l);
      return l;
    });
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 6000);
    this.camera.position.set(0, 0, 1800);
    this.camera.up.set(0, 1, 0);
    this.camera.lookAt(0, 0, 0);
    this.scene.add(new THREE.AmbientLight(0x8caaca, 0.75));
    const sun = new THREE.DirectionalLight(0xffe9c9, 3.2);
    sun.position.set(-250, 350, 600);
    this.scene.add(sun);
    const rim = new THREE.DirectionalLight(0x409fcd, 2.4);
    rim.position.set(200, -100, 250);
    this.scene.add(rim);
    this.nebula = createNebula();
    this.scene.add(this.nebula);
    this.materials = {
      hull: new THREE.MeshStandardMaterial({
        map: hullTexture(),
        color: 0x6d91a8,
        metalness: 0.82,
        roughness: 0.34,
      }),
      dark: new THREE.MeshStandardMaterial({
        color: 0x132534,
        metalness: 0.75,
        roughness: 0.48,
      }),
      edge: new THREE.MeshStandardMaterial({
        color: 0x9eb8c5,
        metalness: 0.72,
        roughness: 0.26,
      }),
      solar: new THREE.MeshStandardMaterial({
        map: texture("solar"),
        metalness: 0.62,
        roughness: 0.3,
        emissive: 0x082847,
        emissiveIntensity: 0.25,
      }),
      rock: new THREE.MeshStandardMaterial({
        map: texture("rock"),
        color: 0x87908b,
        roughness: 0.97,
        metalness: 0.12,
        ...rockMaps(),
      }),
    };
    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.bloom = new UnrealBloomPass(
      new THREE.Vector2(this.width, this.height),
      0.38,
      0.45,
      1.6,
    );
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());
    this.resize();
  }
  resize() {
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;
    const dpr = Math.min(devicePixelRatio, 2);
    const renderDpr = this.quality === "high" ? dpr : 1;
    this.overlay.width = this.width * dpr;
    this.overlay.height = this.height * dpr;
    this.overlay.style.width = this.width + "px";
    this.overlay.style.height = this.height + "px";
    this.renderer.setPixelRatio(renderDpr);
    this.composer.setPixelRatio(renderDpr);
    this.renderer.setSize(this.width, this.height);
    this.composer.setSize(this.width, this.height);
    this.updateCamera();
  }
  updateCamera() {
    const w = this.width / this.zoom,
      h = this.height / this.zoom;
    Object.assign(this.camera, {
      left: -w / 2,
      right: w / 2,
      top: h / 2,
      bottom: -h / 2,
    });
    this.camera.position.set(this.cameraX, this.cameraY, 1800);
    this.camera.updateProjectionMatrix();
  }
  screenToWorld(x, y) {
    return {
      x: (x - this.width / 2) / this.zoom + this.cameraX,
      y: (this.height / 2 - y) / this.zoom + this.cameraY,
    };
  }
  worldToScreen(x, y) {
    return {
      x: (x - this.cameraX) * this.zoom + this.width / 2,
      y: this.height / 2 - (y - this.cameraY) * this.zoom,
    };
  }
  pan(dx, dy) {
    this.cameraX -= dx / this.zoom;
    this.cameraY += dy / this.zoom;
    this.updateCamera();
  }
  setZoom(value, x = this.width / 2, y = this.height / 2) {
    const before = this.screenToWorld(x, y);
    this.zoom = Math.max(0.42, Math.min(3.2, value));
    const after = this.screenToWorld(x, y);
    this.cameraX += before.x - after.x;
    this.cameraY += before.y - after.y;
    this.updateCamera();
  }
  center() {
    this.cameraX = 0;
    this.cameraY = 0;
    this.zoom = Math.max(0.8, Math.min(1.7, this.height / 510));
    this.updateCamera();
  }
  glow(color, strength = 2) {
    return new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: strength,
      roughness: 0.4,
      metalness: 0.3,
    });
  }
  mesh(group, geometry, material, x = 0, y = 0, z = 0) {
    const o = new THREE.Mesh(geometry, material);
    o.position.set(x, y, z);
    group.add(o);
    return o;
  }
  cylinder(group, r, h, material, x = 0, y = 0, z = 0, segments = 12) {
    const o = this.mesh(
      group,
      new THREE.CylinderGeometry(r * 0.92, r, h, segments),
      material,
      x,
      y,
      z,
    );
    o.rotation.x = Math.PI / 2;
    return o;
  }
  rock(a) {
    const group = new THREE.Group(),
      random = rng(a.seed);
    const geo = new THREE.IcosahedronGeometry(a.radius, 2);
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const vx = p.getX(i),
        vy = p.getY(i),
        vz = p.getZ(i);
      const f =
        0.9 +
        0.12 * Math.sin(vx * 0.5 + vy * 0.3) * Math.cos(vz * 0.4) +
        0.08 * Math.sin(vy * 1.1);
      p.setXYZ(i, vx * f, vy * f, vz * f * 0.7);
    }
    geo.computeVertexNormals();
    const main = this.mesh(group, geo, this.materials.rock);
    main.rotation.set(0.2, a.rotation, 0.3);
    group.rotation.z = a.rotation;
    for (let i = 0; i < 5; i++) {
      const theta = random() * TAU,
        rr = a.radius * (0.2 + random() * 0.55);
      this.mesh(
        group,
        new THREE.DodecahedronGeometry(1 + random() * 2, 0),
        this.glow("#a0bd8c", 0.3),
        Math.cos(theta) * rr,
        Math.sin(theta) * rr,
        a.radius * 0.58,
      );
    }
    group.position.set(a.x, a.y, -5);
    return group;
  }
  structure(b) {
    const g = new THREE.Group(),
      d = BUILDINGS[b.type],
      m = this.materials,
      r = d.radius / (d.visualScale || 1);
    g.userData.type = b.type;
    const minimal = b.type === "repair";
    this.cylinder(g, r * 0.92, minimal ? 2 : 5, m.dark, 0, 0, 1);
    this.cylinder(g, r * 0.74, minimal ? 2 : 3, m.hull, 0, 0, minimal ? 3 : 5);
    for (let i = 0; !minimal && i < 4; i++) {
      const a = (i * TAU) / 4 + Math.PI / 4;
      this.cylinder(
        g,
        1,
        1,
        m.edge,
        Math.cos(a) * r * 0.7,
        Math.sin(a) * r * 0.7,
        7,
        5,
      );
    }
    if (!minimal)
      this.mesh(
        g,
        new THREE.TorusGeometry(r * 0.88, 0.5, 5, 24),
        m.edge,
        0,
        0,
        4,
      );
    const glow = this.glow(d.color, 1.8);
    g.userData.lights = [];
    const core = (rad, z = 8) => {
      const o = this.cylinder(g, rad, 3, glow, 0, 0, z);
      g.userData.lights.push(o);
      return o;
    };
    if (b.type === "solar") {
      const petals = solarPetals(b.level);
      const shape = new THREE.Shape();
      shape.moveTo(6, -2);
      shape.bezierCurveTo(12, -3, 19, -8, 24, -4.5);
      shape.quadraticCurveTo(28, -2.5, 28, 0);
      shape.quadraticCurveTo(28, 2.5, 24, 4.5);
      shape.bezierCurveTo(19, 8, 12, 3, 6, 2);
      shape.closePath();
      const frameGeometry = new THREE.ExtrudeGeometry(shape, {
        depth: 1.6,
        bevelEnabled: true,
        bevelSize: 0.3,
        bevelThickness: 0.3,
        bevelSegments: 1,
        curveSegments: 8,
        steps: 1,
      });
      const panelGeometry = new THREE.ShapeGeometry(shape, 8);
      const positions = panelGeometry.attributes.position;
      const uv = panelGeometry.attributes.uv;
      for (let i = 0; i < uv.count; i++)
        uv.setXY(i, positions.getX(i) / 28, positions.getY(i) / 16 + 0.5);
      for (let i = 0; i < petals; i++) {
        const petal = new THREE.Group();
        petal.name = `solar-petal-${i + 1}`;
        petal.rotation.z = (i * TAU) / petals + Math.PI / 6;
        this.mesh(petal, new THREE.BoxGeometry(19, 1.5, 2), m.hull, 12, 0, 5);
        this.mesh(petal, frameGeometry, m.edge, 0, 0, 6);
        const panel = this.mesh(petal, panelGeometry, m.solar, 1.1, 0, 7.95);
        panel.scale.set(0.93, 0.83, 1);
        this.mesh(
          petal,
          new THREE.BoxGeometry(15, 0.45, 0.3),
          m.edge,
          17,
          0,
          8.2,
        );
        g.add(petal);
      }
      this.cylinder(g, 6, 9, m.edge, 0, 0, 8);
      core(2.4, 14);
    } else if (b.type === "relay") {
      this.cylinder(g, 4.2, 8, m.edge, 0, 0, 6);
      core(2.5, 11);
      for (let i = 0; i < 3; i++) {
        const a = (i * TAU) / 3;
        this.mesh(
          g,
          new THREE.SphereGeometry(1.8, 6, 6),
          glow,
          Math.cos(a) * 7,
          Math.sin(a) * 7,
          4,
        );
      }
    } else if (b.type === "miner") {
      this.mesh(g, new THREE.BoxGeometry(16, 10, 6), m.edge, 0, 0, 8);
      const turret = new THREE.Group();
      turret.position.z = 12;
      this.mesh(turret, new THREE.BoxGeometry(16, 4, 3), m.hull, 6, 0, 0);
      this.mesh(turret, new THREE.BoxGeometry(4, 5, 4), glow, 15, 0, 0);
      g.add(turret);
      g.userData.turret = turret;
      core(4, 14);
    } else if (b.type === "battery") {
      for (const s of [-1, 1]) {
        this.mesh(g, new THREE.BoxGeometry(8, 22, 7), m.edge, s * 7, 0, 9);
        const o = this.mesh(
          g,
          new THREE.BoxGeometry(5, 19, 1),
          glow,
          s * 7,
          0,
          13,
        );
        g.userData.lights.push(o);
      }
      this.mesh(g, new THREE.BoxGeometry(5, 26, 4), m.hull, 0, 0, 7);
    } else if (b.type === "repair") {
      core(3, 5);
      for (let i = 0; i < 4; i++) {
        const a = (i * Math.PI) / 2;
        this.cylinder(
          g,
          2.6,
          2,
          m.edge,
          Math.cos(a) * 8,
          Math.sin(a) * 8,
          4,
          8,
        );
        this.cylinder(
          g,
          1.3,
          0.6,
          glow,
          Math.cos(a) * 8,
          Math.sin(a) * 8,
          5.3,
          6,
        );
      }
    } else if (b.type === "laser" || b.type === "thel") {
      const t = new THREE.Group();
      t.position.z = 10;
      this.cylinder(t, r * 0.48, 6, m.edge, 0, 0, 0, 8);
      for (const side of b.type === "thel" ? [-1, 1] : [0]) {
        this.mesh(
          t,
          new THREE.BoxGeometry(r, 3, 4),
          m.hull,
          r * 0.7,
          side * 4,
          3,
        );
        this.mesh(
          t,
          new THREE.BoxGeometry(3, 3.5, 4.5),
          glow,
          r * 1.2,
          side * 4,
          3,
        );
      }
      g.add(t);
      g.userData.turret = t;
      core(r * 0.23, 17);
    } else if (b.type === "missile") {
      for (const s of [-1, 1]) {
        this.mesh(g, new THREE.BoxGeometry(10, 16, 7), m.edge, s * 9, 0, 9);
        for (let i = 0; i < 3; i++)
          this.cylinder(g, 2, 2, glow, s * 9, (i - 1) * 4, 14, 6);
      }
      core(4, 12);
    } else if (b.type === "station") {
      this.cylinder(g, 25, 12, m.edge, 0, 0, 8);
      this.mesh(g, new THREE.TorusGeometry(32, 5, 6, 8), m.hull, 0, 0, 4);
      core(12, 16);
      for (const s of [-1, 1]) {
        this.mesh(g, new THREE.BoxGeometry(14, 45, 2), m.solar, s * 43, 0, 4);
        this.mesh(g, new THREE.BoxGeometry(48, 3, 4), m.edge, s * 23, 0, 2);
      }
    }
    const tierLight = b.level > 1 ? this.glow("#fbebad", 1.7) : null;
    for (let i = 0; i < b.level - 1; i++)
      this.mesh(
        g,
        new THREE.BoxGeometry(2.6, 2, 1),
        tierLight,
        (i - (b.level - 2) / 2) * 5,
        -r * 0.8,
        7,
      );
    if (["relay", "solar", "battery", "repair", "missile"].includes(b.type))
      this.batchStructure(g);
    g.scale.setScalar(d.visualScale || 1);
    g.position.set(b.x, b.y, 4);
    return g;
  }
  batchStructure(group) {
    const batches = new Map();
    const originals = new Set();
    const lightMaterials = new Set(
      group.userData.lights.map((o) => o.material),
    );
    group.updateMatrixWorld(true);
    group.traverse((mesh) => {
      if (!mesh.isMesh) return;
      // Extruded solar frames are non-indexed; normalize before merging them
      // with indexed bolts and struts, preserving every material and UV.
      const geometry = (
        mesh.geometry.index
          ? mesh.geometry.toNonIndexed()
          : mesh.geometry.clone()
      ).applyMatrix4(mesh.matrixWorld);
      if (!batches.has(mesh.material)) batches.set(mesh.material, []);
      batches.get(mesh.material).push(geometry);
      originals.add(mesh.geometry);
    });
    group.clear();
    originals.forEach((geometry) => geometry.dispose());
    group.userData.lights = [];
    for (const [material, geometries] of batches) {
      const merged = mergeGeometries(geometries);
      geometries.forEach((g) => g.dispose());
      const mesh = this.mesh(group, merged, material);
      mesh.matrixAutoUpdate = false;
      if (lightMaterials.has(material)) group.userData.lights.push(mesh);
    }
  }
  enemy(e) {
    const group = new THREE.Group(),
      d = ENEMIES[e.type],
      m = this.materials;
    const shell = new THREE.MeshStandardMaterial({
      color: e.type === "mothership" ? 0x53445e : 0x624347,
      metalness: 0.7,
      roughness: 0.4,
    });
    const light = this.glow(d.color, 2.5);
    if (e.type === "ring") {
      this.mesh(
        group,
        new THREE.TorusGeometry(d.radius * 0.8, 3.4, 6, 12),
        shell,
        0,
        0,
        5,
      );
      this.mesh(
        group,
        new THREE.TorusGeometry(d.radius * 0.77, 0.7, 4, 18),
        light,
        0,
        0,
        8,
      );
    } else if (e.type === "mothership") {
      const body = this.mesh(
        group,
        new THREE.OctahedronGeometry(d.radius, 0),
        shell,
        0,
        0,
        10,
      );
      body.scale.set(1.4, 0.6, 0.4);
      for (const s of [-1, 1])
        this.mesh(
          group,
          new THREE.BoxGeometry(35, 6, 7),
          m.edge,
          -4,
          s * 20,
          4,
        );
      this.mesh(group, new THREE.BoxGeometry(25, 4, 2), light, 0, 0, 21);
    } else {
      const shape = new THREE.Shape();
      shape.moveTo(d.radius, 0);
      shape.lineTo(-d.radius, d.radius * 0.7);
      shape.lineTo(-d.radius * 0.5, 0);
      shape.lineTo(-d.radius, -d.radius * 0.7);
      shape.closePath();
      this.mesh(
        group,
        new THREE.ExtrudeGeometry(shape, {
          depth: 4,
          bevelEnabled: true,
          bevelThickness: 1,
          bevelSize: 1,
          bevelSegments: 1,
        }),
        shell,
        0,
        0,
        5,
      );
    }
    this.mesh(
      group,
      new THREE.SphereGeometry(d.radius * 0.18, 6, 6),
      light,
      -d.radius * 0.7,
      0,
      7,
    );
    group.scale.setScalar(ENEMY_SCALE);
    return group;
  }
  disposeGroup(group) {
    if (group.userData.shared) {
      this.scene.remove(group);
      return;
    }
    group.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material && !Object.values(this.materials).includes(o.material))
        o.material.dispose();
    });
    this.scene.remove(group);
  }
  sync(sim) {
    if (sim !== this.sim) {
      for (const g of this.objects.values()) this.disposeGroup(g);
      this.objects.clear();
      this.sim = sim;
    }
    const alive = new Set();
    for (const a of sim.asteroids) {
      if (a.ore <= 0) continue;
      const key = "a" + a.id;
      alive.add(key);
      if (!this.objects.has(key)) {
        const obj = this.rock(a);
        this.objects.set(key, obj);
        this.scene.add(obj);
      }
      const g = this.objects.get(key);
      g.scale.setScalar(asteroidRadius(a) / a.radius);
    }
    for (const b of sim.buildings) {
      const key = "b" + b.id;
      alive.add(key);
      let g = this.objects.get(key);
      if (g && (g.userData.level !== b.level || g.userData.type !== b.type)) {
        this.disposeGroup(g);
        this.objects.delete(key);
        g = null;
      }
      if (!g) {
        g = this.structure(b);
        g.userData.level = b.level;
        this.objects.set(key, g);
        this.scene.add(g);
      }
      if (g.userData.turret) g.userData.turret.rotation.z = b.angle;
      g.scale.setScalar(
        (BUILDINGS[b.type].visualScale || 1) *
          (b.construction < 1 ? 0.65 + b.construction * 0.35 : 1),
      );
      for (const l of g.userData.lights || [])
        l.material.emissiveIntensity = b.powered
          ? 0.65 + b.activity * 0.5 + (b.powerPulse || 0) * 2.2
          : 0.08;
    }
    for (const e of sim.enemies) {
      const key = "e" + e.id;
      alive.add(key);
      let g = this.objects.get(key);
      if (!g) {
        let template = this.enemyTemplates.get(e.type);
        if (!template) {
          template = this.enemy(e);
          this.enemyTemplates.set(e.type, template);
        }
        g = template.clone(true);
        g.userData.shared = true;
        this.objects.set(key, g);
        this.scene.add(g);
      }
      g.position.set(e.x, e.y, 10);
      g.rotation.z = e.angle;
    }
    for (const [key, g] of this.objects)
      if (!alive.has(key)) {
        this.disposeGroup(g);
        this.objects.delete(key);
      }
  }
  render(sim, state, wallTime) {
    this.nebula.material.uniforms.uTime.value = this.reducedMotion
      ? 0
      : wallTime * 0.001;
    this.sync(sim);
    const flashes =
      this.quality === "high"
        ? sim.effects
            .filter((e) => e.type === "beam" || e.type === "explosion")
            .slice(-6)
        : [];
    for (let i = 0; i < this.flashLights.length; i++) {
      const l = this.flashLights[i],
        e = flashes[i];
      if (e) {
        l.color.set(e.color || "#ffbc79");
        l.position.set(e.toX ?? e.x, e.toY ?? e.y, 24);
        l.intensity =
          (e.type === "explosion" ? 750 : 300) * (e.life / e.maxLife);
      } else l.intensity = 0;
    }
    if (this.quality === "high") this.composer.render();
    else this.renderer.render(this.scene, this.camera);
    const c = this.ctx,
      dpr = this.overlay.width / this.width;
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.clearRect(0, 0, this.width, this.height);
    const p = (x, y) => this.worldToScreen(x, y);
    const line = (a, b, color, width = 1) => {
      c.strokeStyle = color;
      c.lineWidth = width;
      c.beginPath();
      c.moveTo(a.x, a.y);
      c.lineTo(b.x, b.y);
      c.stroke();
    };
    if (state.grid) {
      c.fillStyle = "#8bbaad22";
      const start = this.screenToWorld(0, this.height);
      const end = this.screenToWorld(this.width, 0);
      for (let x = Math.ceil(start.x / 40) * 40; x < end.x; x += 40)
        for (let y = Math.ceil(start.y / 40) * 40; y < end.y; y += 40) {
          const a = p(x, y);
          c.fillRect(a.x, a.y, 1.5, 1.5);
        }
    }
    const buildingIndex = new Map(sim.buildings.map((b) => [b.id, b]));
    const positions = new Map(sim.buildings.map((b) => [b.id, p(b.x, b.y)]));
    // Batch passive cables into just two canvas strokes.
    for (const powered of [false, true]) {
      c.strokeStyle = powered ? "#69bce767" : "#ce8b7250";
      c.lineWidth = powered ? 1.2 : 1;
      c.beginPath();
      for (const edge of sim.links) {
        const from = buildingIndex.get(edge.a),
          to = buildingIndex.get(edge.b);
        if (!from || !to || Boolean(from.powered && to.powered) !== powered)
          continue;
        const a = positions.get(edge.a),
          b = positions.get(edge.b);
        c.moveTo(a.x, a.y);
        c.lineTo(b.x, b.y);
      }
      c.stroke();
    }
    if (this.powerFrameSim !== sim || this.powerFrameTime !== sim.time) {
      this.powerFrameSim = sim;
      this.powerFrameTime = sim.time;
      this.powerSegments = collectPowerSegments(sim.flows || []);
    }
    for (const flow of this.powerSegments) {
      const a = positions.get(flow.a),
        b = positions.get(flow.b);
      if (!a || !b) continue;
      // Offscreen power arcs do not need canvas geometry or glow work.
      if (
        Math.max(a.x, b.x) < -20 ||
        Math.min(a.x, b.x) > this.width + 20 ||
        Math.max(a.y, b.y) < -20 ||
        Math.min(a.y, b.y) > this.height + 20
      )
        continue;
      const alpha =
        Math.min(1, flow.life / flow.maxLife + 0.15) *
        Math.min(1, 0.35 + Math.sqrt(flow.amount) * 0.4);
      const dx = b.x - a.x,
        dy = b.y - a.y,
        len = Math.hypot(dx, dy);
      if (len < 1e-6) continue;
      const segments = Math.min(18, Math.max(3, Math.floor(len / 10)));
      c.save();
      c.shadowBlur = 0;
      c.beginPath();
      c.moveTo(a.x, a.y);
      for (let j = 1; j < segments; j++) {
        const f = j / segments;
        const jitter = this.reducedMotion
          ? 0
          : Math.sin(j * 13.31 + Math.floor(sim.time * 28) * 4.9 + flow.a) *
            2.8 *
            this.zoom *
            Math.sin(f * Math.PI);
        c.lineTo(
          a.x + dx * f - (dy / len) * jitter,
          a.y + dy * f + (dx / len) * jitter,
        );
      }
      c.lineTo(b.x, b.y);
      // A broad translucent stroke supplies glow without a blur filter per arc.
      if (this.quality === "high") {
        c.globalAlpha = alpha * 0.2;
        c.strokeStyle = "#57cbf2";
        c.lineWidth = 4;
        c.stroke();
      }
      c.globalAlpha = alpha;
      c.strokeStyle = "#b9f4ff";
      c.lineWidth = 1.2;
      c.stroke();
      if (!this.reducedMotion) {
        const t = 1 - flow.life / flow.maxLife;
        c.fillStyle = "#e2fdff";
        c.beginPath();
        c.arc(a.x + dx * t, a.y + dy * t, 1.7 * this.zoom, 0, TAU);
        c.fill();
      }
      c.restore();
    }
    const selectedRock = sim.asteroids.find(
      (a) => a.id === state.selectedAsteroid,
    );
    if (selectedRock && selectedRock.ore > 0) {
      const at = p(selectedRock.x, selectedRock.y);
      c.strokeStyle = "#edc980";
      c.lineWidth = 1.5;
      c.beginPath();
      c.arc(at.x, at.y, asteroidRadius(selectedRock) * this.zoom + 5, 0, TAU);
      c.stroke();
    }
    for (const b of sim.buildings) {
      const a = p(b.x, b.y),
        r = BUILDINGS[b.type].radius * this.zoom;
      if (b.activity > 0 && (b.type === "miner" || b.type === "repair")) {
        const ids =
          b.type === "miner" ? b.miningTargetIds || [b.targetId] : [b.targetId];
        for (const id of ids) {
          const target =
            sim.asteroids.find((t) => t.id === id) ||
            sim.buildings.find((t) => t.id === id);
          if (target) {
            c.globalAlpha = 0.5 + Math.sin(wallTime * 0.03) * 0.15;
            line(
              a,
              p(target.x, target.y),
              b.type === "miner" ? "#d6cc88" : "#8df1c7",
              1.1,
            );
            c.globalAlpha = 1;
          }
        }
      }
      if (b.powerPulse > 0) {
        c.save();
        c.globalAlpha = b.powerPulse * 0.7;
        c.strokeStyle = "#9ceeff";
        c.lineWidth = 1.2;
        c.shadowColor = "#66d6f5";
        c.shadowBlur = 0;
        c.beginPath();
        c.arc(a.x, a.y, r + (1 - b.powerPulse) * 7, 0, TAU);
        c.stroke();
        c.restore();
      }
      if (b.construction < 1) {
        c.strokeStyle = "#9fdbe9";
        c.lineWidth = 2;
        c.beginPath();
        c.arc(
          a.x,
          a.y,
          r + 4,
          -Math.PI / 2,
          -Math.PI / 2 + TAU * b.construction,
        );
        c.stroke();
      }
      const shieldMax = shieldCapacity(b);
      if (shieldMax && b.shieldCharge > 0 && b.construction >= 1) {
        c.save();
        c.strokeStyle = "#79baff";
        c.globalAlpha = 0.25 + 0.35 * (b.shieldCharge / shieldMax);
        c.lineWidth = 1;
        c.beginPath();
        c.arc(
          a.x,
          a.y,
          r + 5,
          -Math.PI / 2,
          -Math.PI / 2 + (TAU * b.shieldCharge) / shieldMax,
        );
        c.stroke();
        c.restore();
      }
      if (b.shieldPulse > 0) {
        c.save();
        c.globalAlpha = b.shieldPulse * 0.8;
        c.strokeStyle = "#9edbff";
        c.lineWidth = 2;
        c.shadowColor = "#8dc6ff";
        c.shadowBlur = 0;
        c.beginPath();
        c.arc(a.x, a.y, r + 5, 0, TAU);
        c.stroke();
        c.restore();
      }
      if (b.hp < b.maxHp || state.selected === b.id) {
        c.fillStyle = "#091319";
        c.fillRect(a.x - 18, a.y + r + 6, 36, 3);
        c.fillStyle = b.hp / b.maxHp < 0.35 ? "#ff8674" : this.accent;
        c.fillRect(a.x - 18, a.y + r + 6, (36 * b.hp) / b.maxHp, 3);
      }
      if (!b.powered && b.type !== "station") {
        c.fillStyle = "#ed9c70";
        c.font = "11px monospace";
        c.textAlign = "center";
        c.fillText("!", a.x, a.y - r - 6);
      }
      if (state.selected === b.id) {
        this.ring(c, a, r + 7, this.accent, 1.5, wallTime);
        const s = stats(b);
        if (s.range)
          this.range(
            c,
            a,
            s.range * this.zoom,
            b.type === "miner" ? "#e9c97e" : "#a6dcca",
          );
        this.range(c, a, s.link * this.zoom, "#83bade", true);
      }
    }
    for (const d of sim.drones || []) {
      const a = p(d.x, d.y);
      c.fillStyle = "#a7f3c9";
      c.shadowColor = "#72d3ac";
      c.shadowBlur = 5;
      c.beginPath();
      c.moveTo(a.x, a.y - 3);
      c.lineTo(a.x + 3, a.y + 2);
      c.lineTo(a.x - 3, a.y + 2);
      c.closePath();
      c.fill();
      c.shadowBlur = 0;
      if (d.mode === "repair") {
        const target = sim.buildings.find((b) => b.id === d.targetId);
        if (target) line(a, p(target.x, target.y), "#8cebc780", 1);
      }
    }
    if (!this.reducedMotion)
      for (const e of sim.enemies) {
        const d = ENEMIES[e.type],
          a = p(
            e.x - Math.cos(e.angle) * d.radius * ENEMY_SCALE,
            e.y - Math.sin(e.angle) * d.radius * ENEMY_SCALE,
          ),
          b = p(
            e.x - Math.cos(e.angle) * (d.radius + 18) * ENEMY_SCALE,
            e.y - Math.sin(e.angle) * (d.radius + 18) * ENEMY_SCALE,
          );
        const g = c.createLinearGradient(a.x, a.y, b.x, b.y);
        g.addColorStop(0, d.color + "a0");
        g.addColorStop(1, d.color + "00");
        line(a, b, g, Math.max(2, d.radius * ENEMY_SCALE * 0.25 * this.zoom));
      }
    for (const e of sim.enemies) {
      if (e.intelValue) {
        const a = p(e.x, e.y),
          radius = ENEMIES[e.type].radius * ENEMY_SCALE * this.zoom + 7;
        if (
          a.x >= -50 &&
          a.x <= this.width + 50 &&
          a.y >= -50 &&
          a.y <= this.height + 50
        ) {
          c.strokeStyle = "#efcb76";
          c.lineWidth = 1;
          c.beginPath();
          c.moveTo(a.x, a.y - radius);
          c.lineTo(a.x + radius, a.y);
          c.lineTo(a.x, a.y + radius);
          c.lineTo(a.x - radius, a.y);
          c.closePath();
          c.stroke();
          c.font = '9px "SFMono-Regular",monospace';
          c.textAlign = "center";
          c.fillStyle = "#efcb76";
          c.fillText(
            `${e.rare ? "ELITE" : "COMMAND"} · ${e.intelValue} INTEL`,
            a.x,
            a.y - radius - 6,
          );
        }
      }
      if (e.shield > 0) {
        const a = p(e.x, e.y);
        this.range(
          c,
          a,
          ENEMIES[e.type].radius * ENEMY_SCALE * this.zoom + 4,
          "#e5cd72",
        );
      }
      if (e.hp < e.maxHp || e.type === "mothership") {
        const a = p(e.x, e.y),
          w = e.type === "mothership" ? 65 : 26;
        c.fillStyle = "#170d16";
        c.fillRect(
          a.x - w / 2,
          a.y + ENEMIES[e.type].radius * ENEMY_SCALE * this.zoom + 8,
          w,
          3,
        );
        c.fillStyle = "#fa887b";
        c.fillRect(
          a.x - w / 2,
          a.y + ENEMIES[e.type].radius * ENEMY_SCALE * this.zoom + 8,
          (w * e.hp) / e.maxHp,
          3,
        );
      }
    }
    for (const e of sim.effects) {
      const a = p(e.x, e.y),
        f = e.life / e.maxLife;
      c.globalAlpha = f;
      if (e.type === "intel") {
        c.fillStyle = "#ffe098";
        c.font = '12px "SFMono-Regular",monospace';
        c.textAlign = "center";
        c.fillText(`+${e.value} INTEL`, a.x, a.y - (1 - f) * 35);
      } else if (e.type === "beam") {
        const b = p(e.toX, e.toY);
        c.shadowColor = e.color;
        c.shadowBlur = e.heavy ? 13 : 7;
        line(a, b, e.color, e.heavy ? 3.2 : 1.7);
        line(a, b, "#ffffff", e.heavy ? 1.1 : 0.6);
        c.shadowBlur = 0;
      } else if (e.type === "explosion") {
        const radius = (e.size || 25) * this.zoom * (1 - f + 0.15);
        const g = c.createRadialGradient(a.x, a.y, 0, a.x, a.y, radius);
        g.addColorStop(0, "#fff8dc");
        g.addColorStop(0.2, e.color || "#ffa580");
        g.addColorStop(1, "#ff9a6800");
        c.fillStyle = g;
        c.beginPath();
        c.arc(a.x, a.y, radius, 0, TAU);
        c.fill();
        if (!this.reducedMotion) {
          for (let j = 0; j < 9; j++) {
            const angle = j * 2.399 + e.x,
              travel = (1 - f) * (e.size || 30) * this.zoom;
            const ax = a.x + Math.cos(angle) * travel,
              ay = a.y + Math.sin(angle) * travel;
            c.strokeStyle = e.color;
            c.lineWidth = 1;
            c.beginPath();
            c.moveTo(ax, ay);
            c.lineTo(
              ax + Math.cos(angle) * 6 * f,
              ay + Math.sin(angle) * 6 * f,
            );
            c.stroke();
          }
        }
      } else {
        c.fillStyle = e.color;
        c.beginPath();
        c.arc(a.x, a.y, 5 * this.zoom * f, 0, TAU);
        c.fill();
      }
      c.globalAlpha = 1;
    }
    for (const o of sim.projectiles) {
      if (o.delay > 0) continue;
      const a = p(o.x, o.y),
        b = p(o.x - Math.cos(o.angle) * 12, o.y - Math.sin(o.angle) * 12);
      c.shadowColor = o.friendly ? "#e2b9ff" : "#ff7e73";
      c.shadowBlur = 5;
      line(a, b, c.shadowColor, o.friendly ? 2 : 1.5);
      c.shadowBlur = 0;
    }
    if (state.buildType && state.mouse) {
      const world = state.mouse,
        d = stats({ type: state.buildType, level: 1, research: sim.rules }),
        a = p(world.x, world.y),
        check = sim.placement(state.buildType, world.x, world.y),
        color = check.ok
          ? check.powered
            ? this.accent
            : "#e4bd77"
          : "#ed8f7e";
      this.range(c, a, d.link * this.zoom, "#83bade", true);
      if (d.range)
        this.range(
          c,
          a,
          (d.range + (state.buildType === "miner" ? 20 : 0)) * this.zoom,
          d.color,
        );
      for (const b of check.links || []) line(a, p(b.x, b.y), color, 1.8);
      c.strokeStyle = color;
      c.fillStyle = check.ok ? "#87ebcc18" : "#ed8f7e18";
      c.lineWidth = 1.5;
      c.beginPath();
      c.arc(a.x, a.y, placementRadius(state.buildType) * this.zoom, 0, TAU);
      c.fill();
      c.stroke();
      line({ x: a.x - 5, y: a.y }, { x: a.x + 5, y: a.y }, color);
      line({ x: a.x, y: a.y - 5 }, { x: a.x, y: a.y + 5 }, color);
      c.font = '11px "SFMono-Regular",monospace';
      c.fillStyle = color;
      c.textAlign = "center";
      c.fillText(
        check.ok
          ? `${d.name.toUpperCase()} · ${d.cost} M${check.powered ? "" : " · AWAITING POWER"}`
          : check.reason,
        a.x,
        a.y + d.radius * this.zoom + 25,
      );
    }
  }
  range(c, a, r, color, dashed = false) {
    if (!r) return;
    c.save();
    c.globalAlpha = 0.35;
    c.strokeStyle = color;
    c.lineWidth = 1;
    if (dashed) c.setLineDash([4, 6]);
    c.beginPath();
    c.arc(a.x, a.y, r, 0, TAU);
    c.stroke();
    c.restore();
  }
  ring(c, a, r, color, width, time) {
    c.save();
    c.strokeStyle = color;
    c.lineWidth = width;
    for (let i = 0; i < 4; i++) {
      const angle = (i * Math.PI) / 2;
      c.beginPath();
      c.arc(a.x, a.y, r, angle + 0.13, angle + 0.6);
      c.stroke();
    }
    c.restore();
  }
  minimap(canvas, sim) {
    const c = canvas.getContext("2d"),
      w = canvas.width,
      h = canvas.height,
      s = Math.min(w, h) / (sim.mission.world * 1.25);
    c.clearRect(0, 0, w, h);
    c.fillStyle = "#030b1099";
    c.fillRect(0, 0, w, h);
    const point = (o) => ({ x: w / 2 + o.x * s, y: h / 2 - o.y * s });
    c.strokeStyle = "#40616c35";
    c.lineWidth = 1;
    for (let i = 1; i < 4; i++) {
      c.beginPath();
      c.moveTo((i * w) / 4, 0);
      c.lineTo((i * w) / 4, h);
      c.moveTo(0, (i * h) / 4);
      c.lineTo(w, (i * h) / 4);
      c.stroke();
    }
    for (const a of sim.asteroids) {
      if (a.ore <= 0) continue;
      const p = point(a);
      c.fillStyle = "#8b938077";
      c.beginPath();
      c.arc(p.x, p.y, Math.max(1, a.radius * s), 0, TAU);
      c.fill();
    }
    for (const b of sim.buildings) {
      const p = point(b);
      c.fillStyle = b.powered ? this.accent : "#9a685c";
      c.fillRect(p.x - 1.5, p.y - 1.5, 3, 3);
    }
    for (const e of sim.enemies) {
      const p = point(e);
      c.fillStyle = "#f28575";
      c.fillRect(p.x - 1, p.y - 1, 2.5, 2.5);
    }
    const incoming = sim.nextWavePreview();
    if (incoming)
      for (const angle of incoming.angles) {
        const r = sim.mission.world * 0.5,
          p = point({ x: Math.cos(angle) * r, y: Math.sin(angle) * r });
        c.save();
        c.translate(p.x, p.y);
        c.rotate(-angle + Math.PI);
        c.fillStyle =
          incoming.seconds <= 15 && !incoming.manual ? "#ff795f" : "#eeb778";
        c.beginPath();
        c.moveTo(6, 0);
        c.lineTo(-4, -4);
        c.lineTo(-4, 4);
        c.closePath();
        c.fill();
        c.restore();
      }
    const pos = point({ x: this.cameraX, y: this.cameraY });
    c.strokeStyle = "#96b7c57a";
    c.strokeRect(
      pos.x - ((this.width / this.zoom) * s) / 2,
      pos.y - ((this.height / this.zoom) * s) / 2,
      (this.width / this.zoom) * s,
      (this.height / this.zoom) * s,
    );
  }
}
