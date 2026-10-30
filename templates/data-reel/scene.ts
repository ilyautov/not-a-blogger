// SPDX-License-Identifier: MIT
// Data reel scene for the starter (copy to scene/scene.ts). Every number drawn here comes from reel.json -> n,
// which reel_from_numbers.py builds from real-numbers.json. Never type a number into this file.
// Contract with the starter: window.ready, window.setTime(t), window.shotTimes (cuts for the sound), window.events (marks for SFX).
// Shots: total (odometer) -> top folders (bars) -> by kind (two tiles) -> old files (100-cell grid) -> source card.
type Cue = {id: number; start: number; end: number; text: string};
type Word = {line: number; text: string; start: number; end: number};
type Story = {duration: number; cues: Cue[]; words: Word[]};
type Bar = {name: string; gb: number; fmt: string};
type Nums = {target: string; total_gb: number; top1_name: string; top1_pct: number; video_gb: number; archives_gb: number; old_pct: number;
  fmt: Record<string, string>; bars: Bar[]};
type Reel = {n: Nums; source: string};
interface Window {ready: boolean; setTime: (t: number) => Promise<void>; shotTimes: number[]; events: Record<string, number>}

const FW = 1080, FH = 1920;
// neutral palette: replace with your own
const BG = '#0e1116', PANEL = '#171c24', ACC = '#3ddbd9', WARM = '#ffb547', WHITE = '#ffffff', GREY = '#8b95a3', DIM = '#2a313c';
const SANS = '"Helvetica Neue", Arial, sans-serif';
const canvas = document.querySelector<HTMLCanvasElement>('#film')!;
const out = canvas.getContext('2d')!;
const world = document.createElement('canvas'); world.width = FW; world.height = FH;
const c = world.getContext('2d')!;

const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = (v: number) => 1 - Math.pow(1 - clamp(v), 3);
const inout = (v: number) => {const x = clamp(v); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;};
const back = (v: number) => {const x = clamp(v), k = 1.7; return 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2);};
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const sines = (t: number, l: [number, number, number][]) => l.reduce((s, [amp, f, ph]) => s + amp * Math.sin(t * f + ph), 0);

function text(s: string, x: number, y: number, size: number, col = WHITE, align: CanvasTextAlign = 'center', w = 700) {
  c.font = `${w} ${size}px ${SANS}`; c.textAlign = align; c.textBaseline = 'alphabetic'; c.fillStyle = col; c.fillText(s, x, y); return c.measureText(s).width;
}
function box(x: number, y: number, w: number, h: number, col: string, r = 24) {c.beginPath(); c.roundRect(x, y, w, h, r); c.fillStyle = col; c.fill();}
function bg() {c.fillStyle = BG; c.fillRect(-600, -600, FW + 1200, FH + 1200);}
function cam(cx: number, cy: number, s: number) {c.translate(FW / 2, FH / 2); c.scale(s, s); c.translate(-cx, -cy);}
// a number that counts up to its final shown form; the final frame shows exactly the string from reel.json
function counter(final: string, value: number, k: number, x: number, y: number, size: number, col: string) {
  const dec = final.includes(',') || final.includes('.') ? 1 : 0, sep = final.includes(',') ? ',' : '.';
  const s = k >= 1 ? final : (value * inout(k)).toFixed(dec).replace('.', sep);
  text(s, x, y, size, col);
}

async function main() {
  const s: Story = await (await fetch('story.json')).json();
  const reel: Reel = await (await fetch('reel.json')).json(); const N = reel.n, F = N.fmt;
  await document.fonts.ready;
  const W = s.words, END = s.duration;
  const norm = (x: string) => x.toLowerCase().replace(/ё/g, 'е').replace(/[^a-zа-я0-9]/g, '');
  // time of the first word of a line starting with prefix; falls back to the line start so edited lines never crash
  function wt(line: number, prefix: string) {
    const w = W.find(x => x.line === line && prefix !== '' && norm(x.text).startsWith(norm(prefix)));
    return w ? w.start : s.cues[Math.min(line, s.cues.length - 1)].start;
  }
  const E = {total: wt(0, F.total_gb), top: wt(1, F.top1_pct), kinds: wt(2, F.video_gb), old: wt(3, F.old_pct)};
  const cue = (i: number) => s.cues[Math.min(i, s.cues.length - 1)].start;

  function total(t: number) {
    bg(); const k = ease((t - E.total + .1) / 1.1);
    box(190, 640, 700, 560, PANEL, 40); box(190, 600, 300, 90, PANEL, 30);                    // folder shape
    text(N.target, 540, 790, 64, GREY);
    counter(F.total_gb, N.total_gb, k, 540, 1040, 230, ACC);
    text('GB', 540, 1140, 64, WHITE);
  }
  function bars(t: number) {
    bg(); text(N.target, 540, 700, 52, GREY);
    const B = N.bars.slice(0, 6), max = Math.max(...B.map(b => b.gb), 1e-9);
    B.forEach((b, i) => {
      const y = 800 + i * 150, k = ease((t - cue(1) - i * .08) / .5), hot = i === 0 && t >= E.top;
      text(b.name, 140, y + 20, 44, hot ? WHITE : GREY, 'left', 600);
      box(140, y + 40, 800, 56, DIM, 28);
      box(140, y + 40, Math.max(56, 800 * (b.gb / max) * k), 56, hot ? WARM : ACC, 28);
      text(b.fmt + ' GB', 940, y + 20, 44, hot ? WARM : WHITE, 'right');
    });
    if (t >= E.top) {const k = back((t - E.top) / .3); c.save(); c.translate(540, 1780); c.scale(k, k); text(F.top1_pct + '%', 0, 0, 120, WARM); c.restore();}
  }
  function kinds(t: number) {
    bg();
    const tiles: [string, string, number, string][] = [['video', F.video_gb, N.video_gb, ACC], ['archives', F.archives_gb, N.archives_gb, WARM]];
    tiles.forEach(([label, f, v, col], i) => {
      const at = i === 0 ? E.kinds : E.kinds + .6, k = ease((t - at + .1) / .5), y = 700 + i * 480;
      c.save(); c.globalAlpha = k; c.translate(0, (1 - k) * 60);
      box(150, y, 780, 400, PANEL, 36); text(label, 540, y + 110, 52, GREY);
      counter(f, v, ease((t - at) / .8), 540, y + 300, 170, col); c.restore();
    });
  }
  function old(t: number) {
    bg(); const pct = clamp(N.old_pct / 100), k = ease((t - E.old + .2) / 1.2);
    for (let i = 0; i < 100; i++) {
      const x = 190 + (i % 10) * 72, y = 620 + Math.floor(i / 10) * 72, on = i < Math.round(pct * 100 * k);
      box(x, y, 60, 60, on ? GREY : DIM, 10);
    }
    counter(F.old_pct, N.old_pct, k, 540, 1560, 200, WHITE); text('%', 760, 1560, 90, GREY);
  }
  function source(t: number) {
    bg(); const k = ease((t - cue(4)) / .5);
    c.save(); c.translate(0, (1 - k) * 200);
    box(170, 640, 740, 700, '#f4f3ee', 24);
    text('real-numbers.json', 540, 780, 54, '#1b1f24');
    text(F.total_gb + ' GB', 540, 960, 110, '#1b1f24');
    text(reel.source.replace(/^real-numbers\.json \(|\)$/g, '').split(',').slice(-1)[0].trim(), 540, 1100, 34, '#536067', 'center', 400);   // measurement time
    text('measured, not guessed', 540, 1240, 42, '#536067', 'center', 400);
    c.restore();
  }
  const shots: {at: number; draw: (t: number, lt: number) => void}[] = [
    {at: 0, draw: (t, lt) => {cam(540, 960, lerp(1, 1.06, ease(lt / 3))); total(t);}},
    {at: cue(1) - .05, draw: (t, lt) => {cam(540, 1100, lerp(1, 1.04, ease(lt / 3))); bars(t);}},
    {at: cue(2) - .05, draw: (t, lt) => {cam(540, 1060, lerp(1, 1.05, ease(lt / 3))); kinds(t);}},
    {at: cue(3) - .05, draw: (t, lt) => {cam(540, 1060, lerp(1, 1.06, ease(lt / 3))); old(t);}},
    {at: cue(4) - .05, draw: (t, lt) => {cam(540, 990, lerp(1, 1.04, ease(lt / 2))); source(t);}},
  ];
  for (let i = 1; i < shots.length; i++) if (shots[i].at <= shots[i - 1].at) throw new Error('cuts out of order: fewer than 5 lines?');
  window.events = E; window.shotTimes = shots.map(x => x.at);

  // subtitles: current line, words appear when spoken, numbers in the accent color
  function captions(t: number) {
    let li = -1; for (const q of s.cues) if (t >= q.start - .05) li = q.id;
    if (li < 0 || t > s.cues[li].end + .5) return;
    const ws = W.filter(w => w.line === li); const gap = 20, rows: Word[][] = [[]]; let lw = 0;
    out.save(); out.font = `700 68px ${SANS}`; out.textAlign = 'left'; out.shadowColor = 'rgba(0,0,0,.8)'; out.shadowBlur = 22;
    for (const w of ws) {const ww = out.measureText(w.text).width; if (lw + ww > 940 && rows[rows.length - 1].length) {rows.push([]); lw = 0;} rows[rows.length - 1].push(w); lw += ww + gap;}
    rows.forEach((r, i) => {
      let x = 540 - (r.reduce((a, w) => a + out.measureText(w.text).width, 0) + gap * (r.length - 1)) / 2;
      for (const w of r) {const k = clamp((t - w.start + .04) / .12); out.globalAlpha = k; out.fillStyle = /\d/.test(w.text) ? ACC : WHITE;
        out.fillText(w.text, x, 320 + i * 88 + (1 - ease(k)) * 14); x += out.measureText(w.text).width + gap;}
    });
    out.restore();
  }
  function render(t: number) {
    let i = 0; for (let k = 0; k < shots.length; k++) if (t >= shots[k].at) i = k;
    const sh = shots[i], lt = t - sh.at;
    c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.clearRect(0, 0, FW, FH); c.save(); sh.draw(t, lt); c.restore();
    out.setTransform(1, 0, 0, 1, 0, 0); out.globalAlpha = 1; out.fillStyle = '#000'; out.fillRect(0, 0, FW, FH);
    const hx = sines(t, [[12, .8, 0], [5, 2.1, 1]]), hy = sines(t, [[10, .7, 2], [4, 1.7, 0]]);    // handheld camera from sines
    const punch = i > 0 && lt < .16 ? 1 + (1 - ease(lt / .16)) * .05 : 1;
    out.translate(FW / 2 + hx, FH / 2 + hy); out.scale(1.04 * punch, 1.04 * punch); out.drawImage(world, -FW / 2, -FH / 2);
    out.setTransform(1, 0, 0, 1, 0, 0);
    const top = out.createLinearGradient(0, 0, 0, 600); top.addColorStop(0, 'rgba(0,0,0,.55)'); top.addColorStop(1, 'rgba(0,0,0,0)');
    out.fillStyle = top; out.fillRect(0, 0, FW, 600);
    captions(t);
  }
  window.setTime = async (t: number) => render(clamp(t, 0, END));
  await window.setTime(0); window.ready = true;
}
main().catch(e => {console.error(e); throw e;});
