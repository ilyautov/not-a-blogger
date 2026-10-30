// SPDX-License-Identifier: MIT
// Style "clean": modern toy look in plain three.js. Smooth primitives with physical materials (clearcoat on the bot,
// soft sheen on the hoodie), image-based light from RoomEnvironment (no HDRI file needed), soft shadows, gentle DOF.
// This is the cheap daily driver: ~0.03-0.06 s per frame on a laptop GPU, every edit visible after one re-render.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { TL, U, W, H, animateRig, frameShot, run } from '../common/core.js';

const { clamp, V } = U;
// ---------- palette (neutral pastel: replace with your own) ----------
const P = { wall: 0xe9e4dc, floor: 0xcfc6b8, table: 0x9b7653, hood: 0x4f7cac, skin: 0xf0c3a0, hair: 0x3b2a20, pants: 0x2e3440,
  bot: 0xf4f6f8, botTrim: 0x8a96a3, screen: 0x0f1a24, ink: 0x6ff7e8, accent: 0xff8f6b };

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1); renderer.setSize(W, H);
renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(P.wall);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture; scene.environmentIntensity = .55;
const camera = new THREE.PerspectiveCamera(32, W / H, .05, 60);

// ---------- light: key / fill / rim, the classic three-point setup ----------
const key = new THREE.DirectionalLight(0xfff1e0, 2.2); key.position.set(-3, 5, 4); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -1, near: .5, far: 20 });
key.shadow.radius = 6; key.shadow.bias = -.0004; key.shadow.normalBias = .02; scene.add(key);
const fillL = new THREE.DirectionalLight(0xdfe8ff, .6); fillL.position.set(4, 2, 5); scene.add(fillL);
const rim = new THREE.SpotLight(0xffffff, 40, 12, .7, .6, 2); rim.position.set(0, 4, -3); rim.target.position.set(0, 1.2, 0); scene.add(rim, rim.target);

const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .7, ...o });
const phys = (color, o = {}) => new THREE.MeshPhysicalMaterial({ color, roughness: .35, clearcoat: .6, clearcoatRoughness: .2, ...o });
function mesh(geo, mat, x = 0, y = 0, z = 0, parent, shadow = true) {
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.castShadow = shadow; m.receiveShadow = true; parent && parent.add(m); return m;
}
const grp = (parent, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.position.set(x, y, z); parent && parent.add(g); return g; };

// ---------- set: room corner, table, a window glow, a plant ----------
mesh(new THREE.PlaneGeometry(20, 20), std(P.floor, { roughness: .9 }), 0, 0, 0, scene).rotation.x = -Math.PI / 2;
mesh(new THREE.PlaneGeometry(20, 8), std(P.wall, { roughness: .95 }), 0, 4, -3, scene);
const win = mesh(new THREE.PlaneGeometry(2.2, 1.6), new THREE.MeshBasicMaterial({ color: 0xfff6e0 }), -2.6, 2.4, -2.98, scene, false);
mesh(new THREE.BoxGeometry(2.4, .08, 1.8), std(0xffffff), -2.6, 1.56, -2.94, scene); win.material.toneMapped = false;
const table = grp(scene, 0, 0, .1);
mesh(new THREE.CylinderGeometry(1.1, 1.1, .08, 48), std(P.table, { roughness: .5 }), 0, .78, 0, table);
mesh(new THREE.CylinderGeometry(.08, .12, .78, 16), std(0x3a3f47), 0, .39, 0, table);
const mugs = [[-.45, .2], [.5, .25]].map(([x, z]) => { const m = grp(table, x, .82, z);
  mesh(new THREE.CylinderGeometry(.08, .07, .16, 24), phys(P.accent), 0, .08, 0, m);
  mesh(new THREE.TorusGeometry(.045, .012, 8, 16), phys(P.accent), .09, .08, 0, m); return m; });
const plant = grp(scene, 3.4, 0, -2.6);
mesh(new THREE.CylinderGeometry(.25, .2, .45, 24), phys(0xd9cbb8), 0, .22, 0, plant);
for (let i = 0; i < 7; i++) { const l = mesh(new THREE.SphereGeometry(.22, 16, 12), std(0x5d8f5a), 0, 0, 0, plant);
  l.position.set(Math.cos(i * .9) * .18, .6 + i * .09, Math.sin(i * .9) * .18); l.scale.set(.6, 1.4, .3); l.rotation.set(i * .3, i, .3); }

// ---------- Dude ----------
function makeDude() {
  const root = grp(scene, -.95, 0, .55); root.rotation.y = .5;
  const HOOD = phys(P.hood, { clearcoat: 0, roughness: .8, sheen: .6, sheenColor: new THREE.Color(0x9fc0ff) }), SKIN = std(P.skin, { roughness: .55 });
  [-.13, .13].forEach(x => mesh(new THREE.CapsuleGeometry(.1, .55, 6, 16), std(P.pants), x, .38, 0, root));
  const torso = grp(root, 0, .78, 0);
  mesh(new THREE.CapsuleGeometry(.3, .45, 8, 24), HOOD, 0, .42, 0, torso);
  const neck = grp(torso, 0, .92, 0); mesh(new THREE.CylinderGeometry(.08, .09, .12, 16), SKIN, 0, .04, 0, neck);
  const head = grp(neck, 0, .1, 0);
  mesh(new THREE.SphereGeometry(.3, 40, 28), SKIN, 0, .28, 0, head).scale.set(1, 1.08, .98);
  const hair = mesh(new THREE.SphereGeometry(.31, 40, 20, 0, Math.PI * 2, 0, 1.35), std(P.hair, { roughness: .9 }), 0, .32, -.02, head); hair.rotation.x = -.35;
  [-1, 1].forEach(s => mesh(new THREE.SphereGeometry(.06, 16, 12), SKIN, s * .3, .28, 0, head).scale.set(.5, 1, .8));
  mesh(new THREE.SphereGeometry(.045, 16, 12), SKIN, 0, .25, .3, head);
  const eyes = [-1, 1].map(s => { const g = grp(head, s * .11, .33, .25);
    mesh(new THREE.SphereGeometry(.055, 24, 16), std(0xffffff, { roughness: .2 }), 0, 0, 0, g, false).scale.set(1, 1.1, .6);
    mesh(new THREE.SphereGeometry(.028, 16, 12), std(0x1b1410, { roughness: .1 }), 0, 0, .035, g, false); return g; });
  const brows = [-1, 1].map(s => { const b = grp(head, s * .11, .43, .27); mesh(new THREE.CapsuleGeometry(.014, .08, 4, 8), std(P.hair), 0, 0, 0, b, false).rotation.z = Math.PI / 2; return b; });
  const mouth = mesh(new THREE.SphereGeometry(.05, 24, 12), std(0x5a1f22, { roughness: .6 }), 0, .14, .27, head, false); mouth.scale.set(1.3, .25, .4);
  const arms = [-1, 1].map(s => { const sh = grp(torso, s * .36, .72, 0); mesh(new THREE.CapsuleGeometry(.08, .26, 6, 12), HOOD, 0, -.17, 0, sh);
    const el = grp(sh, 0, -.36, 0); mesh(new THREE.CapsuleGeometry(.075, .24, 6, 12), HOOD, 0, -.15, 0, el); mesh(new THREE.SphereGeometry(.07, 16, 12), SKIN, 0, -.33, 0, el);
    return { sh, el, s }; });
  const face = st => {
    eyes.forEach(g => g.scale.set(1 + st.shock * .2, st.blink ? .1 : (1 + st.shock * .3) * (1 - st.smug * .45), 1));
    brows.forEach((b, i) => { const s = i ? 1 : -1; b.position.y = .43 + st.shock * .05 + st.happy * .02 - st.slump * .01; b.rotation.z = s * (st.slump * .35 - st.shock * .1 + st.smug * .2 * s); });
    const open = clamp(st.mouth * 1.2 + st.shock * .4);
    mouth.scale.set(1.3 - open * .3 + st.happy * .4, .25 + open * .9, .4);
  };
  return { root, torso, neck, head, arms, face };
}

// ---------- Bot: white glossy robot, dark screen face with emissive eyes ----------
function makeBot() {
  const root = grp(scene, .95, 0, .55); root.rotation.y = -.5;
  const SHELL = phys(P.bot, { roughness: .25, clearcoat: 1 }), TRIM = std(P.botTrim, { roughness: .4, metalness: .3 });
  mesh(new THREE.CylinderGeometry(.22, .28, .5, 32), TRIM, 0, .25, 0, root);
  const torso = grp(root, 0, .5, 0);
  mesh(new THREE.CapsuleGeometry(.32, .3, 8, 32), SHELL, 0, .4, 0, torso);
  const chest = mesh(new THREE.CircleGeometry(.09, 32), new THREE.MeshBasicMaterial({ color: P.ink }), 0, .45, .325, torso, false); chest.material.toneMapped = false;
  const neck = grp(torso, 0, .82, 0); mesh(new THREE.CylinderGeometry(.07, .07, .1, 16), TRIM, 0, .04, 0, neck);
  const head = grp(neck, 0, .1, 0);
  mesh(new THREE.CapsuleGeometry(.26, .32, 8, 32), SHELL, 0, .28, 0, head).rotation.z = Math.PI / 2;
  const scr = mesh(new THREE.CapsuleGeometry(.19, .26, 8, 32), std(P.screen, { roughness: .15 }), 0, .28, .1, head, false); scr.rotation.z = Math.PI / 2; scr.scale.set(1, 1, .9);
  const EYE = new THREE.MeshBasicMaterial({ color: P.ink }); EYE.toneMapped = false;
  const eyes = [-1, 1].map(s => mesh(new THREE.CapsuleGeometry(.035, .05, 4, 12), EYE, s * .12, .31, .27, head, false));
  const mouth = mesh(new THREE.CapsuleGeometry(.012, .08, 4, 8), EYE, 0, .2, .275, head, false); mouth.rotation.z = Math.PI / 2;
  const sweat = mesh(new THREE.SphereGeometry(.03, 16, 12), phys(0x9fd6ff, { transmission: .4, roughness: .05 }), .3, .45, .15, head, false);
  [-1, 1].forEach(s => mesh(new THREE.SphereGeometry(.08, 24, 16), TRIM, s * .44, .28, 0, head));
  const arms = [-1, 1].map(s => { const sh = grp(torso, s * .38, .62, 0); mesh(new THREE.CapsuleGeometry(.065, .22, 6, 12), TRIM, 0, -.15, 0, sh);
    const el = grp(sh, 0, -.32, 0); mesh(new THREE.CapsuleGeometry(.06, .2, 6, 12), SHELL, 0, -.13, 0, el); mesh(new THREE.SphereGeometry(.075, 16, 12), TRIM, 0, -.3, 0, el);
    return { sh, el, s }; });
  const face = st => {
    eyes.forEach((e, i) => { const y = st.blink ? .12 : (1 + st.shock * .4) * (1 - st.smug * .55); e.scale.set(1 + st.happy * .2, y, 1); e.rotation.z = (i ? -1 : 1) * st.smug * .4; });
    mouth.scale.set(1, 1 + st.mouth * 1.5 + st.happy * .6, 1); mouth.scale.x = 1 + st.mouth * 2.5;
    sweat.visible = st.sweatK >= 0; if (sweat.visible) sweat.position.y = .45 - st.sweatK * .15;
  };
  return { root, torso, neck, head, arms, face };
}

const dude = makeDude(), bot = makeBot();
const facing = r => V(Math.sin(r.root.rotation.y), 0, Math.cos(r.root.rotation.y));
const rigs = {
  dude: { head: () => dude.head.localToWorld(V(0, .28, .1)), facing: facing(dude), size: .62 },
  bot: { head: () => bot.head.localToWorld(V(0, .28, .1)), facing: facing(bot), size: .62 },
};
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { samples: 4, type: THREE.HalfFloatType }));
composer.addPass(new RenderPass(scene, camera));
const bokeh = new BokehPass(scene, camera, { focus: 4, aperture: .0025, maxblur: .008 }); composer.addPass(bokeh);
composer.addPass(new OutputPass());

await run(t => {
  animateRig(dude, 'dude', t, .4); animateRig(bot, 'bot', t, 1.3);
  bot.torso.position.y = .5 + Math.sin(t * 2 * Math.PI / 1.9) * .012 + (TL.lines.find(l => l.who === 'bot' && t >= l.start && t < l.end) ? .01 : 0);
  mugs[1].rotation.y = Math.sin(t * .5) * .05;
  scene.updateMatrixWorld(true);
  const f = frameShot(camera, rigs, t, { fov: 32, medium: 7, tight: 5, wide: 13 });
  bokeh.uniforms.focus.value = camera.position.distanceTo(f.focus);
  bokeh.uniforms.aperture.value = f.shot.name === 'wide' ? .0008 : .0025;
  composer.render();
});
