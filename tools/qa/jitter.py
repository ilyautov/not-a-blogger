#!/usr/bin/env python3
"""Метрика дёрганья видео: насколько неровно меняются кадры.

Что делает: для каждой пары соседних кадров считает среднюю разницу яркости d_i
(кадр уменьшен до --width по ширине). «Рывок» — отклонение d_i от среднего соседей
|d_i − (d_{i−1} + d_{i+1}) / 2|. Плавное движение даёт маленький рывок, пропущенные или
задвоенные кадры и несглаженная анимация — большой. Склейки (d > 6 × медианы) исключаются.
Главная цифра — jerk_ratio = средний рывок / средняя разница: не зависит от того,
насколько много движется в кадре.

Вход: один или несколько видеофайлов (любое разрешение и ориентация).
Выход: по JSON-строке на файл: frames, diff_mean, diff_p95, jerk_mean, jerk_p95, jerk_ratio.
Код возврата: 0; 1, если задан --max-ratio и хоть у одного файла jerk_ratio выше.

Пример:
  python3 tools/qa/jitter.py output/final.mp4
  python3 tools/qa/jitter.py a.mp4 b.mp4 --max-ratio 0.5
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


def read_gray(path, width=216):
    r = subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                        '-of', 'csv=p=0', path], capture_output=True, text=True, check=True)
    w, h = (int(v) for v in r.stdout.strip().split(',')[:2])
    sw = max(2, width // 2 * 2)
    sh = max(2, int(round(h * sw / w / 2)) * 2)
    raw = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-vf', f'scale={sw}:{sh},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, sh, sw).astype(np.float32)


def jitter(frames):
    d = np.abs(np.diff(frames, axis=0)).mean((1, 2))
    if len(d) < 3:
        raise ValueError('слишком мало кадров для метрики (нужно ≥ 4)')
    med = np.median(d)
    cut = d > 6 * med if med > 0 else np.zeros_like(d, bool)
    j = np.abs(d[1:-1] - .5 * (d[:-2] + d[2:]))
    ok = ~(cut[1:-1] | cut[:-2] | cut[2:])
    j, dd = j[ok], d[~cut]
    if not len(j) or not len(dd) or dd.mean() == 0:
        return {'frames': len(frames), 'diff_mean': 0.0, 'diff_p95': 0.0, 'jerk_mean': 0.0, 'jerk_p95': 0.0, 'jerk_ratio': 0.0}
    return {'frames': len(frames), 'diff_mean': round(float(dd.mean()), 3), 'diff_p95': round(float(np.percentile(dd, 95)), 3),
            'jerk_mean': round(float(j.mean()), 3), 'jerk_p95': round(float(np.percentile(j, 95)), 3),
            'jerk_ratio': round(float(j.mean() / dd.mean()), 3)}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Метрика дёрганья видео.')
    ap.add_argument('videos', nargs='+')
    ap.add_argument('--width', type=int, default=216, help='ширина анализа, px (216)')
    ap.add_argument('--max-ratio', type=float, help='код 1, если jerk_ratio выше')
    a = ap.parse_args(argv)
    bad = False
    for p in a.videos:
        try:
            r = {'file': os.path.basename(p), **jitter(read_gray(p, a.width))}
        except FileNotFoundError as e:
            if e.filename not in (FFMPEG, FFPROBE):
                raise
            print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
            return 2
        print(json.dumps(r, ensure_ascii=False))
        bad = bad or (a.max_ratio is not None and r['jerk_ratio'] > a.max_ratio)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
