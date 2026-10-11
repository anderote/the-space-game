import * as THREE from "three";
import { rng } from "./engine.js";
// Original procedural materials. No downloaded game artwork or remote assets.
export function createNebula() {
  const material = new THREE.ShaderMaterial({
    depthWrite: false,
    uniforms: { uTime: { value: 0 } },
    vertexShader: `varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader: `
 precision highp float;
 varying vec2 vUv;uniform float uTime;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+1.),f.x),f.y);}
 float fbm(vec2 p){float f=0.,a=.5;for(int i=0;i<6;i++){f+=a*noise(p);p=mat2(.8,-.6,.6,.8)*p*2.02+13.7;a*=.5;}return f;}
 void main(){
  vec2 p=vUv*24.;vec2 q=vec2(fbm(p+1.7),fbm(p+8.3));float cloud=fbm(p+q*3.3);float ridge=pow(cloud,3.1);float dust=fbm(p*2.4+q*4.);
  vec3 cold=vec3(.035,.12,.14),warm=vec3(.11,.038,.065);vec3 col=vec3(.0017,.0035,.006)+mix(cold,warm,smoothstep(.2,.8,fbm(p*.6)))*ridge*2.8;
  col*=.55+.55*smoothstep(.18,.7,dust);col+=vec3(.008,.014,.021)*pow(fbm(p*1.6+q),7.)*2.;
  vec2 grid=vUv*2300.,cell=floor(grid),local=fract(grid)-.5;float n=hash(cell);float size=.001+.006*pow(n,20.);float star=exp(-dot(local,local)/size)*step(.992,n);float twinkle=.85+.15*sin(uTime*.45+n*53.);col+=star*mix(vec3(.34,.42,.53),vec3(.65,.53,.36),hash(cell+9.))*twinkle;
  gl_FragColor=vec4(col,1.);
 }`,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(7500, 7500), material);
  mesh.position.z = -650;
  return mesh;
}
export function rockMaps() {
  const size = 256,
    random = rng(12574),
    height = new Float32Array(size * size);
  const craters = Array.from({ length: 42 }, () => ({
    x: random() * size,
    y: random() * size,
    r: 3 + random() * 19,
    depth: 0.2 + random() * 0.4,
  }));
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      let h =
        0.5 +
        (random() - 0.5) * 0.1 +
        0.1 * Math.sin(x * 0.071 + y * 0.039) * Math.cos(y * 0.056 - x * 0.017);
      for (const c of craters) {
        const d = Math.hypot(x - c.x, y - c.y) / c.r;
        if (d < 1.2)
          h +=
            d < 0.85
              ? -c.depth * (1 - d * d)
              : c.depth * 0.3 * Math.sin(((d - 0.85) / 0.35) * Math.PI);
      }
      height[y * size + x] = h;
    }
  const normal = new Uint8Array(size * size * 4),
    rough = new Uint8Array(size * size * 4);
  const at = (x, y) => height[((y + size) % size) * size + ((x + size) % size)];
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const i = (y * size + x) * 4,
        dx = (at(x - 1, y) - at(x + 1, y)) * 2.2,
        dy = (at(x, y - 1) - at(x, y + 1)) * 2.2;
      const n = new THREE.Vector3(dx, dy, 1).normalize();
      normal[i] = (n.x * 0.5 + 0.5) * 255;
      normal[i + 1] = (n.y * 0.5 + 0.5) * 255;
      normal[i + 2] = (n.z * 0.5 + 0.5) * 255;
      normal[i + 3] = 255;
      rough[i] = rough[i + 1] = rough[i + 2] = 195 + height[y * size + x] * 55;
      rough[i + 3] = 255;
    }
  const nt = new THREE.DataTexture(normal, size, size),
    rt = new THREE.DataTexture(rough, size, size);
  nt.needsUpdate = rt.needsUpdate = true;
  nt.magFilter = rt.magFilter = THREE.LinearFilter;
  nt.minFilter = rt.minFilter = THREE.LinearMipmapLinearFilter;
  nt.generateMipmaps = rt.generateMipmaps = true;
  nt.wrapS = nt.wrapT = rt.wrapS = rt.wrapT = THREE.RepeatWrapping;
  return {
    normalMap: nt,
    normalScale: new THREE.Vector2(0.75, 0.75),
    roughnessMap: rt,
  };
}
export function hullTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const x = c.getContext("2d"),
    random = rng(216);
  x.fillStyle = "#8a9ba2";
  x.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 22; i++) {
    const px = Math.floor(random() * 8) * 32,
      py = Math.floor(random() * 8) * 32,
      w = 32 + Math.floor(random() * 3) * 32,
      h = 32 + Math.floor(random() * 2) * 32;
    x.fillStyle = `rgba(28,49,60,${0.12 + random() * 0.17})`;
    x.fillRect(px + 2, py + 2, w - 4, h - 4);
    x.strokeStyle = "#405464";
    x.lineWidth = 1;
    x.strokeRect(px + 1, py + 1, w - 2, h - 2);
    x.fillStyle = "#c1ccd0";
    x.fillRect(px + 5, py + 5, 2, 2);
  }
  for (let i = 0; i < 1500; i++) {
    x.fillStyle = `rgba(220,231,229,${random() * 0.08})`;
    x.fillRect(random() * 256, random() * 256, 1 + random() * 8, 1);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
