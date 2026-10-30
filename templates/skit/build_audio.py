# SPDX-License-Identifier: MIT
"""lines.json (+ optional takes) -> timeline.json + audio/mix.wav for the skit scene.

Layout: lines follow each other with a short gap; a cut on every line; events are anchored to WORDS, so when
a take changes, cuts, stamps, phone messages and sounds move with it. Word timings come from:
  1. placeholder babble (no 'voice' in lines.json): exact by construction;
  2. a real take + --asr: faster-whisper word timestamps (pip install faster-whisper);
  3. a real take without --asr: spread over the take proportionally to word length (good enough to block out).

  python3 build_audio.py               # timeline.json + audio/mix.wav
  python3 build_audio.py --asr         # word timings from faster-whisper for real takes
SFX are synthesized in code (no sample files). Music is optional: lines.json -> music.file (open license, credit it).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(1021)        # seeded: same lines -> same mix, byte for byte


# ---------- voice ----------
def syl(word: str) -> int:
    return max(1, len(re.findall(r'[aeiouyаеёиоуыэюя]', word.lower())))


def babble(text: str, who: str):
    """Placeholder speech: voiced blips per syllable. Returns audio and exact word timings."""
    f0 = 135.0 if who == 'dude' else 210.0
    out, words, t = [], [], 0.0
    for w in text.split():
        st = t
        for k in range(syl(w)):
            d = .1 + .05 * rng.random(); tt = np.arange(int(d * SR)) / SR
            ph = 2 * np.pi * np.cumsum(f0 * (1 + .08 * np.sin(2 * np.pi * 3 * tt + k))) / SR
            x = sum(np.sin(ph * h) / h for h in range(1, 7)) * np.sin(np.pi * tt / d) ** .7 * .35
            out += [x, np.zeros(int(.02 * SR))]; t += d + .02
        words.append([w, round(st, 3), round(t, 3)])
        pause = .16 if w[-1] in ',.;:!?' else .05
        out.append(np.zeros(int(pause * SR))); t += pause
    return np.concatenate(out), words


def load_take(path: Path):
    """Real take -> (audio trimmed to speech and normalized, seconds cut from the start)."""
    import soundfile as sf
    x, sr = sf.read(path, dtype='float64', always_2d=True); x = x.mean(1)
    if sr != SR: x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
    hop = int(.01 * SR); r = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) + 1e-9 for k in range(0, len(x) - hop, hop)])
    on = np.where(20 * np.log10(r / r.max()) > -38)[0]
    a = max(0, on[0] * hop - int(.04 * SR))
    x = x[a:min(len(x), (on[-1] + 1) * hop + int(.12 * SR))]   # long tail: TTS clips endings
    return x / (np.abs(x).max() + 1e-9) * .89, a / SR


def spread_words(text: str, dur: float):
    ws = text.split(); n = sum(len(w) + 2 for w in ws); t, out = 0.0, []
    for w in ws:
        d = dur * (len(w) + 2) / n; out.append([w, round(t, 3), round(t + d * .85, 3)]); t += d
    return out


def asr_words(path: Path, lang: str | None):
    from faster_whisper import WhisperModel
    m = WhisperModel('small', compute_type='int8')
    segs, _ = m.transcribe(str(path), language=lang, word_timestamps=True)
    return [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]


def take_words(path: Path, text: str, x, offset: float, asr: bool, lang: str | None):
    """Word timings relative to the TRIMMED take x. ASR runs on the original file, so its times are shifted back by
    the leading silence load_take cut off (offset), and clipped to the take."""
    dur = len(x) / SR
    if not asr:
        return spread_words(text, dur)
    out = []
    for w, s, e in asr_words(path, lang):
        s, e = s - offset, e - offset
        if e <= 0 or s >= dur:
            continue                     # inside the cut-off silence
        out.append([w, round(max(0.0, s), 3), round(min(dur, e), 3)])
    return out


def envelope(x, fps, att=.045, rel=.11, vmax=4.0):
    """Mouth per frame: RMS 5 ms -> attack/release -> speed limit (raw RMS makes the mouth chatter)."""
    hop = int(.005 * SR); r = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(0, len(x) - hop, hop)])
    r = r / (np.percentile(r, 95) or 1); ka, kr = 1 - np.exp(-.005 / att), 1 - np.exp(-.005 / rel)
    y = np.zeros_like(r); v = 0.0; step = vmax * .005
    for i, e in enumerate(np.minimum(r, 1.0)):
        tgt = v + (e - v) * (ka if e > v else kr); v = v + np.clip(tgt - v, -step, step); y[i] = v
    tt = np.arange(0, len(x) / SR, 1 / fps); idx = np.minimum((tt / .005).astype(int), len(y) - 1)
    return [round(float(v), 3) for v in y[idx]]


# ---------- SFX, all synthesized ----------
def t_(d): return np.arange(int(d * SR)) / SR
def lp(x, k=6): return np.convolve(x, np.ones(k) / k, mode='same')


def whoosh(d=.3):            # smoothed white noise, sin^2 envelope: the quiet "sniff" on every cut
    t = t_(d); return lp(rng.normal(size=len(t))) * np.sin(np.pi * t / d) ** 2


def pop():
    t = t_(.08); return np.sin(2 * np.pi * np.cumsum(900 - 5000 * t) / SR) * np.exp(-t / .02) * .3


def ding(a=1046.5, b=1568.0):
    t = t_(1.2); x = np.zeros_like(t)
    for f0, st in ((a, 0), (b, .09)):
        q = np.clip(t - st, 0, None); x += (t >= st) * np.sin(2 * np.pi * f0 * q) * np.exp(-q / .4)
    return x * .22


def thud(f=60, d=.4):
    t = t_(d); ph = 2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-t / .03))) / SR
    return np.sin(ph) * np.exp(-t / .12) * .7


def tick():
    t = t_(.018); return lp(rng.normal(size=len(t)), 2) * np.exp(-t / .003) * .5


def cricket(d=.9):
    t = t_(d); return np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 32 * t) > .2) * (np.sin(2 * np.pi * 3.2 * t) > 0) * .12


SFX = {'whoosh': whoosh, 'pop': pop, 'ding': ding, 'thud': thud, 'tick': tick, 'cricket': cricket}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--asr', action='store_true'); ap.add_argument('--lang', default=None)
    a = ap.parse_args()
    S = json.loads((P / 'lines.json').read_text()); fps = S.get('fps', 30)
    t, L = S.get('lead', .15), []
    for i, ln in enumerate(S['lines']):
        t += ln.get('gap', .12) if i else 0
        if ln.get('voice'):
            x, offset = load_take(P / ln['voice'])
            words = take_words(P / ln['voice'], ln['text'], x, offset, a.asr, a.lang)
        else:
            x, words = babble(ln['text'], ln['who'])
        L.append({**ln, 'start': round(t, 3), 'end': round(t + len(x) / SR, 3), 'x': x,
                  'words': [[w, round(t + s, 3), round(t + e, 3)] for w, s, e in words]})
        t += len(x) / SR
    dur = round(t + S.get('tail', 1.5), 2)
    norm = lambda s: re.sub(r'[^\w]', '', s.lower().replace('ё', 'е'))

    def word_time(ln, pref):
        for w, s, e in ln['words']:
            if norm(w).startswith(norm(pref)): return s
        raise SystemExit(f'no word "{pref}" in {ln["id"]}: {[w[0] for w in ln["words"]]}')

    shots, marks, phone, stamps, reactions, sfx_at = [], {}, [], [], [], []
    for i, ln in enumerate(L):
        shots.append({'name': ln.get('shot', ln['who']), 'start': 0.0 if i == 0 else round(ln['start'] - .06, 3)})
        for ev in ln.get('events', []):
            at = round(word_time(ln, ev['word']), 3); marks[ev['name']] = at
            if ev.get('cut'): shots.append({'name': ev['cut'], 'start': round(at - .06, 3)})
            if ev.get('msg'): phone.append({'at': at, **ev['msg']})
            if ev.get('stamp'): stamps.append({'at': at, 'text': ev['stamp']})
            if ev.get('react'): reactions.append({'who': ln['who'], 'kind': ev['react'], 'a': at, 'b': round(min(ln['end'] + .8, dur), 3)})
            if ev.get('sfx'): sfx_at.append((at, ev['sfx']))
    shots.sort(key=lambda s: s['start'])
    for k, s in enumerate(shots): s['end'] = shots[k + 1]['start'] if k + 1 < len(shots) else dur
    short = [(s['name'], round(s['end'] - s['start'], 2)) for s in shots if s['end'] - s['start'] < .5]
    if short: raise SystemExit(f'shots shorter than 0.5 s: {short}')
    lines = [{'id': l['id'], 'who': l['who'], 'text': l['text'], 'start': l['start'], 'end': l['end'], 'words': l['words'],
              'env': envelope(l['x'], fps)} for l in L]
    (P / 'timeline.json').write_text(json.dumps({'fps': fps, 'duration': dur, 'shots': shots, 'lines': lines, 'marks': marks,
                                                 'phone': phone, 'stamps': stamps, 'reactions': reactions,
                                                 'music': S.get('music', {})}, ensure_ascii=False) + '\n')
    # ---------- mix ----------
    import soundfile as sf
    n = int(dur * SR); speech, fx = np.zeros((n, 2)), np.zeros((n, 2))

    def put(buf, at, x, g=1.0, pan=0.0):
        p = int(round(at * SR)); p0 = max(0, p); q = min(n, p + len(x))
        if q > p0:
            v = x[p0 - p:q - p] * g; buf[p0:q, 0] += v * np.sqrt((1 - pan) / 2) * 1.414; buf[p0:q, 1] += v * np.sqrt((1 + pan) / 2) * 1.414

    for l in L: put(speech, l['start'], l['x'], 1.0, -.15 if l['who'] == 'dude' else .15)
    for s in shots[1:]: put(fx, s['start'] - .12, whoosh(), .10, rng.uniform(-.5, .5))      # on EVERY cut
    for at, kind in sfx_at: put(fx, at, SFX[kind](), .6)
    mix = speech + fx
    mu = S.get('music') or {}
    if mu.get('file') and shutil.which('ffmpeg'):
        tmp = P / 'audio/music-cut.wav'; tmp.parent.mkdir(exist_ok=True)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-stream_loop', '-1', '-i', str(P / mu['file']), '-t', str(dur), '-ar', str(SR), '-ac', '2', str(tmp)], check=True)
        m, _ = sf.read(tmp); music = np.zeros((n, 2)); music[:min(n, len(m))] = m[:n]
        duck = np.ones(n)
        for l in L: duck[int(l['start'] * SR):int(l['end'] * SR)] = .32                     # duck under speech
        duck = np.convolve(duck, np.ones(int(.25 * SR)) / int(.25 * SR), mode='same')
        mix += music * duck[:, None] * mu.get('gain', .3)
    f = int(.35 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
    (P / 'audio').mkdir(exist_ok=True); raw = P / 'audio/mix-raw.wav'; out = P / 'audio/mix.wav'
    sf.write(raw, mix * (.9 / (np.abs(mix).max() + 1e-9)), SR, subtype='PCM_24')
    if shutil.which('ffmpeg'):          # two-pass loudnorm to -15 LUFS, true peak -3 dBTP (AAC adds ~1-2 dB later)
        meas = subprocess.run(['ffmpeg', '-i', str(raw), '-af', 'loudnorm=I=-15:TP=-3:LRA=11:print_format=json', '-f', 'null', '-'],
                              capture_output=True, text=True).stderr
        m = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
        ln = (f"loudnorm=I=-15:TP=-3:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(raw), '-af', ln, '-ar', str(SR), str(out)], check=True)
    else:
        shutil.copy(raw, out)
    print('ok', dur, 's,', len(shots), 'shots,', len(marks), 'marks')
    for s in shots: print(f"  {s['name']:6s} {s['start']:6.2f}-{s['end']:6.2f}")


if __name__ == '__main__':
    main()
