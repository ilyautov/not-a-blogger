#!/usr/bin/env python3
"""Срезает «жертвенное» слово в конце дубля TTS по энергии, без ASR.

Зачем: некоторые TTS (замечено на F5-TTS) обрывают окончание реплики: хвост генерации
не содержит тишины, звук обрывается примерно на −44 dB. Приём — дописать в конец реплики
короткое лишнее слово (например «Ага.»), синтезировать и потом отрезать его. ASR на полном
файле часто «не слышит» такое конечное междометие, поэтому режем по энергии.

Что делает: идёт от конца файла назад: концевая тишина → звучащий хвост (лишнее слово) →
пауза перед ним. Режет на входе в паузу, гасит последние --fade секунд и дописывает --pad
секунд тишины. Предохранитель: хвост должен быть длиной от --min-tail до --max-tail секунд,
иначе это не лишнее слово, а настоящая речь, и файл не трогается.

Вход: WAV-дубль. Выход: WAV без хвоста (по умолчанию <имя>.cut.wav) и строка-отчёт
(или --json). Код возврата: 0, если отрезано; 2, если файл не тронут (хвост не похож на слово).

Пример:
  python3 tools/audio/tail_trim.py voice/raw-3.wav
  python3 tools/audio/tail_trim.py voice/raw-3.wav --out voice/raw-3.wav --json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def find_gap(x, sr, silence_db=-50.0, win=0.01):
    """Вернуть время начала паузы перед последним звучащим куском (с) или None."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    w = max(1, int(win * sr))
    lvl = [20 * np.log10(max(1e-7, float(np.sqrt(np.mean(x[k:k + w] ** 2)))))
           for k in range(0, len(x) - w, w)]
    i = len(lvl) - 1
    while i > 0 and lvl[i] < silence_db:      # концевая тишина
        i -= 1
    while i > 0 and lvl[i] >= silence_db:     # само лишнее слово
        i -= 1
    gap_end = i
    while i > 0 and lvl[i] < silence_db:      # пауза перед ним
        i -= 1
    if gap_end - i < 3 or i <= 0:
        return None
    return (i + 1) * w / sr


def trim(x, sr, silence_db=-50.0, min_tail=0.25, max_tail=1.4, fade=0.05, pad=0.20):
    """Вернуть (новый_сигнал_или_None, info). None — файл трогать не надо."""
    cut = find_gap(x, sr, silence_db)
    dur = len(x) / sr
    tail = round(dur - cut, 3) if cut is not None else None
    info = {'duration': round(dur, 3), 'cut_at': cut and round(cut, 3), 'tail': tail}
    if cut is None or not (min_tail <= tail <= max_tail):
        info['trimmed'] = False
        return None, info
    y = np.array(x[:int(cut * sr)], dtype=np.float64)
    k = min(len(y), int(fade * sr))
    if k:
        ramp = np.linspace(1.0, 0.0, k)
        y[-k:] = y[-k:] * (ramp[:, None] if y.ndim > 1 else ramp)
    silence = np.zeros((int(sr * pad),) + y.shape[1:])
    info['trimmed'] = True
    return np.concatenate([y, silence]), info


def main(argv=None):
    ap = argparse.ArgumentParser(description='Срезать лишнее слово в конце дубля по энергии.')
    ap.add_argument('wav')
    ap.add_argument('--out', help='куда писать (по умолчанию <имя>.cut.wav)')
    ap.add_argument('--silence-db', type=float, default=-50.0, help='порог тишины, dBFS (−50)')
    ap.add_argument('--min-tail', type=float, default=0.25, help='минимальная длина хвоста, с')
    ap.add_argument('--max-tail', type=float, default=1.4, help='максимальная длина хвоста, с')
    ap.add_argument('--fade', type=float, default=0.05, help='гашение перед резом, с')
    ap.add_argument('--pad', type=float, default=0.20, help='тишина после реза, с')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    x, sr = sf.read(a.wav)
    y, info = trim(x, sr, a.silence_db, a.min_tail, a.max_tail, a.fade, a.pad)
    src = Path(a.wav)
    info['file'] = src.name
    if y is not None:
        out = Path(a.out) if a.out else src.with_name(src.stem + '.cut.wav')
        sf.write(out, y, sr, subtype='PCM_16')
        info['out'] = str(out)
    if a.json:
        print(json.dumps(info, ensure_ascii=False))
    elif info['trimmed']:
        print(f"{src.name}: хвост {info['tail']:.2f} с отрезан, речь {info['cut_at']:.2f} с → {info['out']}")
    else:
        print(f"{src.name}: хвост {info['tail']} — не похоже на лишнее слово, не трогаю")
    return 0 if info['trimmed'] else 2


if __name__ == '__main__':
    sys.exit(main())
