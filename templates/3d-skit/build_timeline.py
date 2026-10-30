# SPDX-License-Identifier: MIT
"""script.json (+ optional voice takes) -> timeline.json + audio/mix.wav for the 3D skit scene.

One cut per line, mouth envelope per frame, reactions as time windows, a soft whoosh on every cut.
Without a 'voice' file a line gets a placeholder babble (voiced blips, one per syllable), so you can
check cuts, mouth and framing before any TTS. Replace it with real takes later: timing follows the audio.

  python3 build_timeline.py                 # writes timeline.json and audio/mix.wav next to this file
  python3 build_timeline.py --no-audio      # timeline only (numpy needed, soundfile not)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 24000
rng = np.random.default_rng(7)          # every random thing is seeded: same script -> same file


def syllables(text: str) -> int:
    return max(1, len(re.findall(r'[aeiouyаеёиоуыэюя]', text.lower())))


def babble(text: str, who: str) -> np.ndarray:
    """Placeholder speech: one voiced blip per syllable, pitch per character, pauses on punctuation."""
    f0 = 135.0 if who == 'dude' else 210.0
    out = []
    for word in text.split():
        for k in range(syllables(word)):
            d = .11 + .05 * rng.random()
            t = np.arange(int(d * SR)) / SR
            f = f0 * (1 + .08 * np.sin(2 * np.pi * 3 * t + k))
            ph = 2 * np.pi * np.cumsum(f) / SR
            x = sum(np.sin(ph * h) / h for h in range(1, 7)) * np.sin(np.pi * t / d) ** .7
            out += [x * .35, np.zeros(int(.025 * SR))]
        out.append(np.zeros(int((.16 if word[-1] in ',.;:!?' else .05) * SR)))
    return np.concatenate(out).astype(np.float32)


def trim(x: np.ndarray, thr_db=-38, pad=.04) -> np.ndarray:
    """Cut leading/trailing silence of a real take. Keep a longer tail: TTS often clips the last syllable."""
    hop = int(.01 * SR)
    r = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) + 1e-9 for k in range(0, len(x) - hop, hop)])
    on = np.where(20 * np.log10(r / r.max()) > thr_db)[0]
    a, b = max(0, on[0] * hop - int(pad * SR)), min(len(x), (on[-1] + 1) * hop + int(pad * 2 * SR))
    y = x[a:b].copy(); f = int(.01 * SR)
    y[:f] *= np.linspace(0, 1, f); y[-f * 3:] *= np.linspace(1, 0, f * 3)
    return y


def envelope(x: np.ndarray, fps: int, att=.045, rel=.11, vmax=4.0) -> list:
    """Mouth opening per video frame: RMS over 5 ms -> attack/release follower -> speed limit.
    The speed limit matters: raw RMS makes the jaw chatter at 5-8 Hz and reads as jitter on screen."""
    hop = int(.005 * SR)
    r = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(0, len(x) - hop, hop)])
    r = r / (np.percentile(r, 95) or 1)
    ka, kr = 1 - np.exp(-.005 / att), 1 - np.exp(-.005 / rel)
    y = np.zeros_like(r); v = 0.0; step = vmax * .005
    for i, e in enumerate(np.minimum(r, 1.0)):
        tgt = v + (e - v) * (ka if e > v else kr); v = v + np.clip(tgt - v, -step, step); y[i] = v
    t = np.arange(0, len(x) / SR, 1 / fps); idx = np.minimum((t / .005).astype(int), len(y) - 1)
    return [round(float(v), 3) for v in y[idx]]


def whoosh(d=.3) -> np.ndarray:
    """Smoothed white noise with a sin^2 envelope. Quiet, on every cut, 0.12 s before it."""
    n = int(d * SR); t = np.arange(n) / n
    w = np.convolve(rng.normal(size=n), np.ones(6) / 6, mode='same')
    return (w * np.sin(np.pi * t) ** 2 * .1).astype(np.float32)


def load_take(path: Path) -> np.ndarray:
    import soundfile as sf
    x, sr = sf.read(path, dtype='float32', always_2d=True)
    x = x.mean(1)
    if sr != SR:                                   # plain linear resample is enough for a mouth envelope
        x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x).astype(np.float32)
    y = trim(x)
    return y / (np.abs(y).max() + 1e-9) * .89


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--script', type=Path, default=HERE / 'script.json')
    ap.add_argument('--no-audio', action='store_true')
    a = ap.parse_args()
    S = json.loads(a.script.read_text())
    fps, gap = S.get('fps', 30), S.get('gap', .2)
    t = S.get('lead', .25); lines, shots, reactions, takes = [], [], [], []
    for i, ln in enumerate(S['lines']):
        x = load_take(HERE / ln['voice']) if ln.get('voice') else babble(ln['text'], ln['who'])
        start, end = round(t, 3), round(t + len(x) / SR, 3)
        lines.append({'i': i + 1, 'who': ln['who'], 'text': ln['text'], 'start': start, 'end': end, 'env': envelope(x, fps),
                      'placeholder': not ln.get('voice')})
        shots.append({'name': ln.get('shot', ln['who']), 'start': 0.0 if i == 0 else round(t - .1, 3)})
        for r in ln.get('react', []):
            reactions.append({'who': r['who'], 'kind': r['kind'], 'a': round(start + r['a'], 3), 'b': round(start + r['b'], 3)})
        takes.append((start, x)); t += len(x) / SR + gap
    tail = S.get('tail_shot')
    dur = round(t - gap + .3, 3)
    if tail:
        ts = round(t - .05, 3); shots.append({'name': tail['shot'], 'start': ts})
        for r in tail.get('react', []):
            reactions.append({'who': r['who'], 'kind': r['kind'], 'a': round(ts + r['a'], 3), 'b': round(ts + r['b'], 3)})
        dur = round(ts + tail['seconds'], 3)
    for k, s in enumerate(shots):
        s['end'] = shots[k + 1]['start'] if k + 1 < len(shots) else dur
        assert s['end'] - s['start'] >= .4, f'shot {k} is shorter than 0.4 s: merge it or lengthen the line'
    tl = {'fps': fps, 'duration': dur, 'lines': lines, 'shots': shots, 'reactions': reactions}
    (HERE / 'timeline.json').write_text(json.dumps(tl, ensure_ascii=False) + '\n')
    if not a.no_audio:
        import soundfile as sf
        n = int(dur * SR) + 1; voice = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
        for start, x in takes:
            p = int(start * SR); voice[p:p + len(x)] += x[:n - p]
        for s in shots[1:]:
            w = whoosh(); p = max(0, int((s['start'] - .12) * SR)); fx[p:p + len(w)] += w[:n - p]
        room = np.convolve(rng.normal(size=n), np.ones(40) / 40, mode='same').astype(np.float32)
        room *= .015 / (np.abs(room).max() + 1e-9)
        mix = voice * .85 + fx + room; mix *= .92 / (np.abs(mix).max() + 1e-9)
        f = int(.3 * SR); mix[-f:] *= np.linspace(1, 0, f)
        (HERE / 'audio').mkdir(exist_ok=True); sf.write(HERE / 'audio/mix.wav', mix, SR)
    print('duration', dur, 's,', len(shots), 'shots,', sum(l['placeholder'] for l in lines), 'placeholder lines')


if __name__ == '__main__':
    main()
