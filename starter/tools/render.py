"""Покадровый рендер сцены: headless Chromium (Playwright) -> JPEG в трубу -> ffmpeg image2pipe -> output/picture.mp4.
Почему не запись экрана: браузер не обязан успевать в реальном времени. Мы сами ставим время кадра
window.setTime(i/FPS) и снимаем скриншот, поэтому тяжёлый кадр не «проседает», а рендер повторяем побайтно.

Режимы (из папки starter, под блокировкой render):
  python3 locked.py render -- $PY tools/render.py --probe          # story.json + qa/shots.json + qa/events.json (нужно звуку)
  python3 locked.py render -- $PY tools/render.py --frames 0.75    # сухой просмотр: кадр каждые 0,75 с -> qa/frames/sheet-N.jpg
  python3 locked.py render -- $PY tools/render.py                  # весь ролик -> output/picture.mp4
  python3 locked.py render -- $PY tools/render.py --from 0 --to 4  # кусок (для пробы)
Перед запуском: build/scene.js собран (tsc -p scene), voice-track.json есть (voice/trim.py или voice/fake_track.py)."""
import argparse, functools, hashlib, json, math, shutil, subprocess, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent.parent
FPS, W, H = 30, 1080, 1920


def story():
    """voice-track.json -> story.json (что читает сцена). Длительность = длина голоса, округлённая вверх до кадра."""
    v = json.loads((P / 'voice-track.json').read_text()); wav = P / v['file']
    if hashlib.sha256(wav.read_bytes()).hexdigest() != v['sha256']:
        raise SystemExit('voice-track.wav не совпадает с voice-track.json: перезапусти voice/trim.py')
    s = {'width': W, 'height': H, 'fps': FPS, 'duration': math.ceil(v['duration'] * FPS) / FPS, 'cues': v['cues'], 'words': v['words'],
         'voice_track': v['file'], 'publication_approved': False}
    (P / 'story.json').write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n'); return s


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


def font_missing(msg):
    """404 на assets/fonts/*: шрифты качает make.sh fonts, без них сцена рисует запасными (см. index.html). Не ошибка сцены."""
    url = (msg.location or {}).get('url', '') if msg.location else ''
    return '/assets/fonts/' in url or ('assets/fonts/' in msg.text and 'Failed to load resource' in msg.text)


def with_page(fn):
    """Поднять локальный HTTP-сервер на папке проекта (fetch('story.json') из file:// не работает), открыть страницу, дождаться ready."""
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(P)))
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and not font_missing(m) else None)
            pg.goto(f'http://127.0.0.1:{srv.server_port}/index.html', wait_until='load')
            try:
                pg.wait_for_function('window.ready === true', timeout=30000)
            except Exception:
                raise SystemExit(f'сцена не поднялась: {errs}')
            fn(pg); b.close()
            if errs: raise SystemExit(f'ошибки в сцене: {errs}')
    finally:
        srv.shutdown(); srv.server_close()


def probe(pg):
    (P / 'qa').mkdir(exist_ok=True)
    (P / 'qa/shots.json').write_text(json.dumps(pg.evaluate('window.shotTimes')) + '\n')
    (P / 'qa/events.json').write_text(json.dumps(pg.evaluate('window.events'), indent=1) + '\n')


def interval(frames, t0, t1, duration):
    """Проверить --frames/--from/--to до любых записей: шаг конечный и > 0, 0 ≤ from < to. Вернуть to, обрезанный по длине ролика.
    Раньше --frames 0 уходил в полный рендер поверх picture.mp4, а отрицательный шаг чистил qa/frames и снимал ноль кадров."""
    bad = lambda v: v is not None and not math.isfinite(v)
    if bad(frames) or bad(t0) or bad(t1): raise SystemExit('render: --frames/--from/--to должны быть числами (не nan/inf)')
    if frames is not None and frames <= 0: raise SystemExit(f'render: --frames {frames}: шаг в секундах должен быть больше нуля, например --frames 0.75')
    t1 = duration if t1 is None else min(t1, duration)
    if not 0 <= t0 < t1: raise SystemExit(f'render: нужен 0 ≤ --from < --to (≤ длины ролика {duration} с), получено --from {t0} --to {t1}')
    return t1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--probe', action='store_true'); ap.add_argument('--frames', type=float)
    ap.add_argument('--from', dest='t0', type=float, default=0); ap.add_argument('--to', dest='t1', type=float); a = ap.parse_args()
    interval(a.frames, a.t0, a.t1, math.inf)   # до story(): неверные флаги не трогают ни один файл
    if not (P / 'build/scene.js').exists(): raise SystemExit('нет build/scene.js: собери сцену (tsc -p scene)')
    s = story(); t1 = interval(a.frames, a.t0, a.t1, s['duration'])
    if a.probe:
        with_page(probe); print('probe ok, duration', s['duration']); return
    if a.frames is not None:
        out = P / 'qa/frames'; shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
        times = [round(a.t0 + i * a.frames, 3) for i in range(int((t1 - a.t0) / a.frames) + 1)]
        def shoot(pg):
            probe(pg)
            for i, t in enumerate(times): pg.evaluate('t=>window.setTime(t)', t); pg.screenshot(path=str(out / f'f_{i:03d}.png'))
        with_page(shoot)
        for k in range(0, len(times), 32):   # контактные листы 8×4
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-start_number', str(k), '-i', str(out / 'f_%03d.png'), '-frames:v', '1',
                            '-vf', 'scale=270:480,tile=8x4', str(out / f'sheet-{k // 32}.jpg')], check=True)
        (out / 'times.json').write_text(json.dumps(times) + '\n'); print('frames', len(times), '->', out); return
    (P / 'output').mkdir(exist_ok=True); (P / 'qa').mkdir(exist_ok=True)
    f0, f1 = round(a.t0 * FPS), round(t1 * FPS)
    log = (P / 'qa/encode.log').open('wb')
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', str(FPS), '-i', '-', '-an',
                            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                            str(P / 'output/picture.mp4')], stdin=subprocess.PIPE, stderr=log)
    def frames(pg):
        probe(pg)
        for i in range(f0, f1):
            pg.evaluate('t=>window.setTime(t)', i / FPS); enc.stdin.write(pg.screenshot(type='jpeg', quality=94))
            if (i - f0) % 120 == 0: print(f'frame {i - f0}/{f1 - f0}', flush=True)
    try:
        with_page(frames)
    finally:
        enc.stdin.close(); code = enc.wait(timeout=120); log.close()
    if code: raise SystemExit('ffmpeg упал, см. qa/encode.log')
    print('picture', P / 'output/picture.mp4', f'{(f1 - f0) / FPS:.2f}s')


if __name__ == '__main__':
    main()
