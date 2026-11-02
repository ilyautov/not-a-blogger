#!/usr/bin/env python3
"""Линт мёртвого времени: сколько секунд подряд в кадре ничего не меняется.

Зачем: статический линт (motion_lint.py) видит механику, но не видит, что сцена длиной
20 секунд живёт только первые полторы. Этот линт смотрит на реальные кадры.

Контракт сцены (как в starter/): папка проекта с index.html, который выставляет
  window.ready = true, window.setTime(t) (может вернуть Promise) и, по желанию,
  window.setQAMode(enabled) — выключает камеру и подвижные постэффекты, но не предметы;
  window.shotTimes = [время начала каждой сцены, ...];
плюс story.json с полями duration, width, height. Страница открывается через локальный
HTTP-сервер (fetch из file:// не работает) в headless Chromium (Playwright).

Что делает: внутри каждой сцены берёт кадры с шагом --step (первые и последние 0,5 с сцены не
судит: это законный вход и выход), сравнивает соседние уменьшенные кадры. Средняя разница
яркости ниже --threshold = кадр стоит. Самый длинный застой сцены сравнивается с --max-still.
Общий наезд камеры маскирует мёртвый кадр: линт вызывает setQAMode(true), если он есть,
иначе сбрасывает transform у DOM-камеры #world. Метод записывается в camera_control;
без этих контрактов выключение камеры не подтверждено (выключить: --keep-camera). Для своей камеры можно
передать JS, который выполняется после setTime: --pre-js "window.cam&&window.cam.reset()".

Вход: папка проекта. Выход: <проект>/qa/still-lint.json и при нарушениях контактный лист
худших сцен <проект>/qa/still/contact.jpg; сводка в stdout.
Код возврата: 0, если застоев длиннее --max-still нет, иначе 1.
Порог 3 с и на чём он мерился: docs/QA-THRESHOLDS.md в корне.

Пример:
  python3 tools/lint/still_lint.py starter --step 0.5 --max-still 3
"""
import argparse
import functools
import io
import json
import math
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
from PIL import Image

HEAD = 0.5   # начало сцены — законный вход, не судим
TAIL = 0.5

RESET_CAMERA = ("(()=>{const w=document.querySelector('#world');"
                "if(w){w.dataset.tr=w.style.transform;w.style.transform='none'}})()")
RESTORE_CAMERA = ("(()=>{const w=document.querySelector('#world');"
                  "if(w&&w.dataset.tr!==undefined)w.style.transform=w.dataset.tr})()")


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def scene_spans(shot_times, duration):
    """Границы сцен [(начало, конец)] из времён склеек; без склеек — одна сцена на весь ролик."""
    cuts = sorted(t for t in (shot_times or []) if 0 <= t < duration)
    if not cuts or cuts[0] > 0:
        cuts = [0.0] + cuts
    return [(cuts[i], cuts[i + 1] if i + 1 < len(cuts) else duration) for i in range(len(cuts))]


def sample_times(spans, step):
    validate_number('step', step, positive=True)
    times, index = [], []
    for i, (a, b) in enumerate(spans):
        t, n0 = a + HEAD, len(times)
        while t <= b - TAIL + 1e-9:
            times.append(round(t, 3)); index.append(i); t += step
        if len(times) == n0:                       # очень короткая сцена
            times.append(round((a + b) / 2, 3)); index.append(i)
    return times, index


def longest_still(greys, times, step, threshold):
    """Вернуть (самый длинный застой, с; время его конца)."""
    run, longest, at = 0.0, 0.0, times[0] if times else 0.0
    for n in range(1, len(greys)):
        d = float(np.abs(greys[n] - greys[n - 1]).mean())
        if d < threshold:
            run += step
            if run > longest:
                longest, at = run, times[n]
        else:
            run = 0.0
    return round(longest, 2), at


def validate_number(name, value, positive=False):
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        bound = '> 0' if positive else '>= 0'
        raise ValueError(f'{name} must be finite and {bound}')


def shoot(project, times, width, height, keep_camera=False, pre_js=None):
    """Снять кадры. Возвращает (jpeg-байты, shotTimes, применённое управление камерой)."""
    from playwright.sync_api import sync_playwright
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(_Quiet, directory=str(project)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    frames, errs = [], []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            pg = b.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(f'http://127.0.0.1:{srv.server_port}/index.html', wait_until='load')
            try:
                pg.wait_for_function('window.ready === true', timeout=30000)
            except Exception:
                raise SystemExit(f'сцена не поднялась (нет window.ready): {errs}')
            shots = pg.evaluate('Array.isArray(window.shotTimes) ? window.shotTimes : []')
            control = {'method': 'kept', 'pre_js': bool(pre_js)}
            if not keep_camera:
                # Await optional asynchronous hooks before the first sampled render.
                method = pg.evaluate('''async () => {
                    if (typeof window.setQAMode === 'function') {
                        await window.setQAMode(true); return 'setQAMode';
                    }
                    return document.querySelector('#world') ? 'dom-world' : 'unsupported';
                }''')
                control['method'] = method
                if method == 'unsupported':
                    control['warning'] = ('Camera removal is unverified: no setQAMode hook or #world DOM camera. '
                                          'Use --pre-js for a custom camera; its effect requires your review.')
            for t in times:
                pg.evaluate('t => Promise.resolve(window.setTime(t)).then(() => 0)', t)
                if pre_js:
                    pg.evaluate(pre_js)
                if control['method'] == 'dom-world':
                    pg.evaluate(RESET_CAMERA)
                pg.evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                frames.append(pg.screenshot(type='jpeg', quality=70))
                if control['method'] == 'dom-world':
                    pg.evaluate(RESTORE_CAMERA)
            b.close()
    finally:
        srv.shutdown(); srv.server_close()
    if errs:
        raise SystemExit(f'ошибки в сцене: {errs}')
    return frames, shots, control


def grey(buf):
    im = Image.open(io.BytesIO(buf)).convert('L')
    k = 320 / max(im.size)
    return np.asarray(im.resize((max(1, int(im.width * k)), max(1, int(im.height * k)))), dtype=np.float32)


def run(project, step=0.5, max_still=3.0, threshold=0.35, keep_camera=False, pre_js=None, shot_times=None):
    # Public API callers get the same checks as CLI users, before file/browser work.
    validate_number('step', step, positive=True)
    validate_number('max_still', max_still)
    validate_number('threshold', threshold)
    project = Path(project).resolve()
    story = json.loads((project / 'story.json').read_text())
    duration = float(story['duration'])
    width, height = int(story.get('width', 1080)), int(story.get('height', 1920))
    if shot_times is None:      # сначала узнать склейки у страницы
        _, shot_times, _ = shoot(project, [], width, height, keep_camera, pre_js)
    spans = scene_spans(shot_times, duration)
    times, index = sample_times(spans, step)
    frames, _, control = shoot(project, times, width, height, keep_camera, pre_js)
    greys = [grey(f) for f in frames]
    rows, worst = [], {}
    for i, (a, b) in enumerate(spans):
        ks = [k for k in range(len(index)) if index[k] == i]
        if len(ks) < 2:
            rows.append({'scene': i, 'start': round(a, 2), 'dur': round(b - a, 2), 'still': 0.0,
                         'samples': len(ks), 'verdict': 'ok'})
            continue
        still, at = longest_still([greys[k] for k in ks], [times[k] for k in ks], step, threshold)
        verdict = 'ok' if still <= max_still else ('замерла' if still >= (b - a) * .7 else 'застой')
        worst[i] = min(ks, key=lambda k: abs(times[k] - at))
        rows.append({'scene': i, 'start': round(a, 2), 'dur': round(b - a, 2), 'still': still, 'at': round(at, 2),
                     'samples': len(ks), 'verdict': verdict})
    bad = [r for r in rows if r['verdict'] != 'ok']
    qa = project / 'qa'; qa.mkdir(exist_ok=True)
    result = {'scenes': len(rows), 'bad': len(bad), 'step': step, 'max_still': max_still,
              'threshold': threshold, 'camera_control': control, 'rows': rows}
    (qa / 'still-lint.json').write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    if bad:
        (qa / 'still').mkdir(exist_ok=True)
        top = sorted(bad, key=lambda r: -r['still'])[:12]
        tw = 360; th = int(tw * height / width)
        sheet = Image.new('RGB', (tw * 3, th * math.ceil(len(top) / 3)), '#f3f5f0')
        for n, r in enumerate(top):
            im = Image.open(io.BytesIO(frames[worst[r['scene']]])).convert('RGB').resize((tw, th))
            sheet.paste(im, ((n % 3) * tw, (n // 3) * th))
        sheet.save(qa / 'still' / 'contact.jpg', quality=88)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description='Линт мёртвого времени по реальным кадрам сцены.')
    ap.add_argument('project', type=Path, help='папка с index.html и story.json')
    ap.add_argument('--step', type=float, default=0.5, help='шаг проб внутри сцены, с (0,5)')
    ap.add_argument('--max-still', type=float, default=3.0, help='допустимый застой, с (3)')
    ap.add_argument('--threshold', type=float, default=0.35,
                    help='средняя разница яркости 0..255 на превью 320 px, ниже которой кадр стоит (0,35)')
    ap.add_argument('--keep-camera', action='store_true', help='не включать QA mode и не сбрасывать DOM-камеру #world')
    ap.add_argument('--pre-js', help='JS, выполняемый после каждого setTime (например, выключить камеру)')
    a = ap.parse_args(argv)
    try:
        validate_number('step', a.step, positive=True)
        validate_number('max_still', a.max_still)
        validate_number('threshold', a.threshold)
    except ValueError as e:
        ap.error(str(e))
    r = run(a.project, a.step, a.max_still, a.threshold, a.keep_camera, a.pre_js)
    print(f"camera_control: {r['camera_control']['method']}; pre_js: {r['camera_control']['pre_js']}")
    if r['camera_control'].get('warning'):
        print(r['camera_control']['warning'], file=sys.stderr)
    tot = sum(x['still'] for x in r['rows'])
    print(f"сцен {r['scenes']}, с застоем длиннее {a.max_still} с — {r['bad']}, мёртвого времени всего {tot:.1f} с")
    for x in sorted((x for x in r['rows'] if x['verdict'] != 'ok'), key=lambda x: -x['still'])[:20]:
        print(f"  сцена {x['scene']:>3} с {x['start']:.1f} с, длина {x['dur']} с — {x['verdict']}, застой {x['still']} с")
    return 1 if r['bad'] else 0


if __name__ == '__main__':
    sys.exit(main())
