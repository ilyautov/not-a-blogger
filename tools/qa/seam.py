#!/usr/bin/env python3
"""Стык зацикленного клипа: разница последнего и первого кадра против разниц соседних кадров.

Что делает: декодирует клип в серые кадры малого размера, считает среднюю попиксельную разницу
каждой пары соседних кадров и пары «последний → первый» (стык петли). Стык заметен, когда он
сильно больше обычного шага между кадрами. По умолчанию провал, если стык больше 2 × медианы
соседних разниц (выбрано, не откалибровано: на четырёх принятых петлях отношение было 1,0–1,7).

Вход: видео (mp4 и всё, что читает ffmpeg).
Выход: строка-сводка или JSON (--json): кадров, стык, медиана и максимум соседних, отношение.
Код возврата: 0, если отношение ≤ --max-ratio; иначе 1.

Пример:
  python3 tools/qa/seam.py bg/loop.mp4
  python3 tools/qa/seam.py bg/loop.mp4 --max-ratio 1.5 --json
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np


def read_gray(path, w=270, h=480):
    ff = os.environ.get('FFMPEG', 'ffmpeg')
    raw = subprocess.run([ff, '-v', 'error', '-i', str(path), '-vf', f'scale={w}:{h},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def seam_stats(frames):
    """frames: (n, h, w). Вернуть словарь: стык last→first, медиана и максимум соседних разниц, отношение."""
    if len(frames) < 3:
        raise ValueError('нужно хотя бы 3 кадра')
    d = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    seam = float(np.abs(frames[-1] - frames[0]).mean())
    med = float(np.median(d))
    return {'frames': int(len(frames)), 'seam': round(seam, 2), 'median': round(med, 2),
            'max': round(float(d.max()), 2), 'ratio': round(seam / max(med, 1e-6), 2)}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Проверка стыка петли: последний→первый кадр против соседних.')
    ap.add_argument('video')
    ap.add_argument('--max-ratio', type=float, default=2.0, help='порог стык / медиана соседних (2,0)')
    ap.add_argument('--json', action='store_true', help='вывод JSON')
    a = ap.parse_args(argv)
    r = seam_stats(read_gray(a.video))
    r['pass'] = r['ratio'] <= a.max_ratio
    if a.json:
        print(json.dumps({'file': os.path.basename(a.video), **r}, ensure_ascii=False))
    else:
        print(f"{os.path.basename(a.video)}: кадров {r['frames']}, стык {r['seam']}, соседние медиана {r['median']}, "
              f"макс {r['max']}, отношение {r['ratio']} → {'ok' if r['pass'] else 'ШОВ'}")
    return 0 if r['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
