#!/usr/bin/env python3
"""Голосовой гейт перед показом: сплющенное сведение, метроном пауз, скомканный темп, фальцет.

Что меряет:
  • на готовом файле (mp4 или wav, ffmpeg ebur128): true peak и LRA. TP ниже −2,5 dBTP при нормальной
    громкости = пики придавлены лимитером или софт-клипом (tanh); LRA ниже 2,5 LU = плоско;
  • по таймингу реплик: разброс пауз между репликами (σ) ≥ 0,1 с, иначе метроном;
  • на каждую реплику: темп ≤ 6,3 слога/с (гласные текста на длительность реплики) и, если есть голос
    без музыки, медиана F0 ≤ 250 Гц (выше = фальцет).
Пороги и откуда они: docs/QA-THRESHOLDS.md. Пороги выбраны по одобренным эталонам одного автора и по
просмотрам не калиброваны: это диагностика, а не приговор. Решает человек на слух.

Вход: готовый файл и JSON с репликами, тайминги в секундах от начала файла:
  [{"id": "l1", "text": "Текст реплики", "start": 0.40, "end": 2.10}, ...]
  или {"lines": [...]}. Необязательно у реплики "file": wav этой реплики без музыки (для F0).
  --voice voice.wav: дорожка голоса без музыки с тем же таймингом; F0 тогда режется из неё.
  Без голоса без музыки F0 не меряется (в отчёте null), проверка f0 помечается как не выполненная.
Слоги считаются по гласным (кириллица и латиница): для латиницы это грубо («Claude» = 3 гласных
на 1 слог), поэтому иноязычные слова в "text" лучше писать так, как их произносит синтез.
Выход: JSON-отчёт (--json), сводка в stdout. Код возврата: 0, если все выполненные проверки прошли; иначе 1.
Зависимости: numpy, soundfile, ffmpeg в PATH; librosa — только для F0.

Пример:
  python3 tools/qa/voice_qa.py output/final.mp4 --lines voice/timing.json --voice voice/voice.wav \\
      --json qa/voice-qa.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

TP_MIN, LRA_MIN, GAP_SD_MIN, RATE_MAX, F0_MAX = -2.5, 2.5, 0.1, 6.3, 250.0
VOWELS = set('аеёиоуыэюяaeiouy')


def ebur128(path):
    """(integrated LUFS, LRA LU, true peak dBTP) файла через ffmpeg ebur128."""
    ff = os.environ.get('FFMPEG', 'ffmpeg')
    err = subprocess.run([ff, '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    if 'Summary:' not in err:
        raise RuntimeError(f'ffmpeg ebur128 не дал сводку для {path}')
    s = err[err.rindex('Summary:'):]
    g = lambda k: float(re.search(k + r':\s+(-?[\d.]+|-inf)', s).group(1))
    return g('I'), g('LRA'), g('Peak')


def syllables(text):
    return sum(ch in VOWELS for ch in text.lower())


def gap_stats(lines):
    """Паузы между соседними репликами (start следующей − end предыдущей) и их σ."""
    ls = sorted(lines, key=lambda x: x['start'])
    gaps = [round(b['start'] - a['end'], 3) for a, b in zip(ls, ls[1:])]
    sd = float(np.std(gaps)) if len(gaps) > 1 else 0.0
    return gaps, round(sd, 3)


def line_rates(lines):
    return {x['id']: round(syllables(x['text']) / max(x['end'] - x['start'], .1), 2) for x in lines}


def median_f0(x, sr):
    """Медиана F0 по громким кадрам, Гц; 0 — если голоса нет."""
    import librosa
    x = np.asarray(x, dtype=np.float32)
    if x.ndim > 1:
        x = x.mean(1)
    if len(x) < 2048:
        return 0
    f = librosa.yin(x, fmin=60, fmax=500, sr=sr, frame_length=2048)
    e = librosa.feature.rms(y=x, frame_length=2048, hop_length=512)[0]
    n = min(len(f), len(e))
    v = f[:n][e[:n] > e.max() * .2]
    return round(float(np.median(v))) if len(v) else 0


def line_f0(lines, base, voice=None):
    """F0 каждой реплики: из её "file" или из куска --voice; None, если голоса без музыки нет."""
    import soundfile as sf
    out, track = {}, None
    if voice:
        track = sf.read(voice)
    for x in lines:
        if x.get('file'):
            y, sr = sf.read(base / x['file'])
            out[x['id']] = median_f0(y, sr)
        elif track is not None:
            y, sr = track
            out[x['id']] = median_f0(y[int(x['start'] * sr):int(x['end'] * sr)], sr)
        else:
            out[x['id']] = None
    return out


def evaluate(tp, lra, lines, f0=None, tp_min=TP_MIN, lra_min=LRA_MIN, gap_sd_min=GAP_SD_MIN,
             rate_max=RATE_MAX, f0_max=F0_MAX, f0_diagnostic=False):
    """Чистая логика гейта: замеры → checks {имя: [значение, прошло|None]}; None = не мерилось."""
    gaps, sd = gap_stats(lines)
    rates = line_rates(lines)
    f0 = f0 or {}
    measured_f0 = {k: v for k, v in f0.items() if v}
    checks = {
        'true_peak': [round(tp, 2), tp >= tp_min],
        'lra': [round(lra, 2), lra >= lra_min],
        'gap_sd': [sd, sd >= gap_sd_min if len(gaps) > 1 else None],
        'rate_over': [[k for k, v in rates.items() if v > rate_max], None],
        'f0_over': [[k for k, v in measured_f0.items() if v > f0_max], None],
    }
    checks['rate_over'][1] = not checks['rate_over'][0]
    checks['f0_over'][1] = (not checks['f0_over'][0]) if measured_f0 else None
    rows = [{'id': x['id'], 'dur': round(x['end'] - x['start'], 2), 'rate': rates[x['id']], 'f0': f0.get(x['id'])}
            for x in lines]
    # f0_diagnostic: голос без откалиброванного потолка; F0 пишем в отчёт, но в pass он не входит
    gate = {k: v for k, v in checks.items() if not (f0_diagnostic and k == 'f0_over')}
    return {'gaps': gaps, 'gap_sd': sd, 'lines': rows, 'checks': checks, 'f0_diagnostic': f0_diagnostic,
            'pass': all(v[1] is not False for v in gate.values())}


def load_lines(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    lines = data['lines'] if isinstance(data, dict) else data
    for i, x in enumerate(lines):
        x.setdefault('id', f'l{i + 1}')
        if not {'text', 'start', 'end'} <= x.keys():
            raise ValueError(f'реплика {x["id"]}: нужны поля text, start, end')
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description='Голосовой гейт: true peak, LRA, разброс пауз, темп, F0 по репликам.')
    ap.add_argument('file', type=Path, help='готовый mp4 или wav')
    ap.add_argument('--lines', type=Path, required=True, help='JSON реплик: id, text, start, end [, file]')
    ap.add_argument('--voice', type=Path, help='дорожка голоса без музыки с тем же таймингом (для F0)')
    ap.add_argument('--json', type=Path, help='куда записать отчёт')
    ap.add_argument('--tp-min', type=float, default=TP_MIN)
    ap.add_argument('--lra-min', type=float, default=LRA_MIN)
    ap.add_argument('--gap-sd-min', type=float, default=GAP_SD_MIN)
    ap.add_argument('--rate-max', type=float, default=RATE_MAX)
    ap.add_argument('--f0-max', type=float, default=F0_MAX)
    ap.add_argument('--f0-diagnostic', action='store_true',
                    help='голос без откалиброванного потолка F0: высота только в отчёте, на pass не влияет')
    a = ap.parse_args(argv)
    lines = load_lines(a.lines)
    lufs, lra, tp = ebur128(a.file)
    f0 = line_f0(lines, a.lines.parent, a.voice)
    res = evaluate(tp, lra, lines, f0, a.tp_min, a.lra_min, a.gap_sd_min, a.rate_max, a.f0_max, a.f0_diagnostic)
    res = {'file': a.file.name, 'lufs': lufs, 'true_peak': tp, 'lra': lra, **res}
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    for k, (v, ok) in res['checks'].items():
        mark = '—' if ok is None else ('ok' if ok else 'FAIL')
        if k == 'f0_over' and res['f0_diagnostic'] and ok is not None:
            mark = 'diag'
        print(f"{k:10} {mark:4} {v}")
    print('pass' if res['pass'] else 'FAIL', f"(LUFS {lufs}, σ пауз {res['gap_sd']} с)")
    return 0 if res['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
