// Учебная сцена «подписка за 200 рублей»: один предмет — телефон во весь кадр, весь кадр рисуется на <canvas> кодом.
// Главная учебная цель — связь голоса и движения. Места, где слово управляет картинкой, помечены «ГОЛОС → ДВИЖЕНИЕ».
// Правила, которые нельзя ломать:
//  1. setTime(t) — чистая функция от t: никакого состояния между кадрами, никакого Math.random и Date.now.
//  2. Всё случайное — из сидированного PRNG rng(seed), посчитано один раз при загрузке.
//  3. Время событий берётся из слов голоса (wt): сменил текст или голос — сцена сама переехала.
//  4. Наружу: window.ready, window.setTime, window.shotTimes (склейки для звука), window.events (метки для SFX),
//     window.counterAt(t) — что показывает счётчик в момент t (для численной проверки синхронности «ноля»).
// Грамматика рила: телефон во весь кадр, без заголовков и хрома, движение внутри кадра всегда, камера дрейфует,
// у каждого движения свой характер кривой (пружина, перелёт, экспонента, плавный вход-выход).
// Петля: последний кадр совпадает с первым — дрейф собран из гармоник периода LAST, финал возвращает камеру и экран.
// Сборка: tsc -p scene (см. scene/tsconfig.json) -> build/scene.js.
type Cue = {id: number; start: number; end: number; text: string};
type Word = {line: number; text: string; start: number; end: number};
type Story = {duration: number; cues: Cue[]; words: Word[]};
interface Window {
  ready: boolean; setTime: (t: number) => Promise<void>; shotTimes: number[]; events: Record<string, number>;
  counterAt: (t: number) => {text: string; settled: boolean};
  setQAMode?: (enabled: boolean) => void;
}

// Optional still_lint contract: keep object movement, remove camera and postprocessing.
let qaMode = false;
window.setQAMode = (enabled: boolean) => {qaMode = enabled;};

const FW = 1080, FH = 1920, FPS = 30;
// Нейтральная палитра: графит, камень, бумага. Интерфейс и сервис «Медиатека+» вымышлены.
const INK = '#15171a', INK2 = '#5d636b', PAPER = '#fbfaf6', BODY = '#1c1e21', SCREEN = '#eef0f1', CARD = '#ffffff';
const RED = '#cf4a3f', GREEN = '#2f9e6a', OFF = '#c3c7cb', ICON = '#56636e', WALL1 = '#2f3a44', WALL2 = '#8c8f87';
const NOTIF_BG = 'rgba(246,246,243,.92)';
const SANS = 'Onest, "Helvetica Neue", Arial, sans-serif', ACCENT = 'Accent, Georgia, serif', MONO = 'Menlo, "DejaVu Sans Mono", monospace';
const canvas = document.querySelector<HTMLCanvasElement>('#film')!;
const out = canvas.getContext('2d')!;                       // финальный кадр: whip, виньетка, зерно, субтитры
const world = document.createElement('canvas'); world.width = FW; world.height = FH;
const c = world.getContext('2d')!;                          // «мир»: стол и телефон, его снимает камера

// ---------- математика времени: у каждой кривой свой характер ----------
const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const outCubic = (v: number) => 1 - Math.pow(1 - clamp(v), 3);                                  // мягкая остановка
const inout = (v: number) => {const x = clamp(v); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;};  // камера: плавно туда-обратно
const outExpo = (v: number) => {const x = clamp(v); return x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);};  // счётчик: резкий старт, точная посадка
const spring = (u: number, w = 18, z = 7) => u <= 0 ? 0 : 1 - Math.exp(-z * u) * Math.cos(w * u);  // пружина 0 -> 1 с перелётом
const kick = (u: number, w = 30, z = 9) => u <= 0 ? 0 : Math.exp(-z * u) * Math.sin(w * u);        // затухающий толчок 0 -> 0
function rng(seed: number) {   // mulberry32: один сид — одна и та же последовательность на любой машине
  let a = seed >>> 0;
  return () => {a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296;};
}

// ---------- рисование ----------
function font(size: number, w = 700, fam = SANS) {c.font = `${w} ${size}px ${fam}`;}
function text(s: string, x: number, y: number, size: number, col = INK, align: CanvasTextAlign = 'left', w = 700, fam = SANS) {
  font(size, w, fam); c.textAlign = align; c.textBaseline = 'alphabetic'; c.fillStyle = col; c.fillText(s, x, y); return c.measureText(s).width;
}
function rr(x: number, y: number, w: number, h: number, r: number, col: string) {c.beginPath(); c.roundRect(x, y, w, h, r); c.fillStyle = col; c.fill();}
function mix(a: string, b: string, k: number) {   // смешать два цвета #rrggbb
  const p = (s: string) => [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16)); const A = p(a), B = p(b);
  return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], clamp(k)))).join(',')})`;
}

// Телефон в координатах мира: корпус чуть шире кадра, экран почти совпадает с кадром — «во весь кадр».
const SCR = {x: 18, y: 10, w: 1044, h: 1900, r: 96};
function screenPath() {c.beginPath(); c.roundRect(SCR.x, SCR.y, SCR.w, SCR.h, SCR.r);}
function statusBar(col: string) {
  text('08:17', 80, 78, 34, col, 'left', 700);
  rr(900, 52, 74, 32, 9, col); rr(978, 61, 6, 14, 3, col);
}

async function main() {
  const s: Story = await (await fetch('story.json')).json();
  // шрифты грузятся лениво, при первом использовании: без явной загрузки кадр 0 рисуется запасным шрифтом
  await Promise.all(['700 40px Onest', '400 40px Onest', 'italic 400 40px Accent'].map(f => document.fonts.load(f, 'Аа0₽')));
  await document.fonts.ready;
  const W = s.words, END = s.duration;
  const LAST = Math.max(1 / FPS, Math.round(END * FPS) / FPS - 1 / FPS);   // время последнего отрендеренного кадра
  const norm = (x: string) => x.toLowerCase().replace(/ё/g, 'е').replace(/[^a-zа-я0-9]/g, '');
  function wt(line: number, prefix: string) {
    const w = W.find(x => x.line === line && norm(x.text).startsWith(norm(prefix)));
    if (!w) throw new Error(`нет слова «${prefix}» в реплике ${line}`);
    return w.start;
  }
  // ====== ГОЛОС → ДВИЖЕНИЕ: четыре метки берутся из начала слов (voice-track.json -> story.json) ======
  //   cost    «двести»     — пуш «Списано 200 ₽» бьёт в стопку, камера вздрагивает, звук thud
  //   cancel  «продление»  — переключатель щёлкает, строка «Автопродление» гаснет, звук click
  //   zero    «ноль»       — разряды «200» докручиваются и встают в «0», панч камеры, звук pop
  //   receipt «чек»        — чек выползает из низа телефона, камера отъезжает, звук chord
  const E = {cost: wt(0, '200'), cancel: wt(1, 'продление'), zero: wt(2, '0'), receipt: wt(3, 'чек')};
  const WHIP = s.cues[1].start - .12;                                  // переброска в настройки за 0,12 с до «Отключаю»
  const lastEnd = W[W.length - 1].end;
  const M = Math.min(LAST - .45, Math.max(lastEnd - .05, LAST - .8));  // начало возврата к первому кадру (петля)
  const order = [E.cost, WHIP, E.cancel, E.zero, E.receipt, M];
  for (let i = 1; i < order.length; i++) if (order[i] <= order[i - 1]) throw new Error(`события не по порядку: ${order.map(v => v.toFixed(2))}`);
  const per = (t: number, k: number, ph: number) => Math.sin(2 * Math.PI * k * t / LAST + ph);  // гармоника периода петли

  const grain = document.createElement('canvas'); grain.width = 540; grain.height = 960;
  {const g = grain.getContext('2d')!, d = g.createImageData(540, 960), r = rng(7);
    for (let i = 0; i < d.data.length; i += 4) {const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255;}
    g.putImageData(d, 0, 0);}
  const bars: number[] = []; {const r = rng(11); for (let i = 0; i < 46; i++) bars.push(2 + Math.floor(r() * 4) * 3);}   // штрихкод чека

  // ---------- экран блокировки и стопка пушей ----------
  type N = {time: string; title: string; body: string; amount: string; amountCol: string};
  const STACK_Y = 860, NH = 168, NG = 18, NX = 56, NW = 968;
  const RECEIPT_N: N = {time: 'вчера', title: 'Чек сохранён', body: 'подписка за прошлый месяц', amount: '200 ₽', amountCol: INK};
  const OLD: N[] = [RECEIPT_N,
    {time: '23 сен', title: 'Списано за подписку', body: 'тариф «Месяц»', amount: '−200 ₽', amountCol: RED},
    {time: '23 авг', title: 'Списано за подписку', body: 'тариф «Месяц»', amount: '−200 ₽', amountCol: RED},
    {time: '23 июл', title: 'Списано за подписку', body: 'тариф «Месяц»', amount: '−200 ₽', amountCol: RED},
    {time: '23 июн', title: 'Списано за подписку', body: 'тариф «Месяц»', amount: '−200 ₽', amountCol: RED}];   // стопка заполняет экран
  const NEW: N = {time: 'сейчас', title: 'Списано за подписку', body: 'открывали за месяц: 1 раз', amount: '−200 ₽', amountCol: RED};
  function notif(n: N, x: number, y: number) {
    rr(x, y, NW, NH, 40, NOTIF_BG);
    rr(x + 28, y + 36, 96, 96, 24, ICON); text('М', x + 76, y + 100, 52, '#fff', 'center');
    text(`Медиатека+ · ${n.time}`, x + 150, y + 54, 30, INK2, 'left', 400);
    text(n.title, x + 150, y + 102, 40, INK);
    text(n.body, x + 150, y + 144, 32, INK2, 'left', 400);
    text(n.amount, x + NW - 34, y + 112, 52, n.amountCol, 'right');
  }
  function lock(t: number, prePush: boolean, skipTop: boolean) {
    const g = c.createLinearGradient(0, 0, 0, FH); g.addColorStop(0, WALL1); g.addColorStop(1, WALL2);
    c.fillStyle = g; c.fillRect(0, 0, FW, FH);
    const bx = 540 + 260 * per(t, 1, 0), by = 1250 + 180 * per(t, 1, 1.7);   // мягкий блик обоев плывёт всегда
    const rg = c.createRadialGradient(bx, by, 40, bx, by, 760); rg.addColorStop(0, 'rgba(255,244,226,.30)'); rg.addColorStop(1, 'rgba(255,244,226,0)');
    c.fillStyle = rg; c.fillRect(0, 0, FW, FH);
    statusBar('#fff');
    text('четверг, 23 октября', 540, 520, 40, 'rgba(255,255,255,.85)', 'center', 400);
    text('08:17', 540, 730, 210, '#fff', 'center', 400);
    // ГОЛОС → ДВИЖЕНИЕ: пуш падает сверху с ускорением и бьёт в стопку ровно в E.cost («двести»),
    // старые пуши получают пружинный толчок вниз в тот же момент.
    const shift = prePush ? 0 : spring(t - E.cost, 15, 8) * (NH + NG);
    OLD.forEach((n, i) => {if (!(skipTop && i === 0)) notif(n, NX, STACK_Y + i * (NH + NG) + shift);});
    if (!prePush) {
      const f0 = Math.max(0, E.cost - .24), k = clamp((t - f0) / Math.max(.01, E.cost - f0));
      const y = t < E.cost ? lerp(-260, STACK_Y, k * k) : STACK_Y + 34 * kick(t - E.cost, 24, 9);
      notif(NEW, NX, y);
    }
  }

  // ---------- настройки подписки ----------
  // Счётчик «Следующий платёж»: три разряда крутятся вниз, каждый докручивается к E.zero.
  const COLS = [{from: 2, steps: 2, dur: .42}, {from: 0, steps: 10, dur: .54}, {from: 0, steps: 20, dur: .66}];
  // ГОЛОС → ДВИЖЕНИЕ: положение разряда — outExpo от времени до начала слова «ноль»; при t = E.zero позиция целая.
  const colPos = (i: number, t: number) => COLS[i].steps * outExpo((t - (E.zero - COLS[i].dur)) / COLS[i].dur);
  const collapse = (t: number) => inout((t - (E.zero - .2)) / .2);   // лишние разряды схлопываются ровно к «ноль»
  const digitAt = (i: number, n: number) => (((COLS[i].from - n) % 10) + 10) % 10;
  window.counterAt = (t: number) => {
    const ps = COLS.map((_, i) => colPos(i, t)), col = collapse(t);
    const ds = ps.map((p, i) => digitAt(i, Math.round(p)));
    const shown = col < .5 ? ds.join('').replace(/^0+(?=\d)/, '') : String(ds[2]);
    return {text: shown, settled: ps.every(p => Math.abs(p - Math.round(p)) < .02) && (col < .001 || col > .999)};
  };
  function counter(t: number, x: number, base: number, size: number) {
    font(size); const dw = c.measureText('0').width, H = size * 1.02, col = collapse(t);
    const widths = [dw * (1 - col), dw * (1 - col), dw];
    const pop = 1 + .09 * kick(t - E.zero, 20, 8);   // поп: цифра коротко подпрыгивает на «ноль»
    c.save(); c.translate(x, base); c.scale(pop, pop); c.translate(-x, -base);
    let cx = x;
    widths.forEach((w, i) => {
      if (w < .5) return;
      const p = colPos(i, t), n = Math.floor(p), f = p - n;
      c.save(); c.beginPath(); c.rect(cx, base - size * .86, w, size * 1.02); c.clip();
      c.globalAlpha = i < 2 ? 1 - col : 1;
      text(String(digitAt(i, n)), cx + w / 2, base + f * H, size, INK, 'center');
      if (f > .001) text(String(digitAt(i, n + 1)), cx + w / 2, base - H + f * H, size, INK, 'center');
      c.restore(); cx += w;
    });
    text('₽', cx + 22, base, size * .5, INK2, 'left', 700);
    c.restore();
  }
  function settings(t: number) {
    c.fillStyle = SCREEN; c.fillRect(0, 0, FW, FH);
    statusBar(INK);
    rr(60, 260, 150, 150, 36, ICON); text('М', 135, 362, 84, '#fff', 'center');
    text('Медиатека+', 240, 322, 56, INK);
    text('тариф «Месяц» · 200 ₽', 240, 382, 36, INK2, 'left', 400);
    // группа 1: автопродление
    rr(40, 470, 1000, 250, 40, CARD);
    // ГОЛОС → ДВИЖЕНИЕ: на «продление» ручка уходит пружиной, цвет гаснет за 0,12 с, строка тускнеет
    const off = spring(t - E.cancel, 20, 9), colk = clamp((t - E.cancel) / .12), dim = outCubic((t - E.cancel) / .35);
    c.globalAlpha = 1 - .55 * dim; text('Автопродление', 90, 580, 48, INK); c.globalAlpha = 1;
    c.globalAlpha = 1 - dim; text('продлится 23 ноября', 90, 650, 34, INK2, 'left', 400);
    c.globalAlpha = dim; text('доступ до 22 ноября', 90, 650, 34, INK2, 'left', 400); c.globalAlpha = 1;
    rr(800, 543, 180, 104, 52, mix(GREEN, OFF, colk));
    const kx = lerp(928, 852, off), stretch = 1 + .35 * Math.abs(kick(t - E.cancel, 20, 12));
    c.save(); c.shadowColor = 'rgba(0,0,0,.25)'; c.shadowBlur = 10; c.shadowOffsetY = 3;
    c.beginPath(); c.ellipse(kx, 595, 44 * stretch, 44, 0, 0, Math.PI * 2); c.fillStyle = '#fff'; c.fill(); c.restore();
    // группа 2: следующий платёж, крупный счётчик
    rr(40, 760, 1000, 520, 40, CARD);
    text('Следующий платёж', 90, 850, 40, INK2, 'left', 400);
    const z = outCubic((t - E.zero) / .25);
    c.globalAlpha = 1 - z; text('23 ноября', 990, 850, 36, INK2, 'right', 400);
    c.globalAlpha = z; text('не будет', 990, 850, 36, INK2, 'right', 400); c.globalAlpha = 1;
    counter(t, 90, 1170, 260);
    // группа 3: история списаний
    rr(40, 1320, 1000, 470, 40, CARD);
    text('История списаний', 90, 1405, 40, INK2, 'left', 400);
    [['23 октября', '−200 ₽'], ['23 сентября', '−200 ₽'], ['23 августа', '−200 ₽']].forEach(([a, b], i) => {
      const y = 1510 + i * 100; text(a, 90, y, 42, INK, 'left', 400); text(b, 990, y, 42, INK, 'right');
      if (i < 2) {c.fillStyle = '#e4e6e8'; c.fillRect(90, y + 38, 900, 2);}
    });
  }

  // ---------- чек ----------
  const RX = 150, RW = 780, RTOP = 790, PIV = 650;   // PIV — точка поворота бумаги от её верхнего края
  function paper() {   // бумага в локальных координатах: (0,0) — верхний левый угол
    const H = 1300;
    c.save(); c.shadowColor = 'rgba(0,0,0,.28)'; c.shadowBlur = 30; c.shadowOffsetY = 10;
    c.beginPath(); c.moveTo(0, 14);
    for (let i = 0; i <= 26; i++) c.lineTo(i * RW / 26, i % 2 ? 0 : 14);   // зубчатый край
    c.lineTo(RW, H); c.lineTo(0, H); c.closePath(); c.fillStyle = PAPER; c.fill(); c.restore();
    const L = 56, R = RW - 56, dash = (y: number) => {c.fillStyle = '#c9c6bd'; for (let x = L; x < R; x += 22) c.fillRect(x, y, 12, 3);};
    text('МЕДИАТЕКА+', RW / 2, 120, 46, INK, 'center', 700, MONO);
    text('кассовый чек · 23.09', RW / 2, 172, 30, INK2, 'center', 400, MONO);
    dash(220);
    text('Подписка, 1 мес.', L, 300, 34, INK, 'left', 400, MONO); text('200,00', R, 300, 34, INK, 'right', 400, MONO);
    text('ИТОГО', L, 400, 50, INK, 'left', 700, MONO); text('200,00 ₽', R, 400, 50, INK, 'right', 700, MONO);
    dash(450);
    text('Автопродление', L, 530, 32, INK2, 'left', 400, MONO); text('выкл.', R, 530, 32, INK, 'right', 700, MONO);
    text('След. платёж', L, 590, 32, INK2, 'left', 400, MONO); text('0,00 ₽', R, 590, 32, INK, 'right', 700, MONO);
    let bx = L; c.fillStyle = INK; bars.forEach((w, i) => {if (i % 2 === 0) c.fillRect(bx, 660, w, 110); bx += w + 4;});
    text('учебный пример · суммы вымышлены', RW / 2, 840, 24, INK2, 'center', 400, MONO);
  }
  const paperRot = (t: number) => -.035 + .02 * kick(t - E.receipt - .45, 9, 4);
  function receipt(t: number) {
    // ГОЛОС → ДВИЖЕНИЕ: на «чек» бумага выползает снизу толчками, как из принтера, и чуть качается
    const k = clamp((t - E.receipt) / .7), p = outCubic(k) + .012 * Math.sin(k * 60) * (1 - k);
    const y = lerp(SCR.y + SCR.h + 20, RTOP, p);
    c.save(); c.translate(RX + RW / 2, y + PIV); c.rotate(paperRot(t)); c.translate(-RW / 2, -PIV); paper(); c.restore();
  }

  // ---------- камера ----------
  type Cam = {x: number; y: number; s: number; r: number};
  const START: Cam = {x: 540, y: 960, s: 1.03, r: 0};
  const TOG = {x: 600, y: 680, s: 1.45}, AMT = {x: 430, y: 1190, s: 1.42}, PULL = {x: 540, y: 1000, s: .84};
  const mv0 = Math.min(E.cancel + .32, E.zero - .75), mv1 = mv0 + .5;
  function midCam(t: number): Cam {   // настройки: переключатель -> счётчик -> панч на «ноль»
    let x: number, y: number, sc: number;
    if (t < mv0) {   // после whip камера «доезжает» пружиной
      x = TOG.x; y = TOG.y; sc = TOG.s * (1 + .1 * (1 - spring(t - WHIP, 13, 6)));
      sc *= 1 + .025 * kick(t - E.cancel, 26, 10);   // ГОЛОС → ДВИЖЕНИЕ: щелчок переключателя чуть толкает камеру
    } else if (t < mv1) {
      const k = inout((t - mv0) / (mv1 - mv0)); x = lerp(TOG.x, AMT.x, k); y = lerp(TOG.y, AMT.y, k); sc = lerp(TOG.s, AMT.s, k);
    } else {
      const k = outCubic((t - mv1) / Math.max(.3, E.zero - mv1)); x = AMT.x; y = AMT.y; sc = lerp(AMT.s, AMT.s * 1.07, k);
    }
    // ГОЛОС → ДВИЖЕНИЕ: панч на цифру — скачок +15 % ровно в кадре E.zero и затухающее колебание
    if (t >= E.zero) sc *= 1 + .15 * Math.exp(-6 * (t - E.zero)) * Math.cos(13 * (t - E.zero));
    return {x, y, s: sc, r: 0};
  }
  function camAt(t: number): Cam {
    let q: Cam;
    if (t < WHIP) {
      const k = inout(t / WHIP); q = {x: 540, y: lerp(START.y, 1020, k), s: lerp(START.s, 1.1, k), r: 0};
      q.y += 22 * kick(t - E.cost, 40, 9); q.r += .012 * kick(t - E.cost, 33, 8);   // ГОЛОС → ДВИЖЕНИЕ: камера вздрагивает на «двести»
    } else if (t < M) {
      q = midCam(t);
      const k = inout((t - (E.receipt - .05)) / .9);   // ГОЛОС → ДВИЖЕНИЕ: отъезд камеры вместе с чеком
      if (k > 0) q = {x: lerp(q.x, PULL.x, k), y: lerp(q.y, PULL.y, k), s: lerp(q.s, PULL.s, k), r: 0};
    } else {
      const k = inout((t - M) / (LAST - M)); q = {x: lerp(PULL.x, START.x, k), y: lerp(PULL.y, START.y, k), s: lerp(PULL.s, START.s, k), r: 0};
    }
    // ручной дрейф: гармоники с периодом LAST, поэтому в последнем кадре он равен дрейфу первого
    q.x += 9 * per(t, 1, 0) + 4 * per(t, 3, 1.3); q.y += 7 * per(t, 1, 2) + 3 * per(t, 2, .5);
    q.r += .004 * per(t, 1, .7) + .002 * per(t, 4, 2.1);
    return q;
  }

  window.events = E; window.shotTimes = [0, WHIP, M];   // склейки для «вжухов»: whip и возврат к началу петли

  // ---------- субтитры по слову: обводка вместо плашки, акцент антиквой ----------
  const ACC = new Set(['продление', 'чек']);
  type Ph = {words: Word[]; start: number; end: number};
  const phrases: Ph[] = [];
  {let cur: Word[] = []; const flush = () => {if (cur.length) phrases.push({words: cur, start: cur[0].start, end: cur[cur.length - 1].end}); cur = [];};
    W.forEach((w, i) => {if (cur.length && cur[0].line !== w.line) flush(); cur.push(w); const n = W[i + 1];
      if ((/[.,:!?»]$/.test(w.text) && cur.length >= 2) || cur.length >= 5 || (n && n.start - w.end > .3)) flush();});
    flush(); phrases.forEach((p, i) => {const n = phrases[i + 1]; p.end = n ? Math.min(n.start - .02, p.end + .7) : M;});}   // к петле субтитров нет
  function captions(t: number) {
    const p = phrases.find(x => t >= x.start - .06 && t < x.end); if (!p) return;
    const fade = 1 - clamp((t - p.end + .12) / .12);
    const parts = p.words.map(w => {const n = norm(w.text), num = /^\d+$/.test(n), acc = ACC.has(n);
      const fam = acc ? ACCENT : SANS, size = num ? 88 : acc ? 76 : 66, f = `${acc ? 'italic 400' : 700} ${size}px ${fam}`; out.font = f;
      return {w, f, num, width: out.measureText(w.text).width};});
    const gap = 22, lines: (typeof parts)[] = [[]]; let lw = 0;      // перенос, если строка шире 940 px
    for (const q of parts) {if (lw + q.width > 940 && lines[lines.length - 1].length) {lines.push([]); lw = 0;} lines[lines.length - 1].push(q); lw += q.width + gap;}
    const light = t >= WHIP + .11;   // после переброски экран светлый: тёмный текст со светлым ореолом, иначе белое тонет в белом
    const ink = light ? '#15181b' : '#ffffff', numInk = light ? '#9a5200' : '#ffe2a8';
    out.save(); out.textAlign = 'left'; out.lineJoin = 'round'; out.lineWidth = 12; out.strokeStyle = light ? 'rgba(250,250,248,.95)' : 'rgba(14,16,18,.9)';
    lines.forEach((ln, li) => {const lwid = ln.reduce((a, q) => a + q.width, 0) + gap * (ln.length - 1); let x = 540 - lwid / 2; const y = 300 + li * 104;
      if (light) {   // мягкая подложка: при отъезде камеры строка ложится на шапку приложения
        const vis = ln.filter(q => t - q.w.start + .04 > 0), vw = vis.reduce((a, q) => a + q.width, 0) + gap * Math.max(0, vis.length - 1);
        if (vis.length) {out.save(); out.globalAlpha = fade * .9; out.shadowColor = 'rgba(250,250,248,1)'; out.shadowBlur = 28;
          out.fillStyle = 'rgba(250,250,248,.92)'; out.beginPath(); out.roundRect(x - 34, y - 70, vw + 68, 96, 48); out.fill(); out.restore();}}
      for (const q of ln) {const k = clamp((t - q.w.start + .04) / .14);   // слово проявляется к моменту, когда его произносят
        if (k > 0) {out.globalAlpha = fade * k; out.font = q.f; const yy = y + (1 - outCubic(k)) * 18;
          out.strokeText(q.w.text, x, yy); out.fillStyle = q.num ? numInk : ink; out.fillText(q.w.text, x, yy);}
        x += q.width + gap;}});
    out.restore();
  }

  // ---------- кадр целиком ----------
  function drawWorld(t: number) {
    c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.clearRect(0, 0, FW, FH);
    const q = qaMode ? {x: FW / 2, y: FH / 2, s: 1, r: 0} : camAt(t);
    c.translate(FW / 2, FH / 2); c.rotate(q.r); c.scale(q.s, q.s); c.translate(-q.x, -q.y);
    const g = c.createLinearGradient(0, -800, 0, FH + 800); g.addColorStop(0, '#d6d0c6'); g.addColorStop(1, '#a9a297');
    c.fillStyle = g; c.fillRect(-1200, -1200, FW + 2400, FH + 2400);                  // стол, виден только при отъезде
    c.save(); c.shadowColor = 'rgba(0,0,0,.35)'; c.shadowBlur = 60; c.shadowOffsetY = 24;
    rr(-12, -22, FW + 24, FH + 44, 128, BODY); c.restore();                            // корпус
    c.save(); screenPath(); c.clip();
    if (t < WHIP) lock(t, false, false);
    else if (t < M) {settings(t); if (t >= E.receipt) receipt(t);}
    else {   // петля: экран блокировки проявляется, чек сворачивается в верхний пуш стопки
      const k = inout((t - M) / (LAST - M));
      settings(t);
      c.globalAlpha = k; lock(t, true, true); c.globalAlpha = 1;
      if (k >= 1) notif(RECEIPT_N, NX, STACK_Y);   // ровно то же, что рисует lock() в кадре 0
      else {
        const sx = lerp(RX + RW / 2, NX + NW / 2, k), sy = lerp(RTOP + PIV, STACK_Y + NH / 2, k), ps = lerp(1, .2, k);
        c.save(); c.globalAlpha = 1 - k; c.translate(sx, sy); c.rotate(paperRot(t) * (1 - k)); c.scale(ps, ps); c.translate(-RW / 2, -PIV); paper(); c.restore();
        const ns = lerp(.7, 1, k);
        c.save(); c.globalAlpha = k * k; c.translate(sx, sy); c.scale(ns, ns); c.translate(-(NX + NW / 2), -(STACK_Y + NH / 2)); notif(RECEIPT_N, NX, STACK_Y); c.restore();
      }
    }
    c.restore();
  }
  function render(t: number) {
    drawWorld(t);
    out.setTransform(1, 0, 0, 1, 0, 0); out.globalAlpha = 1; out.fillStyle = '#000'; out.fillRect(0, 0, FW, FH);
    if (qaMode) {out.drawImage(world, 0, 0); captions(t); return;}
    const lt = t - WHIP, TW = .22;
    if (lt >= 0 && lt < TW) {   // whip: кадр въезжает справа со сдвигом 460 px, хвост заворачивается (без чёрной полосы), четыре «шлейфа»
      const k = 1 - outCubic(lt / TW);
      for (let g = 4; g >= 0; g--) {out.globalAlpha = g === 0 ? 1 : .2; const x = -k * 460 - g * k * 70; out.drawImage(world, x, 0); out.drawImage(world, x + FW, 0);}
      out.globalAlpha = 1;
    } else out.drawImage(world, 0, 0);
    const v = out.createRadialGradient(540, 960, 650, 540, 960, 1300); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.28)');
    out.fillStyle = v; out.fillRect(0, 0, FW, FH);                                   // виньетка
    const N = Math.round(LAST * FPS), fr = Math.round(t * FPS) % N;                    // зерно: последний кадр = кадр 0
    out.globalAlpha = .06; out.globalCompositeOperation = 'overlay'; out.drawImage(grain, -(fr * 37 % 200), -(fr * 91 % 300), FW + 400, FH + 600);
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1;
    captions(t);
  }
  window.setTime = async (t: number) => render(clamp(t, 0, END));
  await window.setTime(0); window.ready = true;
}
main().catch(e => {console.error(e); throw e;});
