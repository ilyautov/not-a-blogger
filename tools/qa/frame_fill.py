#!/usr/bin/env python3
"""Заполнение кадра по готовому видео: сколько экрана реально занято содержимым.

Зачем: проверки по DOM или по сцене врут (элемент есть, но прозрачный, за краем, мелкий).
Эта метрика смотрит на пиксели готового mp4, то есть на то, что увидит зритель.

Два режима:
  fill  доля пикселей, отличающихся от фона больше порога (фон = медиана кадра);
        плюс пустые отрезки: подряд идущие кадры с заполнением ниже --empty дольше --min-run.
  grid  занятость сетки --cols × --rows: доля клеток, где есть «чернила». Меряет разброс
        содержимого по кадру, а не толщину штрихов.
Полоса субтитров внизу (--subs-band, доля высоты) не учитывается.
Значения по умолчанию — единственное определение пустого кадра в наборе: docs/QA-THRESHOLDS.md в корне.

Вход: видеофайл. Выход: сводка в stdout, полный отчёт в --json (медиана, p10, p90, серия
по времени, пустые отрезки). Код возврата: 0; 1, если медиана ниже --fail-below или (в
режиме fill) найден пустой отрезок, а задан --fail-on-empty.

Пример:
  python3 tools/qa/frame_fill.py output/final.mp4 --json qa/frame-fill.json
  python3 tools/qa/frame_fill.py output/final.mp4 --mode grid --fail-below 30
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or shutil.which('ffprobe') or 'ffprobe'


def probe(path):
    """Вернуть (ширина, высота, длительность_с)."""
    r = subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height:format=duration', '-of', 'json', path],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = d['streams'][0]
    return int(s['width']), int(s['height']), float(d['format']['duration'])


def sample_frames(path, step, long_side):
    """Кадры раз в step секунд, серые, длинная сторона = long_side. Возвращает (кадры, длительность)."""
    w, h, dur = probe(path)
    k = long_side / max(w, h)
    sw, sh = max(2, int(w * k) // 2 * 2), max(2, int(h * k) // 2 * 2)
    raw = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-vf', f'fps=1/{step},scale={sw}:{sh},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, sh, sw).astype(np.int16)
    return frames, dur


def fill_value(frame, thresh):
    return float((np.abs(frame - np.median(frame)) > thresh).mean() * 100)


def grid_value(frame, thresh, cols, rows, cell_min):
    ink = np.abs(frame - np.median(frame)) > thresh
    ch, cw = ink.shape[0] // rows, ink.shape[1] // cols
    occ = sum(1 for r in range(rows) for c in range(cols)
              if ink[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].mean() > cell_min)
    return occ / (cols * rows) * 100


def empty_runs(series, dur, empty, min_run):
    runs, cur = [], None
    for t, v in series:
        if v < empty:
            cur = t if cur is None else cur
        elif cur is not None:
            if t - cur >= min_run:
                runs.append((cur, round(t - cur, 1)))
            cur = None
    if cur is not None and dur - cur >= min_run:
        runs.append((cur, round(dur - cur, 1)))
    return runs


def analyse(path, mode='fill', step=2.0, subs_band=0.14, thresh=None, empty=4.0, min_run=6.0,
            cols=16, rows=8, cell_min=0.012):
    long_side = 240 if mode == 'fill' else 480
    thresh = thresh if thresh is not None else (26 if mode == 'fill' else 24)
    frames, dur = sample_frames(path, step, long_side)
    cut = int(frames.shape[1] * (1 - subs_band))
    series = []
    for i, f in enumerate(frames):
        f = f[:cut]
        v = fill_value(f, thresh) if mode == 'fill' else grid_value(f, thresh, cols, rows, cell_min)
        series.append((round(i * step, 1), round(v, 2)))
    vals = np.array([v for _, v in series]) if series else np.zeros(1)
    out = {'file': os.path.basename(path), 'mode': mode, 'duration': round(dur, 2), 'samples': len(series),
           'median': round(float(np.median(vals)), 2), 'p10': round(float(np.percentile(vals, 10)), 2),
           'p90': round(float(np.percentile(vals, 90)), 2), 'series': series}
    if mode == 'fill':
        out['below_empty_pct'] = round(float((vals < empty).mean() * 100), 1)
        out['empty_runs'] = empty_runs(series, dur, empty, min_run)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Заполнение кадра по готовому видео.')
    ap.add_argument('video')
    ap.add_argument('--mode', choices=['fill', 'grid'], default='fill')
    ap.add_argument('--step', type=float, default=2.0, help='шаг выборки кадров, с (2)')
    ap.add_argument('--subs-band', type=float, default=0.14, help='доля высоты снизу, которую не считать (0,14)')
    ap.add_argument('--thresh', type=float, help='порог отличия от фона 0..255 (fill 26, grid 24)')
    ap.add_argument('--empty', type=float, default=4.0, help='fill: ниже этого %% кадр пустой (4)')
    ap.add_argument('--min-run', type=float, default=6.0, help='fill: минимальный пустой отрезок, с (6)')
    ap.add_argument('--cols', type=int, default=16)
    ap.add_argument('--rows', type=int, default=8)
    ap.add_argument('--cell-min', type=float, default=0.012, help='grid: доля пикселей клетки, чтобы считать её занятой')
    ap.add_argument('--json', help='куда записать полный отчёт')
    ap.add_argument('--fail-below', type=float, help='код 1, если медиана ниже, %%')
    ap.add_argument('--fail-on-empty', action='store_true', help='fill: код 1 при пустом отрезке')
    a = ap.parse_args(argv)
    try:
        out = analyse(a.video, a.mode, a.step, a.subs_band, a.thresh, a.empty, a.min_run, a.cols, a.rows, a.cell_min)
    except FileNotFoundError as e:
        if e.filename not in (FFMPEG, FFPROBE):
            raise
        print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
        return 2
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{a.mode}: медиана {out['median']}%  p10 {out['p10']}%  p90 {out['p90']}%")
    bad = a.fail_below is not None and out['median'] < a.fail_below
    if a.mode == 'fill':
        runs = out['empty_runs']
        print(f"ниже {a.empty}%: {out['below_empty_pct']}% хронометража; пустых отрезков ≥{a.min_run} с: {len(runs)}")
        for t, d in runs[:20]:
            print(f'  {int(t) // 60}:{int(t) % 60:02d}  {d} с')
        bad = bad or (a.fail_on_empty and bool(runs))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
