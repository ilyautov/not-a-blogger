// SPDX-License-Identifier: MIT
// Shared skeleton of the 3D skit: timeline, cuts, mouth envelope, reactions, rig animation, camera presets, subtitles.
// A style module (styles/*.js) only builds the world and the two characters, then calls run().
// Rules that keep renders reproducible:
//  1. setTime(t) is a pure function of t. No state between frames, no Math.random(), no Date.now().
//  2. Randomness only from the seeded PRNG (U.rng) evaluated at load time.
//  3. Motion is slow: drift uses two smooth sines under ~0.4 Hz. Harmonics at 5-8 Hz read as jitter.
import * as THREE from 'three';

export const Q = new URLSearchParams(location.search);
export const TL = await (await fetch(Q.get('timeline') || 'timeline.json')).json();
export const W = 1080, H = 1920;
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------- math ----------
export const U = {
  rng(seed) { let s = seed % 2147483647 || 1; return () => (s = (s * 16807) % 2147483647) / 2147483647; },
  clamp: (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)),
  lerp: (a, b, k) => a + (b - a) * k,
  ease(k) { k = U.clamp(k); return k * k * (3 - 2 * k); },
  easeOut: k => 1 - Math.pow(1 - U.clamp(k), 3),
  easeBack(k) { k = U.clamp(k); const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
  // window: 0 before a, eases to 1 by a+ain, holds until b, eases back to 0 by b+aout
  win: (t, a, b, ain = .22, aout = .3) => Math.min(U.ease((t - a) / ain), 1 - U.ease((t - b) / aout)),
  drift: (t, f, ph) => Math.sin(t * f + ph) * .65 + Math.sin(t * f * 1.61 + ph * 1.3) * .35,
  hash(a, b) { let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177 | 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; },
  V,
};

// ---------- timeline queries ----------
export const cue = {
  shotAt(t) { let s = TL.shots[0]; for (const x of TL.shots) if (t >= x.start) s = x; return s; },
  lineAt: (t, who) => TL.lines.find(l => l.who === who && t >= l.start && t < l.end),
  env(t, who) {                                   // mouth opening 0..1, interpolated between frames
    const l = cue.lineAt(t, who); if (!l) return 0;
    const f = (t - l.start) * TL.fps, i = Math.floor(f);
    return U.lerp(l.env[i] || 0, l.env[i + 1] || 0, f - i);
  },
  react(t, who, kind) {                           // reaction weight 0..1 with eased in/out
    let w = 0;
    for (const r of TL.reactions || []) if (r.who === who && r.kind === kind) w = Math.max(w, U.win(t, r.a, r.b, r.ain ?? .2, r.aout ?? .3));
    return w;
  },
  active(t, who, kind) { return (TL.reactions || []).find(r => r.who === who && r.kind === kind && t >= r.a && t < r.b); },
  blink(t, ph) { const p = 3.1 + ph * .9, k = (t + ph * 2.3) % p; return k < .12; },
};

// ---------- rig animation shared by all styles ----------
// A rig is {root, torso, neck, arms: [{sh, el, s}], face(state)}; arms hang along -Y from the shoulder group.
const KINDS = ['shock', 'slump', 'facepalm', 'happy', 'smug', 'sweat', 'point', 'shrug'];
export function poseOf(t, who) {
  const p = { talk: cue.env(t, who) };
  for (const k of KINDS) p[k] = cue.react(t, who, k);
  return p;
}
const mix = (a, b, k) => a.map((v, i) => U.lerp(v, b[i], k));
export function animateRig(rig, who, t, ph = 0) {
  const p = poseOf(t, who), br = Math.sin(t * 2 * Math.PI / 3.6 + ph);
  rig.torso.scale.set(1 + br * .01, 1 + br * .014, 1);
  rig.torso.rotation.x = U.drift(t, .5, ph + 1) * .015 + p.slump * .1;
  rig.torso.rotation.z = U.drift(t, .4, ph + 2) * .015;
  // head nods ride the smoothed envelope, never the raw audio
  rig.neck.rotation.x = U.drift(t, .45, ph + 3) * .03 - p.talk * .05 + p.slump * .28 - p.shock * .08 + p.facepalm * .25;
  rig.neck.rotation.y = U.drift(t, .35, ph + 4) * .05;
  rig.neck.rotation.z = U.drift(t, .3, ph + 5) * .03 + p.shrug * .1 + p.smug * .08;
  const sw = U.drift(t, .6, ph + 6) * .03;
  let l = [.05 + sw, 0, -.12], le = [-.1, 0, 0], r = [.05 - sw, 0, .12], re = [-.1, 0, 0];
  const g = U.clamp(p.talk * 1.4) * .6;                                // talking hand
  r = mix(r, [-.5 - p.talk * .25, 0, .25], g); re = mix(re, [-.9, 0, 0], g);
  l = mix(l, [-.3, 0, -.5], p.shock); le = mix(le, [-.9, 0, 0], p.shock); r = mix(r, [-.3, 0, .5], p.shock); re = mix(re, [-.9, 0, 0], p.shock);
  const wave = p.happy * (.25 * Math.sin(t * 6));
  l = mix(l, [-2.6 + wave, 0, -.35], p.happy); le = mix(le, [-.3, 0, 0], p.happy); r = mix(r, [-2.6 - wave, 0, .35], p.happy); re = mix(re, [-.3, 0, 0], p.happy);
  r = mix(r, [-1.45, 0, .1], p.point); re = mix(re, [-.15, 0, 0], p.point);
  r = mix(r, [-2.3, 0, -.15], p.facepalm); re = mix(re, [-2.2, 0, 0], p.facepalm);
  l = mix(l, [-.2, 0, -.9], p.shrug); le = mix(le, [-1.2, 0, 0], p.shrug); r = mix(r, [-.2, 0, .9], p.shrug); re = mix(re, [-1.2, 0, 0], p.shrug);
  const [A, B] = rig.arms;
  A.sh.rotation.set(...l); A.el.rotation.set(...le); B.sh.rotation.set(...r); B.el.rotation.set(...re);
  const sweat = cue.active(t, who, 'sweat');
  rig.face({
    ...p, mouth: p.talk, blink: cue.blink(t, ph) && p.shock < .5, t,
    sweatK: sweat ? U.clamp((t - sweat.a) / Math.max(.6, sweat.b - sweat.a)) : -1,
  });
}

// ---------- camera presets ----------
// rigs: {dude, bot}; each has head() -> world Vector3 of the face, facing -> unit Vector3 toward the camera side, size -> head height.
// Composition for 9:16: face at ~45 % from the top, the upper third stays free for subtitles.
export function frameShot(camera, rigs, t, opt = {}) {
  const s = cue.shotAt(t), k = U.clamp((t - s.start) / Math.max(.5, s.end - s.start)), push = U.ease(k);
  const fov = opt.fov || 32;
  let target, dir, dist;
  const pick = who => rigs[who];
  if (s.name === 'wide') {
    target = rigs.dude.head().add(rigs.bot.head()).multiplyScalar(.5);
    dir = rigs.dude.facing.clone().add(rigs.bot.facing).normalize().add(V(0, .18, 0)).normalize();
    dist = (opt.wide || 9) * rigs.dude.size * (1 - .05 * push);
  } else {
    const who = s.name.startsWith('bot') ? 'bot' : 'dude', R = pick(who), tight = s.name.endsWith('_tight');
    target = R.head(); dir = R.facing.clone().add(V(0, .06, 0)).normalize();
    dist = (tight ? (opt.tight || 3.2) : (opt.medium || 4.6)) * R.size * (1 - (tight ? .06 : .08) * push);
  }
  const hh = 2 * dist * Math.tan(THREE.MathUtils.degToRad(fov / 2));
  const look = target.clone().add(V(0, -.05 * hh, 0));
  const pos = target.clone().addScaledVector(dir, dist);
  const ph = s.start * 7.3;                                           // handheld: tiny, slow, seeded by shot start
  pos.x += U.drift(t, .5, ph) * .012 * dist; pos.y += U.drift(t, .42, ph + 2) * .008 * dist;
  camera.position.copy(pos); camera.fov = fov; camera.updateProjectionMatrix(); camera.lookAt(look);
  return { shot: s, focus: target, dist };
}

// ---------- subtitles (HTML layer, never inside the 3D world) ----------
const subEl = document.getElementById('sub');
export function subtitle(t) {
  let cur = null; const L = TL.lines;
  for (let i = 0; i < L.length; i++) { const l = L[i], nx = L[i + 1]; if (t >= l.start - .04 && t < (nx ? Math.min(nx.start - .04, l.end + .9) : l.end + .7)) cur = l; }
  const s = cur ? cur.text : '';
  if (subEl && subEl.dataset.t !== s) { subEl.dataset.t = s; subEl.textContent = s; }
}

// ---------- boot ----------
export async function run(update) {
  window.setTime = t => { update(t); subtitle(t); return true; };
  await document.fonts.ready;
  window.setTime(+(Q.get('t') || 0));
  window.ready = true;
}
