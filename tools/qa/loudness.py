#!/usr/bin/env python3
"""Громкость и true peak готового файла против порогов docs/QA-THRESHOLDS.md.

Что меряет: integrated LUFS, true peak (dBTP) и LRA через ffmpeg ebur128=peak=true, тем же способом,
каким меряются пороги в docs/QA-THRESHOLDS.md. Мерить закодированный mp4, а не мастер: AAC поднимает пики
на 1–2 дБ.
  --target final (по умолчанию): финал −15 LUFS ±1 (окно −16…−14), TP ≤ −1,5 dBTP;
  --target take: отдельный дубль голоса до сведения, −16 LUFS ±1, TP ≤ −2 dBTP.
--lufs, --tolerance и --tp-max переопределяют значения цели; не меняй их в рецептах, меняй таблицу.

Вход: аудио или видео (всё, что читает ffmpeg). Несколько файлов — по строке JSON на файл.
Выход: JSON в stdout: file, target, integrated, true_peak, lra, window, tp_max, checks, pass.
Код возврата: 0, если все файлы прошли; 1, если хоть один нет; 2, если ffmpeg не смог измерить.

Пример:
  python3 tools/qa/loudness.py output/final.mp4
  python3 tools/qa/loudness.py --target take voice/norm/*.wav
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

TARGETS = {'final': {'lufs': -15.0, 'tolerance': 1.0, 'tp_max': -1.5},
           'take': {'lufs': -16.0, 'tolerance': 1.0, 'tp_max': -2.0}}


def measure(path):
    """(integrated LUFS, true peak dBTP, LRA LU) через ffmpeg ebur128; −inf для тишины."""
    ff = os.environ.get('FFMPEG', 'ffmpeg')
    err = subprocess.run([ff, '-nostats', '-hide_banner', '-i', str(path), '-map', '0:a:0',
                          '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    if 'Summary:' not in err:
        raise RuntimeError(f'ffmpeg ebur128 не дал сводку для {path}: {err.strip()[-300:]}')
    s = err[err.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+|-inf)', s).group(1))
    return g('I'), g('Peak'), g('LRA')


def _num(x):
    return None if x is None or math.isinf(x) else round(x, 2)


def evaluate(integrated, true_peak, lra=None, target='final', lufs=None, tolerance=None, tp_max=None):
    t = dict(TARGETS[target])
    for k, v in (('lufs', lufs), ('tolerance', tolerance), ('tp_max', tp_max)):
        if v is not None:
            t[k] = v
    lo, hi = t['lufs'] - t['tolerance'], t['lufs'] + t['tolerance']
    checks = {'integrated': [_num(integrated), lo <= integrated <= hi],
              'true_peak': [_num(true_peak), true_peak <= t['tp_max']]}
    return {'target': target, 'integrated': _num(integrated), 'true_peak': _num(true_peak), 'lra': _num(lra),
            'window': [lo, hi], 'tp_max': t['tp_max'], 'checks': checks,
            'pass': all(ok for _, ok in checks.values())}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Integrated LUFS и true peak файла против порогов docs/QA-THRESHOLDS.md.')
    ap.add_argument('files', nargs='+', help='mp4, wav и всё, что читает ffmpeg')
    ap.add_argument('--target', choices=sorted(TARGETS), default='final',
                    help='final: −15±1 LUFS, TP ≤ −1,5; take: дубль голоса −16±1 LUFS, TP ≤ −2')
    ap.add_argument('--lufs', type=float, help='центр окна, LUFS (переопределяет цель)')
    ap.add_argument('--tolerance', type=float, help='полуширина окна, LU')
    ap.add_argument('--tp-max', type=float, help='потолок true peak, dBTP')
    a = ap.parse_args(argv)
    code = 0
    for f in a.files:
        try:
            i, tp, lra = measure(f)
        except (RuntimeError, AttributeError) as e:
            print(json.dumps({'file': Path(f).name, 'error': str(e), 'pass': False}, ensure_ascii=False))
            code = 2
            continue
        r = evaluate(i, tp, lra, a.target, a.lufs, a.tolerance, a.tp_max)
        print(json.dumps({'file': Path(f).name, **r}, ensure_ascii=False))
        if not r['pass'] and code == 0:
            code = 1
    return code


if __name__ == '__main__':
    sys.exit(main())
