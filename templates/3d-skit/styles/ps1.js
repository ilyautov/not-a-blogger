// SPDX-License-Identifier: MIT
// Style "ps1": retro console look. The scene renders at 360x640 without antialiasing and is upscaled x3 with nearest.
// Vertices snap to the low-res pixel grid (the famous wobble), textures map affinely (no perspective correction),
// then a post pass applies 4x4 Bayer dithering and 15-bit color. Characters animate at 12 fps, the camera at 15 fps.
import * as THREE from 'three';
import { TL, U, W, H, animateRig, frameShot, run } from '../common/core.js';

const { clamp, V } = U;
const LW = 360, LH = 640;
const rnd = U.rng(4242);

// ---------- PS1 materials: vertex snap + affine UVs ----------
const SNAP = { value: new THREE.Vector2(LW / 2, LH / 2) };
function ps1ify(m) {
  m.onBeforeCompile = sh => {
    sh.uniforms.uSnap = SNAP;
    sh.vertexShader = 'uniform vec2 uSnap;\nvarying vec3 vAff;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      { vec4 p = gl_Position; p.xy = floor(p.xy / p.w * uSnap + .5) / uSnap * p.w; gl_Position = p; }
      #ifdef USE_MAP
      vAff = vec3(vMapUv * gl_Position.w, gl_Position.w);
      #else
      vAff = vec3(0., 0., 1.);
      #endif`);
    sh.fragmentShader = 'varying vec3 vAff;\n' + sh.fragmentShader.replace('#include <map_fragment>', `#ifdef USE_MAP
      diffuseColor *= texture2D(map, vAff.xy / vAff.z);
      #endif`);
  };
  return m;
}
function tex(draw, size = 32, rep = [1, 1]) {
  const c = document.createElement('canvas'); c.width = c.height = size; draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); return t;
}
const hex = n => '#' + n.toString(16).padStart(6, '0');
function shade(n, k) { const f = c => Math.round(clamp(k > 0 ? c + (255 - c) * k : c * (1 + k), 0, 255)); return `rgb(${f(n >> 16)},${f((n >> 8) & 255)},${f(n & 255)})`; }
// 32x32 noise textures: base color + per-pixel brightness spread; 'kind' adds a pattern
function noiseTex(base, kind = 'noise', amp = .12, size = 32, rep = [1, 1]) {
  return tex((g, s) => {
    g.fillStyle = hex(base); g.fillRect(0, 0, s, s);
    for (let y = 0; y < s; y++) for (let x = 0; x < s; x++) {
      let k = (rnd() - .5) * amp * 2;
      if (kind === 'fabric') k += (x % 2 ? .04 : -.04) + (y % 4 === 0 ? -.05 : 0);
      if (kind === 'wood') k += Math.sin(y * .9 + Math.sin(x * .2) * 2) * .07;
      if (kind === 'fur') k += Math.sin(x * 1.7 + rnd()) * .1 + (rnd() < .12 ? .25 : 0);
      if (kind === 'panel') k += (x % 16 === 0 || y % 16 === 0) ? -.25 : 0;
      if (kind === 'carpet') k += ((x >> 2) + (y >> 2)) % 2 ? .05 : -.05;
      g.fillStyle = shade(base, k); g.fillRect(x, y, 1, 1);
    }
  }, size, rep);
}
const lam = (color, map = null, o = {}) => ps1ify(new THREE.MeshLambertMaterial({ color, map, flatShading: true, ...o }));
const basic = (color, map = null, o = {}) => ps1ify(new THREE.MeshBasicMaterial({ color, map, ...o }));
const T = {
  skin: noiseTex(0xe2ab86, 'noise', .06), hood: noiseTex(0x3a4858, 'fabric', .1), hair: noiseTex(0x2b1d15, 'fur', .1),
  bot: noiseTex(0x9aa7b4, 'panel', .08), wood: noiseTex(0x6b4a33, 'wood', .08, 32, [3, 1]),
  carpet: noiseTex(0x2d3442, 'carpet', .1, 32, [12, 12]), wall: noiseTex(0x5b6170, 'panel', .06, 32, [6, 3]),
};
function mesh(geo, mat, x = 0, y = 0, z = 0, parent) { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); parent && parent.add(m); return m; }
const grp = (parent, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.position.set(x, y, z); parent && parent.add(g); return g; };

// ---------- renderer: scene to a low-res target, post pass to the screen ----------
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.toneMapping = THREE.NoToneMapping;
document.body.prepend(renderer.domElement);
const rt = new THREE.WebGLRenderTarget(LW, LH, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true });
const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { tDiffuse: { value: rt.texture }, uRes: { value: new THREE.Vector2(LW, LH) } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec2 uRes; varying vec2 vUv;
    const float B[16] = float[16](0.,8.,2.,10.,12.,4.,14.,6.,3.,11.,1.,9.,15.,7.,13.,5.);
    vec3 toSRGB(vec3 c){ c = clamp(c, 0., 1.); return mix(c * 12.92, 1.055 * pow(c, vec3(1. / 2.4)) - .055, step(.0031308, c)); }
    void main(){
      vec2 px = floor(vUv * uRes);
      vec3 c = toSRGB(texture2D(tDiffuse, (px + .5) / uRes).rgb);
      float l = dot(c, vec3(.299, .587, .114)); c = mix(vec3(l), c, 1.12);   // a bit juicier, like a CRT
      int i = int(mod(px.x, 4.)) + int(mod(px.y, 4.)) * 4;
      c += (B[i] / 16. - .5) / 31.;                                             // ordered dithering
      c = floor(clamp(c, 0., 1.) * 31. + .5) / 31.;                            // 5 bits per channel
      gl_FragColor = vec4(c, 1.);
    }`, depthTest: false, depthWrite: false }));
const postScene = new THREE.Scene(); postScene.add(post); const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const scene = new THREE.Scene();
const FOG = 0x0b1220; scene.background = new THREE.Color(FOG); scene.fog = new THREE.Fog(FOG, 5, 15);
const camera = new THREE.PerspectiveCamera(34, W / H, .1, 40);

// ---------- light: no shadows (period-correct); the key light follows the camera and lights the speaker ----------
scene.add(new THREE.HemisphereLight(0x5d6fa8, 0x2a1c16, 1.1));
const key = new THREE.DirectionalLight(0xffc890, 2.4); scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0x7fa6ff, 1.8); scene.add(rim, rim.target);
const lampL = new THREE.PointLight(0xffa860, 6, 5, 1.6); lampL.position.set(-1.9, 1.7, .6); scene.add(lampL);
const monL = new THREE.PointLight(0x5a8cff, 4, 4, 1.6); monL.position.set(0, 1.4, -.6); scene.add(monL);

// ---------- night office ----------
mesh(new THREE.PlaneGeometry(14, 14), lam(0xffffff, T.carpet), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
const wallM = lam(0xffffff, T.wall);
mesh(new THREE.PlaneGeometry(14, 5), wallM, 0, 2.5, -5, scene);
mesh(new THREE.PlaneGeometry(14, 5), wallM, 5, 2.5, 0, scene).rotation.y = -Math.PI / 2;
const city = tex((g, s) => { g.fillStyle = '#0a1430'; g.fillRect(0, 0, s, s);
  for (let b = 0; b < 9; b++) { const x = b * 7 + (rnd() * 3 | 0), w = 5 + (rnd() * 3 | 0), top = 14 + (rnd() * 30 | 0); g.fillStyle = '#121a33'; g.fillRect(x, top, w, s - top);
    for (let y = top + 2; y < s - 2; y += 3) for (let k = x + 1; k < x + w - 1; k += 2) if (rnd() < .45) { g.fillStyle = rnd() < .75 ? '#ffcf73' : '#8fd0ff'; g.fillRect(k, y, 1, 1); } } }, 64, [2, 1]);
mesh(new THREE.PlaneGeometry(14, 5), basic(0xffffff, city), -5, 2.5, 0, scene).rotation.y = Math.PI / 2;
for (let z = -4.5; z <= 4.5; z += 2.2) mesh(new THREE.BoxGeometry(.12, 5, .14), lam(0x1a1d24), -4.94, 2.5, z, scene);
const rack = grp(scene, -1.6, 0, -4.7);
mesh(new THREE.BoxGeometry(1.2, 2.6, .6), lam(0x15171c, noiseTex(0x15171c, 'panel', .1)), 0, 1.3, 0, rack);
const leds = [];
for (let r = 0; r < 14; r++) for (let c = 0; c < 6; c++) leds.push(mesh(new THREE.BoxGeometry(.05, .05, .02), basic(0x30ff70), -.4 + c * .16, .35 + r * .16, .31, rack));
mesh(new THREE.BoxGeometry(2.2, 1.2, .05), lam(0xd9dde4, noiseTex(0xd9dde4, 'noise', .05)), 1.6, 1.8, -4.95, scene);
[[1.0, 2.1, 0xd04a3a], [1.5, 1.9, 0x3a7bd0], [2.1, 2.0, 0x33a060], [1.3, 1.5, 0xd0a03a]].forEach(([x, y, c]) => mesh(new THREE.BoxGeometry(.3, .03, .02), basic(c), x, y, -4.9, scene));
mesh(new THREE.BoxGeometry(4.2, .08, 1.6), lam(0xffffff, T.wood), 0, .75, 0, scene);
[[-1.9, -.65], [1.9, -.65], [-1.9, .65], [1.9, .65]].forEach(([x, z]) => mesh(new THREE.BoxGeometry(.08, .75, .08), lam(0x22252c), x, .37, z, scene));
// monitor with a tiny canvas screen: swap drawScreen() for your story prop
const scrC = document.createElement('canvas'); scrC.width = 64; scrC.height = 40; const sx = scrC.getContext('2d');
const scrT = new THREE.CanvasTexture(scrC); scrT.colorSpace = THREE.SRGBColorSpace; scrT.magFilter = scrT.minFilter = THREE.NearestFilter; scrT.generateMipmaps = false;
mesh(new THREE.BoxGeometry(1.3, .82, .08), lam(0x111318), -.15, 1.32, -.55, scene);
mesh(new THREE.PlaneGeometry(1.2, .72), basic(0xffffff, scrT), -.15, 1.32, -.505, scene);
mesh(new THREE.BoxGeometry(.12, .4, .08), lam(0x111318), -.15, .95, -.6, scene);
function drawScreen(t, alarm) {
  sx.fillStyle = '#0d1424'; sx.fillRect(0, 0, 64, 40); sx.fillStyle = '#26324f'; sx.fillRect(0, 0, 64, 5);
  for (let r = 0; r < 7; r++) for (let c = 0; c < 4; c++) { sx.fillStyle = c ? '#7f9cd6' : '#9fe0c8'; sx.fillRect(3 + c * 15, 8 + r * 4, 6 + ((r * 7 + c * 3) % 6), 2); }
  if (alarm && Math.floor(t * 3) % 2) { sx.fillStyle = '#e8402e'; sx.fillRect(10, 15, 44, 10); sx.fillStyle = '#ffd9d0'; sx.fillRect(14, 19, 36, 2); }
  scrT.needsUpdate = true;
}
mesh(new THREE.BoxGeometry(.9, .04, .3), lam(0x1d2028, noiseTex(0x2a2e38, 'panel', .2, 16, [4, 1])), -.9, .81, .35, scene);
const mug = grp(scene, -1.35, .79, .55); mesh(new THREE.CylinderGeometry(.08, .07, .17, 6), lam(0xe8e2d6), 0, .085, 0, mug);

// ---------- Dude: generic guy in a hoodie (not a real person), bust behind the desk ----------
const SKIN = lam(0xffffff, T.skin), HOOD = lam(0xffffff, T.hood), HAIR = lam(0xffffff, T.hair);
function makeDude() {
  const root = grp(scene, -1.15, 0, .15); root.rotation.y = .62;
  const torso = grp(root, 0, .55, 0);
  mesh(new THREE.CylinderGeometry(.34, .4, .72, 7), HOOD, 0, .36, 0, torso);
  mesh(new THREE.TorusGeometry(.22, .09, 4, 7), HOOD, 0, .72, -.06, torso).rotation.x = 1.3;
  const neck = grp(torso, 0, .74, 0); mesh(new THREE.CylinderGeometry(.11, .12, .12, 5), SKIN, 0, .05, 0, neck);
  const head = grp(neck, 0, .1, 0);
  mesh(new THREE.IcosahedronGeometry(.36, 1), SKIN, 0, .33, 0, head).scale.set(1.0, 1.12, .98);
  mesh(new THREE.IcosahedronGeometry(.2, 1), SKIN, 0, .16, .1, head).scale.set(1.25, .8, .95);
  const cap = mesh(new THREE.SphereGeometry(.4, 7, 5, 0, Math.PI * 2, 0, 1.25), HAIR, 0, .37, -.03, head); cap.scale.set(1.04, 1.06, 1.05); cap.rotation.x = -.3;
  const WEDGE = new THREE.TetrahedronGeometry(.16, 0);
  for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2; const w = mesh(WEDGE, HAIR, Math.cos(a) * .27, .62 + Math.sin(i * 2.3) * .05, Math.sin(a) * .18 - .02, head);
    w.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3); w.scale.set(1, 1.3, .8); }
  [-1, 1].forEach(s => mesh(new THREE.IcosahedronGeometry(.07, 0), SKIN, s * .37, .33, -.02, head).scale.set(.5, 1, .8));
  mesh(new THREE.IcosahedronGeometry(.055, 0), lam(0xf2d6c8, T.skin), 0, .27, .35, head).scale.set(.8, 1.0, .7);
  const eyes = [], brows = [];
  for (const s of [-1, 1]) {
    const eg = grp(head, s * .13, .37, .31);
    mesh(new THREE.SphereGeometry(.05, 6, 4), lam(0xf2eee6), 0, 0, 0, eg).scale.set(1, .8, .6);
    mesh(new THREE.SphereGeometry(.028, 5, 4), basic(0x24150c), 0, 0, .03, eg);
    eyes.push(eg);
    const b = grp(head, s * .14, .46, .33); mesh(new THREE.BoxGeometry(.15, .035, .04), HAIR, 0, 0, 0, b); brows.push(b);
  }
  const mIn = mesh(new THREE.BoxGeometry(.1, .025, .02), basic(0x2a0f10), 0, .17, .3, head);
  const lo = mesh(new THREE.BoxGeometry(.1, .022, .03), lam(0xc98a7a), 0, .145, .3, head);
  const arms = [-1, 1].map(s => { const sh = grp(torso, s * .38, .62, 0); mesh(new THREE.CylinderGeometry(.1, .09, .4, 5), HOOD, 0, -.18, 0, sh);
    const el = grp(sh, 0, -.38, 0); mesh(new THREE.CylinderGeometry(.09, .08, .36, 5), HOOD, 0, -.16, 0, el);
    mesh(new THREE.IcosahedronGeometry(.06, 0), SKIN, 0, -.36, 0, el); return { sh, el, s }; });
  const face = st => {
    eyes.forEach(eg => eg.scale.set(1 + st.shock * .25, Math.max(.12, st.blink ? .1 : 1) * (1 + st.shock * .3), 1));
    brows.forEach((b, i) => { const s = i ? 1 : -1; b.position.y = .46 + st.shock * .06 + st.mouth * .015; b.rotation.z = s * (.22 * (1 - st.shock) + st.slump * .15); });
    const open = clamp(st.mouth * 1.1 + st.shock * .3);
    mIn.scale.set(1, 1 + open * 3.2, 1); mIn.position.y = .17 - open * .035; lo.position.y = .145 - open * .075;
  };
  return { root, torso, neck, head, arms, face };
}

// ---------- Bot: grey capsule robot with round cyan eyes (no visor, no orange) ----------
function makeBot() {
  const root = grp(scene, 1.0, .79, .15); root.rotation.y = -.62;
  const BOT = lam(0xffffff, T.bot), DARK = lam(0x2a2f38), EYE = basic(0x8ff0ff);
  const torso = grp(root, 0, .05, 0);
  mesh(new THREE.CylinderGeometry(.32, .36, .55, 8), BOT, 0, .28, 0, torso);
  mesh(new THREE.BoxGeometry(.26, .16, .04), basic(0x3a6f7a), 0, .32, .33, torso);
  const neck = grp(torso, 0, .58, 0); mesh(new THREE.CylinderGeometry(.08, .08, .1, 6), DARK, 0, .04, 0, neck);
  const head = grp(neck, 0, .1, 0);
  mesh(new THREE.CapsuleGeometry(.3, .18, 3, 8), BOT, 0, .3, 0, head).rotation.z = Math.PI / 2;
  mesh(new THREE.BoxGeometry(.56, .3, .05), DARK, 0, .3, .27, head);
  const eyes = [-1, 1].map(s => mesh(new THREE.CylinderGeometry(.06, .06, .02, 8), EYE, s * .13, .33, .3, head));
  eyes.forEach(e => e.rotation.x = Math.PI / 2);
  const mouth = mesh(new THREE.BoxGeometry(.12, .02, .02), EYE, 0, .22, .3, head);
  const ant = grp(head, -.12, .55, 0); mesh(new THREE.CylinderGeometry(.012, .016, .18, 4), DARK, 0, .09, 0, ant);
  const bulb = mesh(new THREE.SphereGeometry(.035, 5, 4), basic(0x8ff0ff), 0, .2, 0, ant);
  const arms = [-1, 1].map(s => { const sh = grp(torso, s * .38, .45, 0); mesh(new THREE.CylinderGeometry(.06, .05, .3, 5), DARK, 0, -.14, 0, sh);
    const el = grp(sh, 0, -.28, 0); mesh(new THREE.CylinderGeometry(.05, .045, .26, 5), BOT, 0, -.12, 0, el); mesh(new THREE.BoxGeometry(.09, .07, .09), DARK, 0, -.27, 0, el);
    return { sh, el, s }; });
  const face = st => {
    eyes.forEach((e, i) => { e.scale.set(1 + st.shock * .3, 1, (st.blink ? .15 : 1) * (1 - st.smug * .6) * (1 + st.happy * .2)); e.rotation.y = (i ? 1 : -1) * st.smug * .3; });
    mouth.scale.set(1 + st.mouth * .8 + st.happy * .6, 1 + st.mouth * 2.2, 1);
    bulb.material.color.setHex(st.mouth > .3 ? 0xe8ffff : 0x5fc8d8);
  };
  return { root, torso, neck, head, arms, face };
}

const dude = makeDude(), bot = makeBot();
const facing = r => V(Math.sin(r.root.rotation.y), 0, Math.cos(r.root.rotation.y));
const rigs = {
  dude: { head: () => dude.head.localToWorld(V(0, .33, .05)), facing: facing(dude), size: .7 },
  bot: { head: () => bot.head.localToWorld(V(0, .3, .05)), facing: facing(bot), size: .7 },
};

await run(t => {
  const ta = Math.floor(t * 12 + 1e-6) / 12, tc = Math.floor(t * 15 + 1e-6) / 15;   // 12 fps characters, 15 fps camera
  animateRig(dude, 'dude', ta, .3); animateRig(bot, 'bot', ta, 1.1);
  drawScreen(ta, ta >= (TL.lines[2]?.start ?? Infinity));   // the prop reacts to the story: alarm from line 3
  leds.forEach((m, i) => m.visible = ((i * 7 + Math.floor(ta * 6) * 3) % 5) !== 0);
  scene.updateMatrixWorld(true);
  const f = frameShot(camera, rigs, tc, { fov: 34, medium: 5.4, tight: 4.2, wide: 14 });
  key.position.copy(camera.position).add(V(-.8, 1.4, 0)); key.target.position.copy(f.focus);
  rim.position.copy(f.focus).add(V(0, 2, -3)); rim.target.position.copy(f.focus);
  renderer.setRenderTarget(rt); renderer.render(scene, camera);
  renderer.setRenderTarget(null); renderer.render(postScene, postCam);
});
