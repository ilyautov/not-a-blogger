#!/usr/bin/env python3
"""Паузы в голосовой дорожке по энергии.

Что делает: режет звук на окна по 10 мс, считает уровень каждого окна в dB и печатает
отрезки, где уровень ниже (пик − порог) дольше заданного минимума. Окно тише абсолютного
пола (--floor, −70 dBFS) — тишина всегда: так полностью тихая дорожка даёт одну паузу на всю
длительность, а не «пауз нет». Удобно, чтобы найти слишком длинные паузы в склейке дублей
или «дыры» после подрезки.

Вход: WAV/FLAC (любой формат, который читает soundfile), моно или стерео.
Выход: список пауз [начало_с, длительность_с] в stdout (текстом или --json).
Код возврата: 0; с --max-gap X код 1, если есть пауза длиннее X секунд; 2 — пустой файл
(нет ни одного окна, мерить нечего).

Пример:
  python3 tools/audio/gaps.py voice-track.wav
  python3 tools/audio/gaps.py voice-track.wav --min-gap 0.25 --max-gap 0.8 --json
"""
import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf


def find_gaps(x, sr, below_peak_db=40.0, min_gap=0.15, win=0.01, floor_db=-70.0):
    """Вернуть список (start_s, dur_s) тишин длиннее min_gap. x — моно или (n, ch).
    Тишина: окно ниже (пик − below_peak_db) или ниже абсолютного floor_db."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    hop = max(1, int(win * sr))
    n = (len(x) - hop) // hop + 1 if len(x) >= hop else 0
    if n <= 0:
        return []
    frames = x[:n * hop].reshape(n, hop)
    db = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-9)
    quiet = (db < db.max() - below_peak_db) | (db < floor_db)
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * win > min_gap:
                out.append((round(i * win, 2), round((j - i) * win, 2)))
            i = j
        else:
            i += 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Паузы в голосе по энергии.')
    ap.add_argument('wav')
    ap.add_argument('--db', type=float, default=40.0, help='насколько ниже пика считать тишиной, dB (40)')
    ap.add_argument('--min-gap', type=float, default=0.15, help='минимальная пауза, с (0,15)')
    ap.add_argument('--max-gap', type=float, help='код 1, если есть пауза длиннее, с')
    ap.add_argument('--floor', type=float, default=-70.0, help='тише этого всегда тишина, dBFS (−70)')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    x, sr = sf.read(a.wav)
    if len(x) < max(1, int(0.01 * sr)):
        print(f'{os.path.basename(a.wav)}: пустой или короче 10 мс, мерить нечего', file=sys.stderr)
        return 2
    gaps = find_gaps(x, sr, a.db, a.min_gap, floor_db=a.floor)
    if a.json:
        print(json.dumps({'file': os.path.basename(a.wav), 'gaps': gaps}, ensure_ascii=False))
    else:
        for t, d in gaps:
            print(f'{t:8.2f} с  пауза {d:.2f} с')
        print(f'пауз: {len(gaps)}')
    return 1 if a.max_gap is not None and any(d > a.max_gap for _, d in gaps) else 0


if __name__ == '__main__':
    sys.exit(main())
