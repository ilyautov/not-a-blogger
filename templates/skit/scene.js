// SPDX-License-Identifier: MIT
// Flat 2D dialogue skit on <canvas>. Everything is a function of time: window.setTime(t) draws one frame.
// The scene reads timeline.json (build_audio.py): shots, lines with words and mouth envelope, marks, phone messages,
// stamps and reactions. Change a line or a take -> rebuild timeline -> cuts and props move with the words.
// Rules: no state between frames, no Math.random() (seeded rng only), events from words, never from hand-typed seconds.
const FW = 1080, FH = 1920;
const TL = await (await fetch('timeline.json')).json();
const cv = document.getElementById('film'), out = cv.getContext('2d');
const world = document.createElement('canvas'); world.width = FW; world.height = FH; const c = world.getContext('2d');
const SANS = '"Helvetica Neue", Arial, sans-serif';
// neutral palette: replace with your own
const C = { wall: '#f1e7da', wall2: '#e6d8c6', floor: '#c9b49a', table: '#8a6446', hood: '#4f7cac', skin: '#f0c3a0', hair: '#3b2a20',
  bot: '#eef2f5', botD: '#9aa6b2', screen: '#13202b', ink: '#6ff7e8', ink2: '#ffffff', accent: '#ff7a59', text: '#1b1f24' };

// ---------- math ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = v => 1 - Math.pow(1 - clamp(v), 3);
const back = v => { const x = clamp(v), k = 1.7; return 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); };
const win = (t, a, b, ain = .2, aout = .3) => Math.min(ease((t - a) / ain), 1 - ease((t - b) / aout));
const sines = (t, l) => l.reduce((s, [amp, f, ph]) => s + amp * Math.sin(t * f + ph), 0);

// ---------- timeline queries ----------
const shotAt = t => { let s = TL.shots[0]; for (const x of TL.shots) if (t >= x.start) s = x; return s; };
const lineAt = (t, who) => TL.lines.find(l => l.who === who && t >= l.start && t < l.end);
const env = (t, who) => { const l = lineAt(t, who); if (!l) return 0; const f = (t - l.start) * TL.fps, i = Math.floor(f); return lerp(l.env[i] || 0, l.env[i + 1] || 0, f - i); };
const react = (t, who, kind) => Math.max(0, ...TL.reactions.filter(r => r.who === who && r.kind === kind).map(r => win(t, r.a, r.b)));
const blink = (t, ph) => ((t + ph * 2.3) % (3.1 + ph * .9)) < .12;

// ---------- drawing helpers ----------
function rr(x, y, w, h, r, col) { c.beginPath(); c.roundRect(x, y, w, h, r); c.fillStyle = col; c.fill(); }
function ell(x, y, rx, ry, col, rot = 0) { c.beginPath(); c.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), rot, 0, Math.PI * 2); c.fillStyle = col; c.fill(); }
function txt(s, x, y, size, col, align = 'center', w = 700) { c.font = `${w} ${size}px ${SANS}`; c.textAlign = align; c.fillStyle = col; c.fillText(s, x, y); }

function room() {
  c.fillStyle = C.wall; c.fillRect(-800, -800, FW + 1600, FH + 1600);
  rr(90, 420, 360, 460, 18, '#fff7e8'); rr(110, 440, 320, 420, 10, '#cfe6f2');           // window
  c.fillStyle = C.wall2; c.fillRect(-800, 1180, FW + 1600, 60);                           // skirting
  c.fillStyle = C.floor; c.fillRect(-800, 1240, FW + 1600, FH + 800);
  rr(560, 520, 300, 200, 14, '#d9c9b3'); for (let i = 0; i < 3; i++) rr(590 + i * 90, 560, 60, 120, 6, ['#e0a37a', '#8fb7a4', '#c7c0e8'][i]);  // shelf
}
function table() { rr(140, 1320, 800, 46, 22, C.table); rr(500, 1366, 80, 380, 10, '#5b4535'); rr(330, 1268, 70, 60, 14, C.accent); rr(690, 1268, 70, 60, 14, '#6f9ec8'); }

// Dude: generic guy in a hoodie. x,y = feet-ish anchor of the bust.
function dude(t, x, y) {
  const m = env(t, 'dude'), sh = react(t, 'dude', 'shock'), sl = react(t, 'dude', 'slump'), sm = react(t, 'dude', 'smug');
  const bob = Math.sin(t * 1.7) * 4 + m * 6, tilt = sines(t, [[.02, .4, 1]]) + sl * .08;
  c.save(); c.translate(x, y + sl * 18); c.rotate(tilt);
  rr(-170, -260 + bob * .3, 340, 420, 120, C.hood);                                          // body
  rr(-60, -300, 120, 80, 30, C.skin);                                                        // neck
  c.translate(0, -470 + bob - sh * 14);
  ell(0, 0, 150, 165, C.skin); ell(-150, 10, 24, 36, C.skin); ell(150, 10, 24, 36, C.skin);  // head, ears
  c.beginPath(); c.ellipse(0, -60, 158, 120, 0, Math.PI, 0); c.fillStyle = C.hair; c.fill();  // hair
  const eh = blink(t, .4) && sh < .5 ? 3 : 22 * (1 + sh * .5) * (1 - sm * .5);
  for (const s of [-1, 1]) {
    ell(s * 55, 10, 26 * (1 + sh * .25), eh, '#fff'); if (eh > 4) ell(s * 55, 12, 12, Math.min(12, eh * .6), '#1b1410');
    c.save(); c.translate(s * 55, -38 - sh * 18 - m * 6); c.rotate(s * (sl * .35 - sh * .1 + sm * .2)); rr(-34, -7, 68, 14, 7, C.hair); c.restore();
  }
  ell(0, 50, 16, 14, '#e8a988');                                                              // nose
  const open = clamp(m * 1.2 + sh * .4);
  ell(0, 100, 38 - open * 8 + sm * 10, 6 + open * 30, '#5a1f22');                             // mouth from the envelope
  c.restore();
}
// Bot: neutral robot with a screen face.
function bot(t, x, y) {
  const m = env(t, 'bot'), sm = react(t, 'bot', 'smug'), sh = react(t, 'bot', 'shock'), hap = react(t, 'bot', 'happy');
  const bob = Math.sin(t * 2 * Math.PI / 1.9) * 6 + m * 5;
  c.save(); c.translate(x, y);
  rr(-150, -250 + bob * .3, 300, 400, 70, C.bot); ell(0, -80 + bob * .3, 40, 40, C.ink);       // body + chest light
  rr(-26, -300, 52, 70, 12, C.botD); c.translate(0, -470 + bob); c.rotate(sines(t, [[.025, .5, 2]]) + sm * .08);
  rr(-190, -140, 380, 270, 90, C.bot); rr(-150, -100, 300, 190, 60, C.screen);                 // head + screen
  ell(-205, 0, 26, 40, C.botD); ell(205, 0, 26, 40, C.botD); rr(-6, -210, 12, 75, 6, C.botD); ell(0, -215, 18, 18, m > .3 ? C.ink2 : C.ink);
  c.shadowColor = C.ink; c.shadowBlur = 24;
  const eh = blink(t, 1.3) ? 4 : 34 * (1 + sh * .4) * (1 - sm * .55);
  for (const s of [-1, 1]) { c.save(); c.translate(s * 70, -20); c.rotate(-s * sm * .4); rr(-20, -eh / 2, 40, eh, 18, C.ink); c.restore(); }
  rr(-30 - m * 30 - hap * 10, 48 - m * 14, 60 + m * 60 + hap * 20, 10 + m * 28, 10, C.ink);
  c.shadowBlur = 0; c.restore();
}
// Phone insert: chat bubbles appear on their words (TL.phone).
function phone(t) {
  c.fillStyle = '#20262d'; c.fillRect(-800, -800, FW + 1600, FH + 1600);
  rr(230, 600, 620, 1240, 84, '#0d0f12'); rr(250, 620, 580, 1200, 68, '#f4f5f7');   // below the subtitle zone
  rr(250, 620, 580, 130, 68, '#e3e7ec'); txt('Chat', 540, 705, 42, C.text);
  let y = 810;
  for (const msg of TL.phone) {
    const k = ease((t - msg.at) / .25); if (k <= 0) continue;
    const mine = msg.from === 'dude', w = Math.min(500, 60 + msg.text.length * 20);
    c.save(); c.globalAlpha = k; c.translate(0, (1 - k) * 40);
    rr(mine ? 800 - w : 280, y, w, 100, 40, mine ? '#4f7cac' : '#dfe4ea'); txt(msg.text, mine ? 800 - w / 2 : 280 + w / 2, y + 64, 36, mine ? '#fff' : C.text, 'center', 500);
    c.restore(); y += 130;
  }
}
// Stamp: a pill that pops with overshoot on its word.
function stamps(t) {
  for (const s of TL.stamps) {
    const k = t - s.at; if (k < 0 || k > 1.4) continue;
    const sc = back(k / .25) * (1 - ease((k - 1.15) / .25));
    out.save(); out.translate(540, 1500); out.rotate(-.06); out.scale(sc, sc);
    out.font = `800 92px ${SANS}`; const w = out.measureText(s.text).width + 90;
    out.beginPath(); out.roundRect(-w / 2, -80, w, 140, 70); out.fillStyle = C.accent; out.fill();
    out.fillStyle = '#fff'; out.textAlign = 'center'; out.fillText(s.text, 0, 22); out.restore();
  }
}
// Subtitles: phrase of the current line, words appear when spoken.
function captions(t) {
  let l = null;                                  // the latest started line; it stays up to 0.5 s after its end
  for (const x of TL.lines) if (t >= x.start - .05) l = x;
  if (!l || t > l.end + .5) return;
  out.save(); out.font = `700 66px ${SANS}`; out.textAlign = 'left'; out.shadowColor = 'rgba(0,0,0,.8)'; out.shadowBlur = 22;
  const gap = 20, rows = [[]]; let lw = 0;
  for (const w of l.words) { const ww = out.measureText(w[0]).width; if (lw + ww > 920 && rows.at(-1).length) { rows.push([]); lw = 0; } rows.at(-1).push([...w, ww]); lw += ww + gap; }
  rows.forEach((r, i) => { let x = 540 - (r.reduce((a, w) => a + w[3], 0) + gap * (r.length - 1)) / 2;
    for (const [w, s, , ww] of r) { const k = clamp((t - s + .04) / .12); out.globalAlpha = k; out.fillStyle = '#fff'; out.fillText(w, x, 300 + i * 84 + (1 - ease(k)) * 14); x += ww + gap; } });
  out.restore();
}

// shot presets: camera center (x, y) and scale on the world canvas
const SHOTS = { two: [545, 1010, 1.15], dude: [330, 900, 1.55], bot: [760, 900, 1.55] };
function render(t) {
  const s = shotAt(t), lt = t - s.start;
  c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, FW, FH);
  if (s.name === 'phone') phone(t);
  else {
    const [cx, cy, sc] = SHOTS[s.name] || SHOTS.two, push = 1 + .04 * ease(lt / 3);
    c.translate(FW / 2, FH / 2); c.scale(sc * push, sc * push); c.translate(-cx, -cy);
    room(); dude(t, 330, 1300); bot(t, 760, 1300); table();
  }
  out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, FW, FH);
  const hx = sines(t, [[10, .8, 0], [4, 2.1, 1]]), hy = sines(t, [[8, .7, 2], [3, 1.7, 0]]);   // handheld from sines
  const punch = lt < .16 && s.start > 0 ? 1 + (1 - ease(lt / .16)) * .05 : 1;                 // small punch-in on each cut
  out.translate(FW / 2 + hx, FH / 2 + hy); out.scale(1.03 * punch, 1.03 * punch); out.drawImage(world, -FW / 2, -FH / 2);
  out.setTransform(1, 0, 0, 1, 0, 0);
  const top = out.createLinearGradient(0, 0, 0, 560); top.addColorStop(0, 'rgba(0,0,0,.45)'); top.addColorStop(1, 'rgba(0,0,0,0)');
  out.fillStyle = top; out.fillRect(0, 0, FW, 560);
  stamps(t); captions(t);
}
window.setTime = t => { render(clamp(t, 0, TL.duration)); return true; };
await document.fonts.ready;
window.setTime(+(new URLSearchParams(location.search).get('t') || 0));
window.ready = true;
