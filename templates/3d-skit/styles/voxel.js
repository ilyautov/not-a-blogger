// SPDX-License-Identifier: MIT
// Style "voxel": blocky characters with pixel-art faces drawn on a canvas texture, a giant glowing keyboard as the floor,
// a blurred terminal wall in the back, soft shadows and depth of field. Faces change per frame (mouth from the envelope,
// blinks, reaction overlays), so expression costs nothing: it is a few pixels, not a new model.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { U, W, H, animateRig, frameShot, run } from '../common/core.js';

const { clamp, hash, V } = U;

// ---------- palette (neutral: replace with your own) ----------
const P = {
  bg: 0x05070f, key: '#141a33', keyGlowA: 0x2f6bff, keyGlowB: 0x2fd6b8,
  skin: '#e2a57c', hair: '#3a2618', hood: '#5a6a92', hoodD: '#4a5878', jeans: '#2a3456', cap: '#2fb7a8', capD: '#1d7f74',
  bot: '#c9d3df', botD: '#8d99a8', screen: '#0d1622', botInk: '#7ff3ff',
};

// pixel "roughness": an 8x8 texture with tiny brightness noise, NearestFilter keeps the voxel look
const texCache = {};
function voxTex(hex, n = 8, amp = .07) {
  const id = hex + n + amp; if (texCache[id]) return texCache[id];
  const c = document.createElement('canvas'); c.width = c.height = n; const g = c.getContext('2d'); const col = new THREE.Color(hex);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const k = 1 + (hash(x + n * 7, y + hex.length * 13 + n) - .5) * 2 * amp;
    g.fillStyle = `rgb(${clamp(col.r * k) * 255},${clamp(col.g * k) * 255},${clamp(col.b * k) * 255})`; g.fillRect(x, y, 1, 1);
  }
  const t = new THREE.CanvasTexture(c); t.magFilter = t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace;
  return (texCache[id] = t);
}
const vox = (hex, o = {}) => new THREE.MeshStandardMaterial({ color: 0xffffff, map: voxTex(hex, o.n || 8, o.amp ?? .07), roughness: o.rough ?? .82 });
const glow = (color, k = 1) => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: color, emissiveIntensity: k, roughness: 1 });
function box(w, h, d, mat, x = 0, y = 0, z = 0, parent, shadow = true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); m.castShadow = shadow; m.receiveShadow = true;
  parent && parent.add(m); return m;
}
const grp = (parent, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.position.set(x, y, z); parent && parent.add(g); return g; };
function canvasTex(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const t = new THREE.CanvasTexture(c); t.magFilter = t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace;
  return { c, g: c.getContext('2d'), t };
}

// ---------- renderer ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.08;
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(P.bg); scene.fog = new THREE.Fog(P.bg, 22, 46);
const camera = new THREE.PerspectiveCamera(30, W / H, .05, 80);

// ---------- light: warm key, blue bounce from the keyboard, cool rim ----------
scene.add(new THREE.HemisphereLight(0x6f7fd0, 0x120c18, .55));
const key = new THREE.DirectionalLight(0xffe2c4, 2.5); key.position.set(-2.5, 6, 6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -2, near: .5, far: 25 });
key.shadow.bias = -.0005; key.shadow.normalBias = .02; key.shadow.radius = 3; scene.add(key);
const rim = new THREE.SpotLight(0x8aa2ff, 70, 16, .8, .6, 2); rim.position.set(0, 4.5, -3.5); rim.target.position.set(0, 1, .2); scene.add(rim, rim.target);
const bounce = new THREE.PointLight(P.keyGlowA, 9, 6, 2); bounce.position.set(-.6, .35, 1.4); scene.add(bounce);
const fill = new THREE.DirectionalLight(0xdfe6ff, .7); fill.position.set(.5, 2.5, 9); scene.add(fill);

// ---------- world: giant keyboard floor ----------
const KEY = 1.0, GAP = .13, KH = .34;
const keyMat = vox(P.key, { amp: .1 }), glowMats = [];
function glyphTex(ch) {
  const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d');
  g.fillStyle = P.key; g.fillRect(0, 0, 64, 64); g.fillStyle = 'rgba(150,170,255,.55)'; g.font = '700 22px Helvetica, Arial, sans-serif'; g.fillText(ch, 10, 30);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const glyphMats = ['Q', 'W', 'E', 'R', 'A', 'S', 'D', 'F', 'Z', 'X', 'Tab', 'Esc'].map(ch => new THREE.MeshStandardMaterial({ map: glyphTex(ch), roughness: .7 }));
for (let r = -6; r <= 5; r++) for (let c = -9; c <= 9; c++) {
  const x = c * (KEY + GAP) + (r % 2 ? .45 : 0), z = r * (KEY + GAP) + .3, h = hash(r + 40, c + 40);
  let top = keyMat;
  if (h < .16) { const m = glow(h < .08 ? P.keyGlowA : P.keyGlowB, 1.3); glowMats.push({ m, base: 1.3, ph: h * 40 }); top = m; }
  else if (h > .55) top = glyphMats[Math.floor(h * 997) % glyphMats.length];
  const k = new THREE.Mesh(new THREE.BoxGeometry(KEY, KH, KEY), [keyMat, keyMat, top, keyMat, keyMat, keyMat]);
  k.position.set(x, -KH / 2, z); k.receiveShadow = true; scene.add(k);
}
box(40, .2, 30, vox('#04050b'), 0, -KH - .1, 0, scene, false);

// blurred terminal wall: a few layers of generic text at different depths; DOF does the rest
const TERM = ['$ npm test', 'Running tests...', '42 passed', 'git status', 'On branch main', 'nothing to commit', 'build ok', 'done in 3.2s', 'Reading 12 files', 'Edit src/app.ts'];
function termTex(seedK, w = 1024, h = 1024) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
  g.fillStyle = '#060a18'; g.fillRect(0, 0, w, h); g.filter = 'blur(1.6px)';
  for (let i = 0; i < 44; i++) {
    const a = .25 + hash(i, seedK + 3) * .4;
    g.fillStyle = hash(i, seedK + 5) > .86 ? `rgba(120,200,160,${a})` : `rgba(170,185,220,${a})`;
    g.font = `500 ${18 + Math.floor(hash(i, seedK + 7) * 6)}px Menlo, monospace`;
    g.fillText(TERM[Math.floor(hash(i, seedK + 9) * TERM.length)], 30 + hash(i, seedK) * (w - 380), 30 + i * (h / 44));
  }
  g.filter = 'none'; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
[[0, 5.5, -7, 22, 13, 1], [-6, 4.2, -5.2, 7, 7, 2], [6.5, 4.4, -5.6, 7, 7, 3]].forEach(([x, y, z, w, h, s]) => {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: termTex(s), color: 0x9aa3c0, fog: false }));
  m.position.set(x, y, z); scene.add(m);
});

// ---------- Dude: voxel guy in a hoodie and cap, pixel face 24x26 ----------
const dFace = canvasTex(24, 26);
function makeDude() {
  const root = grp(scene, -1.05, 0, .25); root.rotation.y = .42;
  const S = vox(P.skin), HR = vox(P.hair), HD = vox(P.hood, { amp: .09 }), HD2 = vox(P.hoodD), J = vox(P.jeans), SH = vox('#e9e7e1'), CAP = vox(P.cap, { amp: .05 });
  [-.15, .15].forEach(x => { const g = grp(root, x, .82, 0); box(.24, .72, .28, J, 0, -.4, 0, g); box(.27, .14, .38, SH, 0, -.76, .05, g); });
  const torso = grp(root, 0, .84, 0);
  box(.82, .82, .44, HD, 0, .41, 0, torso); box(.5, .2, .05, HD2, 0, .2, .225, torso); box(.6, .14, .5, HD2, 0, .8, -.03, torso);
  const neck = grp(torso, 0, .82, 0); box(.2, .12, .2, S, 0, .05, 0, neck);
  const head = grp(neck, 0, .1, 0);
  const fm = new THREE.MeshStandardMaterial({ map: dFace.t, roughness: .8 });
  const hm = new THREE.Mesh(new THREE.BoxGeometry(.6, .64, .56), [S, S, HR, S, fm, HR]); hm.position.y = .32; hm.castShadow = hm.receiveShadow = true; head.add(hm);
  box(.11, .11, .07, vox('#e9b089'), 0, .27, .305, head);
  [-1, 1].forEach(s => { box(.07, .14, .1, S, s * .325, .33, -.02, head); box(.04, .22, .3, HR, s * .305, .5, -.08, head); });
  box(.62, .22, .3, HR, 0, .56, -.15, head);
  const cap = grp(head, 0, .66, 0);
  box(.66, .2, .62, CAP, 0, .07, -.01, cap, false); box(.6, .045, .34, CAP, 0, -.02, .43, cap, false); box(.1, .05, .1, vox(P.capD), 0, .19, 0, cap, false);
  const arms = [-1, 1].map(s => {
    const sh = grp(torso, s * .53, .72, 0); box(.22, .42, .24, HD, 0, -.2, 0, sh, false);
    const el = grp(sh, 0, -.4, 0); box(.2, .38, .22, HD, 0, -.18, 0, el, false); box(.18, .18, .18, S, 0, -.4, 0, el, false);
    return { sh, el, s };
  });
  return { root, torso, neck, head, arms };
}
const px = (g, x, y, w, h, c) => { g.fillStyle = c; g.fillRect(x, y, w, h); };
function drawDudeFace(st) {
  const g = dFace.g; px(g, 0, 0, 24, 26, P.skin);
  px(g, 0, 0, 24, 2, P.hair); px(g, 0, 2, 3, 3, P.hair); px(g, 21, 2, 3, 3, P.hair);
  const browUp = st.shock > .5 || st.happy > .5 ? 2 : 0, tilt = st.slump > .5 || st.facepalm > .5 ? -2 : st.smug > .5 ? 1 : 0;
  for (const [x0, s] of [[3, -1], [14, 1]]) for (let i = 1; i < 6; i++) {
    const inner = s < 0 ? 6 - i : i; px(g, x0 + i, 6 - browUp + Math.round(tilt * (2 - inner) / 4), 1, 2, P.hair);
  }
  const OF = '#151821';                                          // glasses
  for (const x0 of [3, 14]) { px(g, x0, 8, 7, 1, OF); px(g, x0, 14, 7, 1, OF); px(g, x0, 8, 1, 7, OF); px(g, x0 + 6, 8, 1, 7, OF); px(g, x0 + 1, 9, 5, 5, '#f2ece6'); }
  px(g, 10, 10, 4, 1, OF);
  const eh = st.blink ? 1 : st.smug > .5 ? 2 : st.shock > .5 ? 4 : 3, ey = 11 - Math.floor(eh / 2) + (st.blink ? 1 : 0);
  for (const x0 of [5, 16]) {
    if (st.blink) { px(g, x0 - 1, 12, 5, 1, '#3b2a22'); continue; }
    px(g, x0, ey, 3, eh, '#2b5fa8'); px(g, x0 + 1, ey + Math.floor(eh / 2), 1, 1, '#0b0d14'); px(g, x0, ey, 1, 1, '#ffffff');
  }
  const m = st.mouth > .45 ? 2 : st.mouth > .12 ? 1 : 0, mx = 9, my = 20;
  if (!m && st.happy > .5) { px(g, mx, my, 6, 1, '#7b2b2b'); px(g, mx - 1, my - 1, 1, 1, '#7b2b2b'); px(g, mx + 6, my - 1, 1, 1, '#7b2b2b'); }
  else if (!m && (st.slump > .5 || st.facepalm > .5)) { px(g, mx, my, 6, 1, '#7b2b2b'); px(g, mx - 1, my + 1, 1, 1, '#7b2b2b'); px(g, mx + 6, my + 1, 1, 1, '#7b2b2b'); }
  else if (!m) px(g, mx, my, 6, 1, '#8a3a34');
  else { const h = m === 1 ? 2 : 3 + (st.shock > .5 ? 1 : 0); px(g, mx - (m > 1 ? 1 : 0), my - 1, 6 + (m > 1 ? 2 : 0), h, '#4a1416'); px(g, mx, my - 1, 6, 1, '#f1e9e2'); }
  dFace.t.needsUpdate = true;
}

// ---------- Bot: pale boxy robot, dark screen face with cyan pixels ----------
const bFace = canvasTex(32, 20);
function makeBot() {
  const root = grp(scene, 1.05, 0, .25); root.rotation.y = -.42;
  const B = vox(P.bot, { n: 16, amp: .06, rough: .55 }), B2 = vox(P.botD);
  [[-.3, 0], [.3, 0]].forEach(([x]) => { const g = grp(root, x, .5, 0); box(.2, .5, .22, B2, 0, -.25, 0, g); });
  const torso = grp(root, 0, .5, 0); box(.9, .8, .6, B, 0, .4, 0, torso); box(.5, .3, .04, glow(P.botInk, .25), 0, .45, .31, torso, false);
  const neck = grp(torso, 0, .8, 0); box(.16, .12, .16, B2, 0, .06, 0, neck);
  const head = grp(neck, 0, .12, 0);
  const fm = new THREE.MeshStandardMaterial({ map: bFace.t, roughness: .5, emissive: 0xffffff, emissiveMap: bFace.t, emissiveIntensity: .6 });
  const hm = new THREE.Mesh(new THREE.BoxGeometry(1.0, .64, .6), [B, B, B, B, fm, B]); hm.position.y = .32; hm.castShadow = hm.receiveShadow = true; head.add(hm);
  const ant = grp(head, .3, .64, 0); box(.04, .22, .04, B2, 0, .11, 0, ant); box(.09, .09, .09, glow(P.botInk, 1.2), 0, .25, 0, ant, false);
  const arms = [-1, 1].map(s => {
    const sh = grp(torso, s * .55, .7, 0); box(.16, .38, .16, B2, 0, -.18, 0, sh, false);
    const el = grp(sh, 0, -.36, 0); box(.15, .34, .15, B, 0, -.16, 0, el, false); box(.2, .14, .2, B2, 0, -.36, 0, el, false);
    return { sh, el, s };
  });
  return { root, torso, neck, head, arms };
}
function drawBotFace(st) {
  const g = bFace.g, C = P.botInk; px(g, 0, 0, 32, 20, P.screen);
  for (let y = 0; y < 20; y += 2) px(g, 0, y, 32, 1, 'rgba(255,255,255,.03)');   // scanlines
  const lx = 8, rx = 20, ey = 6;
  if (st.happy > .5) for (const x of [lx, rx]) { px(g, x, ey + 2, 1, 1, C); px(g, x + 1, ey + 1, 2, 1, C); px(g, x + 3, ey + 2, 1, 1, C); }  // ^^
  else if (st.smug > .5) { px(g, lx, ey + 2, 4, 1, C); px(g, rx, ey + 1, 4, 2, C); px(g, rx - 1, ey - 1, 5, 1, C); }
  else if (st.blink) { px(g, lx, ey + 2, 4, 1, C); px(g, rx, ey + 2, 4, 1, C); }
  else { const h = st.shock > .5 ? 5 : 4; px(g, lx, ey, 4, h, C); px(g, rx, ey, 4, h, C); }
  if (st.sweatK >= 0) { const y = 1 + Math.floor(st.sweatK * 5); px(g, 28, y, 1, 1, '#d9f1ff'); px(g, 27, y + 1, 3, 3, '#9fd6ff'); }
  const m = st.mouth > .45 ? 2 : st.mouth > .12 ? 1 : 0, mx = 14, my = 13;
  if (m === 0) { if (st.happy > .5 || st.smug > .5) { px(g, mx, my + 1, 4, 1, C); px(g, mx - 1, my, 1, 1, C); px(g, mx + 4, my, 1, 1, C); } else px(g, mx, my + 1, 4, 1, C); }
  else if (m === 1) px(g, mx + 1, my, 2, 2, C); else px(g, mx, my - 1, 4, 3, C);
  bFace.t.needsUpdate = true;
}

const dude = makeDude(), bot = makeBot();
dude.face = drawDudeFace; bot.face = drawBotFace;
const facing = r => V(Math.sin(r.root.rotation.y), 0, Math.cos(r.root.rotation.y));
const rigs = {
  dude: { head: () => dude.head.localToWorld(V(0, .3, .2)), facing: facing(dude), size: .65 },
  bot: { head: () => bot.head.localToWorld(V(0, .3, .25)), facing: facing(bot), size: .65 },
};

const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { samples: 4, type: THREE.HalfFloatType }));
composer.addPass(new RenderPass(scene, camera));
const bokeh = new BokehPass(scene, camera, { focus: 5, aperture: .002, maxblur: .012 }); composer.addPass(bokeh);
composer.addPass(new OutputPass());

await run(t => {
  animateRig(dude, 'dude', t, .4); animateRig(bot, 'bot', t, 1.3);
  bot.torso.position.y = .5 + Math.sin(t * 2 * Math.PI / 1.9) * .01;
  glowMats.forEach(({ m, base, ph }) => m.emissiveIntensity = base * (.8 + .2 * Math.sin(t * .9 + ph)));
  scene.updateMatrixWorld(true);
  const f = frameShot(camera, rigs, t, { fov: 30, medium: 7.5, tight: 5.4, wide: 24 });
  bokeh.uniforms.focus.value = camera.position.distanceTo(f.focus);
  bokeh.uniforms.aperture.value = f.shot.name === 'wide' ? .0012 : .0042;
  composer.render();
});
