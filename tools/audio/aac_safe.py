#!/usr/bin/env python3
"""Защита от пиков после AAC-кодирования.

Зачем: на живом голосе AAC даёт выброс до +2 dB над мастером (взрывные «б», «п»), и true peak
в готовом mp4 уходит почти к 0 dBFS, хотя мастер был сведён с запасом.

Что делает: несколько проходов «закодировать → декодировать → найти отсчёты выше потолка».
Вокруг каждого превышения (±25 мс, края по окну Ханна) мастер локально приглушается ровно на
величину превышения. Обычно хватает 1–3 проходов. По желанию сразу муксит видео с новым звуком.

Проверочный проход кодирует звук так же, как итоговый мукс: тот же кодек, битрейт и частота.
С --out-video итог всегда 48 кГц, поэтому мастер с другой частотой сначала пересчитывается в 48 кГц,
оптимизируется уже на ней, и --out тоже пишется в 48 кГц. После мукса звуковая дорожка готового
mp4 декодируется и меряется ещё раз: решение «ok» принимается по готовому файлу, а не по проверочному проходу.

Вход: мастер WAV (--in), опционально видео без звука или со звуком (--video).
Выход: исправленный WAV (--out), опционально mp4 (--out-video). Отчёт по проходам в stdout
(или --json, поле final — замер готового mp4). Код возврата: 0, если после последнего прохода
(а с --out-video — в готовом mp4) пиков выше потолка нет; иначе 1.

Пример:
  python3 tools/audio/aac_safe.py --in assets/audio/master.wav --out assets/audio/master-aac.wav
  python3 tools/audio/aac_safe.py --in mix.wav --out mix-aac.wav --video output/picture.mp4 \\
      --out-video output/final.mp4 --ceiling -3.2
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
VIDEO_SR = 48000          # частота звука в итоговом mp4 (см. мукс в main)


def _ff(*args):
    subprocess.run([FFMPEG, '-v', 'error', '-y', *map(str, args)], check=True)


def aac_roundtrip(x, sr, bitrate='256k'):
    """Закодировать в AAC и декодировать обратно. Возвращает массив (n, ch)."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sf.write(td / 'm.wav', x, sr, subtype='PCM_24')
        _ff('-i', td / 'm.wav', '-c:a', 'aac', '-b:a', bitrate, '-ar', sr, td / 'm.m4a')
        _ff('-i', td / 'm.m4a', td / 'd.wav')
        d, _ = sf.read(td / 'd.wav', always_2d=True)
    return d


def resample(x, sr, to_sr):
    """Пересчитать частоту через ffmpeg (float, без клиппинга межотсчётных пиков). Возвращает (n, ch)."""
    if sr == to_sr:
        return x
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        sf.write(td / 'i.wav', x, sr, subtype='FLOAT')
        _ff('-i', td / 'i.wav', '-ar', to_sr, '-c:a', 'pcm_f32le', td / 'o.wav')
        d, _ = sf.read(td / 'o.wav', always_2d=True)
    return d


def measure_track(path, ceiling_db):
    """Декодировать звук готового файла и померить: пик, число отсчётов выше потолка, частота."""
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'd.wav'
        _ff('-i', path, '-map', '0:a:0', '-c:a', 'pcm_f32le', wav)
        d, sr = sf.read(wav, always_2d=True)
    a = np.abs(d).max(axis=1) if len(d) else np.zeros(1)
    lim = 10 ** (ceiling_db / 20)
    return {'peak_dbfs': round(float(20 * np.log10(a.max() + 1e-12)), 2), 'over': int((a > lim).sum()), 'sr': int(sr)}


def make_safe(x, sr, ceiling_db=-3.2, passes=4, bitrate='256k', window=0.025, log=None):
    """Вернуть (исправленный_сигнал (n, ch), отчёт по проходам)."""
    x = np.array(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    lim = 10 ** (ceiling_db / 20)
    w = int(window * sr)
    report = []
    for it in range(passes + 1):
        d = aac_roundtrip(x, sr, bitrate)
        n = min(len(d), len(x))
        a = np.abs(d[:n]).max(axis=1)
        over = np.where(a > lim)[0]
        row = {'pass': it, 'peak_dbfs': round(float(20 * np.log10(a.max() + 1e-12)), 2), 'over': int(len(over))}
        report.append(row)
        if log:
            log(f"проход {it}: пик {row['peak_dbfs']} dBFS, отсчётов выше {ceiling_db}: {row['over']}")
        if not len(over) or it == passes:
            break
        g = np.ones(len(x))
        for k in over:
            dip = lim / a[k] * 0.97
            lo, hi = max(0, k - w), min(len(x), k + w)
            win = 1 - (1 - dip) * np.hanning(hi - lo)
            g[lo:hi] = np.minimum(g[lo:hi], win)
        x *= g[:, None]
    return x, report


def main(argv=None):
    ap = argparse.ArgumentParser(description='Убрать пики, которые появляются после AAC.')
    ap.add_argument('--in', dest='src', required=True, help='мастер WAV')
    ap.add_argument('--out', required=True, help='исправленный WAV')
    ap.add_argument('--ceiling', type=float, default=-3.2, help='потолок после AAC, dBFS (−3,2)')
    ap.add_argument('--passes', type=int, default=4)
    ap.add_argument('--bitrate', default='256k')
    ap.add_argument('--video', help='видео для мукса')
    ap.add_argument('--out-video', help='куда писать mp4 (нужен --video)')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if bool(a.video) != bool(a.out_video):
        ap.error('--video и --out-video задаются вместе')
    x, sr = sf.read(a.src, always_2d=True)
    log = None if a.json else print
    final = None
    try:
        if a.out_video and sr != VIDEO_SR:
            # итоговый мукс пишет 48 кГц: проверять и править надо ту же частоту, иначе отчёт о другом звуке
            if log:
                log(f'частота {sr} → {VIDEO_SR} Гц, как в итоговом mp4')
            x, sr = resample(x, sr, VIDEO_SR), VIDEO_SR
        y, rep = make_safe(x, sr, a.ceiling, a.passes, a.bitrate, log=log)
        sf.write(a.out, y, sr, subtype='PCM_24')
        if a.out_video:
            _ff('-i', a.video, '-i', a.out, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac',
                '-b:a', a.bitrate, '-ar', VIDEO_SR, '-shortest', '-movflags', '+faststart', a.out_video)
            final = measure_track(a.out_video, a.ceiling)
            if log:
                log(f"готовый mp4: пик {final['peak_dbfs']} dBFS, отсчётов выше {a.ceiling}: {final['over']}")
    except FileNotFoundError as e:
        if e.filename != FFMPEG:
            raise
        print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
        return 2
    ok = rep[-1]['over'] == 0 and (final is None or final['over'] == 0)
    if a.json:
        print(json.dumps({'ok': ok, 'ceiling': a.ceiling, 'sr': sr, 'passes': rep, 'final': final, 'out': a.out,
                          'out_video': a.out_video}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
