#!/usr/bin/env python3
"""Feature map of a music track: beats, downbeats, sections, drum hits and 100 Hz envelopes.

Idea after analysis/analyze.py (band onsets, envelopes with a fast attack and slow release, 99th percentile
normalisation), app/src/engine/audio.ts (hit/env) and app/src/timeline.ts (cut on the last beat before the
first word) from mexicat/pdoom-video (MIT, (c) 2026 Giacomo Magnanini); the code is written from scratch.
Difference: there are no Demucs stems here, hits are found in frequency bands of the full mix, so kick,
snare and hat are approximate; sections come from timbre and harmony self-similarity, not from hand labels.

A TOOL, NOT A LAW. On one measured hit reel the cuts landed on a half-beat no more often than random cuts
would (33-35 % against 31-33 %), see recipes/sound/sound-track-feature-map.md. Use the map for interface
sounds, accents and a background pulse, and only optionally for single cuts. `cuts` only PROPOSES points and
writes them to a JSON file; it never edits your scene.

Commands (needs numpy, scipy and librosa: `pip install librosa`):
  python3 tools/audio/audio_feats.py analyze music/track.mp3            # -> music/track.feats.json (cached by sha256)
  python3 tools/audio/audio_feats.py show music/track.mp3               # BPM, beats, sections, hits per minute
  python3 tools/audio/audio_feats.py export music/track.mp3 --offset 12 --duration 30 --out scene/audio-feats.gen.js
  python3 tools/audio/audio_feats.py cuts music/track.mp3 --offset 12 --words voice-track.json --out qa/beat-cuts.json

Cache format (`<track>.feats.json`): duration, bpm, beats[], downbeats[], sections[{name, start, end, energy}],
fps=100, env{rms, low, mid, high} (0..1, frame i at i/100 s), onsets{kick, snare, hat}[[t, strength 0..1]],
quality{beat_confidence, downbeat_margin}. Times are track times; in the video t_video = t_track - offset,
`export` and `cuts` do that for you. The scene side is `audio-feats.js` next to this file.
Exit codes: 0; 1 when the track cannot be read or librosa is missing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
SR = 44100
FPS = 100
VERSION = 1


# ------------------------------------------------------------------ sound
def load_mono(path, sr=SR):
    cmd = [FFMPEG, '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def band_sos(lo, hi, sr):
    from scipy.signal import butter
    if lo and hi:
        return butter(4, [lo, hi], btype='band', fs=sr, output='sos')
    if hi:
        return butter(4, hi, btype='low', fs=sr, output='sos')
    return butter(4, lo, btype='high', fs=sr, output='sos')


def frame_rms(x, sr=SR, fps=FPS, win=2048):
    hop = sr / fps
    n = int(math.ceil(len(x) / sr * fps))
    pad = np.pad(x, (win // 2, win // 2 + int(hop) + 2))
    idx = (np.arange(n) * hop).astype(int)
    c = np.concatenate([[0.0], np.cumsum(pad.astype(np.float64) ** 2)])
    return np.sqrt(np.maximum((c[idx + win] - c[idx]) / win, 0))


def smooth_env(x, fps=FPS, attack=.010, release=.090):
    """One-pole follower: 10 ms attack, 90 ms release, a pulse without jitter."""
    aa, ar = math.exp(-1 / (attack * fps)), math.exp(-1 / (release * fps))
    y, s = np.empty_like(x), 0.0
    for i, v in enumerate(x):
        a = aa if v > s else ar
        s = a * s + (1 - a) * v
        y[i] = s
    return y


def norm01(x, pct=99.0):
    return np.clip(x / (np.percentile(x, pct) + 1e-12), 0, 1)


def band_onsets(x, sr, lo, hi, win=.010, hop_s=.002, min_gap=.08, rel_db=10.0):
    """Attacks in a band: the steepest rise of the band's log energy; strength = peak in dB."""
    from scipy.ndimage import median_filter, uniform_filter1d
    from scipy.signal import find_peaks, sosfiltfilt
    xb = sosfiltfilt(band_sos(lo, hi, sr), x)
    h, w = int(hop_s * sr), int(win * sr)
    e = np.convolve(xb.astype(np.float64) ** 2, np.ones(w) / w, mode='same')[::h]
    db = 10 * np.log10(e + 1e-10)
    fps = sr / h
    d = uniform_filter1d(np.diff(db, prepend=db[0]), 3)
    lag = int(.02 * fps)
    rise = db - np.concatenate([np.full(lag, db[0]), db[:-lag]])
    floor = median_filter(db, int(1.0 * fps) | 1)
    pk, _ = find_peaks(rise, height=rel_db, distance=int(min_gap * fps))
    times, strength = [], []
    for p in pk:
        a = max(0, p - lag)
        q = a + int(np.argmax(d[a:p + 1]))
        peak_db = db[p:p + int(.03 * fps)].max()
        if peak_db < floor[p] + 3:
            continue
        times.append(q / fps)
        strength.append(peak_db)
    return np.array(times), np.array(strength)


def strength01(v, lo=5, hi=95):
    if len(v) == 0:
        return v
    a, b = np.percentile(v, lo), np.percentile(v, hi)
    return np.clip((v - a) / (b - a + 1e-9) * .8 + .2, 0, 1)


def drum_onsets(x, sr):
    """Kick < 120 Hz, snare 1.5-5 kHz with a noise tail, hat > 7 kHz away from snare and kick.

    Full mix, not a stem: bass and melody also attack in these bands, so the thresholds are higher than with
    stems, and a snare is kept only with a noise tail 40-120 ms after the attack (a tonal note has none).
    """
    from scipy.signal import sosfiltfilt
    kt, kdb = band_onsets(x, sr, None, 120, win=.012, min_gap=.15, rel_db=12)
    st, _ = band_onsets(x, sr, 1500, 5000, win=.010, min_gap=.15, rel_db=10)
    sdb = np.array([])
    if len(st):
        xb = sosfiltfilt(band_sos(500, 5000, sr), x)
        e = np.sqrt(np.convolve(xb.astype(np.float64) ** 2, np.ones(441) / 441, mode='same'))
        tail = np.array([20 * np.log10(e[int((t + .04) * sr):int((t + .12) * sr)].mean() + 1e-9) for t in st])
        rel = np.array([tail[i] - tail[np.abs(st - st[i]) < 2.5].max() for i in range(len(st))])
        keep = (rel > -8) & (tail > np.percentile(tail, 95) - 25)
        st, sdb = st[keep], tail[keep]
    ht, hdb = band_onsets(x, sr, 7000, None, win=.006, min_gap=.06, rel_db=9)
    for other, gap in ((st, .04), (kt, .03)):
        if len(other) and len(ht):
            keep = np.min(np.abs(ht[:, None] - other[None, :]), axis=1) > gap
            ht, hdb = ht[keep], hdb[keep]

    def pack(t, s):
        return [[round(float(a), 3), round(float(b), 3)] for a, b in zip(t, strength01(s))]
    return {'kick': pack(kt, kdb), 'snare': pack(st, sdb), 'hat': pack(ht, hdb)}


def beat_grid(y22, low_env):
    """librosa beats on the percussive part, plus the bar phase.

    Which of four beats is the downbeat is chosen by the harmony change on the beat (chroma novelty) with
    weight 1 and bass energy with weight 0.5. Without stems this is a guess: `downbeat_margin` < 0.15 means
    the phases are nearly equal. Always 4/4.
    """
    import librosa
    yp = librosa.effects.percussive(y22, margin=2.0)
    onset = librosa.onset.onset_strength(y=yp, sr=22050)
    # trim=False: otherwise librosa drops the "weak" beats of a quiet intro, and a video may start the
    # track 40 s in. In an intro without drums the beats are a continuation of the grid, not a fact.
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=22050, units='time', trim=False)
    tempo = float(np.atleast_1d(tempo)[0])
    beats = np.asarray(beats, float)
    if len(beats) < 8:
        return tempo, beats, beats[:0], 0.0, 0.0
    ot = librosa.times_like(onset, sr=22050)
    conf = float(np.interp(beats, ot, onset).mean() / (onset.mean() + 1e-9))
    hop = 512
    ch = librosa.feature.chroma_cqt(y=y22, sr=22050, hop_length=hop)
    c = librosa.util.sync(ch, librosa.time_to_frames(beats, sr=22050, hop_length=hop), aggregate=np.median)[:, 1:]
    cn = c / (np.linalg.norm(c, axis=0) + 1e-9)
    nov = np.r_[0, 1 - (cn[:, 1:] * cn[:, :-1]).sum(0)][:len(beats)]
    nov = np.pad(nov, (0, len(beats) - len(nov)))
    lo = np.interp(beats, np.arange(len(low_env)) / FPS, low_env)

    def z(v):
        return (v - v.mean()) / (v.std() + 1e-9)
    zn, zl = z(nov), z(lo)
    score = np.array([zn[k::4].mean() + .5 * zl[k::4].mean() for k in range(4)])
    k = int(np.argmax(score))
    srt = np.sort(score)
    margin = float(srt[-1] - srt[-2])
    return tempo, beats, beats[k::4], conf, margin


def sections(y22, beats, downbeats, rms_env, duration):
    """Sections by chroma and MFCC self-similarity on beats, boundaries snapped to downbeats."""
    import librosa
    if len(beats) < 16:
        return [{'name': 's0', 'start': 0.0, 'end': round(duration, 3), 'energy': 'mid'}]
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y22, sr=22050, hop_length=hop)
    mfcc = librosa.feature.mfcc(y=y22, sr=22050, hop_length=hop, n_mfcc=13)
    bf = librosa.time_to_frames(beats, sr=22050, hop_length=hop)
    feat = np.vstack([librosa.util.normalize(librosa.util.sync(chroma, bf), axis=0),
                      librosa.util.normalize(librosa.util.sync(mfcc, bf), axis=0)])
    k = int(np.clip(round(duration / 28), 3, 10))
    bounds = librosa.segment.agglomerative(feat, k)
    bt = np.concatenate([[0.0], beats])
    starts = sorted({0.0} | {float(bt[min(i, len(bt) - 1)]) for i in bounds if i > 0})
    if len(downbeats):
        starts = sorted({0.0} | {float(downbeats[np.argmin(np.abs(downbeats - s))]) for s in starts[1:]})
    starts = [s for i, s in enumerate(starts) if i == 0 or s - starts[i - 1] > 4.0]
    ends = starts[1:] + [duration]
    t = np.arange(len(rms_env)) / FPS
    lev = [float(rms_env[(t >= a) & (t < b)].mean()) for a, b in zip(starts, ends)]
    q1, q2 = np.percentile(lev, [33, 66]) if len(lev) > 2 else (min(lev), max(lev))

    def tag(v):
        return 'low' if v < q1 else ('high' if v > q2 else 'mid')
    return [{'name': f's{i}', 'start': round(a, 3), 'end': round(b, 3), 'energy': tag(v)}
            for i, (a, b, v) in enumerate(zip(starts, ends, lev))]


# ------------------------------------------------------------------ analysis and cache
def feats_path(track: Path) -> Path:
    return track.with_suffix('.feats.json')


def analyze_signal(x, sr=SR):
    """Feature map of a mono float signal (no cache, no file): the core used by `analyze` and the tests."""
    import librosa
    from scipy.signal import sosfiltfilt
    if sr != SR:
        x = librosa.resample(x, orig_sr=sr, target_sr=SR)
    duration = len(x) / SR
    env = {'rms': frame_rms(x)}
    for nm, (lo, hi) in {'low': (None, 150), 'mid': (150, 2000), 'high': (4000, None)}.items():
        env[nm] = frame_rms(sosfiltfilt(band_sos(lo, hi, SR), x))
    env = {k: norm01(smooth_env(v)) for k, v in env.items()}
    y22 = librosa.resample(x, orig_sr=SR, target_sr=22050)
    bpm, beats, downbeats, conf, margin = beat_grid(y22, env['low'])
    secs = sections(y22, beats, downbeats, env['rms'], duration)
    onsets = drum_onsets(x, SR)
    return {
        'version': VERSION, 'duration': round(duration, 3), 'bpm': round(bpm, 2), 'time_signature': 4,
        'beats': [round(float(t), 3) for t in beats],
        'downbeats': [round(float(t), 3) for t in downbeats],
        'sections': secs, 'fps': FPS,
        'env': {k: [round(float(v), 2) for v in a] for k, a in env.items()},
        'onsets': onsets,
        'quality': {'beat_confidence': round(conf, 2), 'downbeat_margin': round(margin, 3)},
        'notes': ('Hits from bands of the full mix, no stems: kick < 120 Hz, snare 1.5-5 kHz with a noise tail, '
                  'hat > 7 kHz. beat_confidence < 1.3 = weak rhythm (orchestral, ambient), do not use the beats. '
                  'downbeat_margin < 0.15 = bar phase is a guess. A tool, not a law: cuts on the beat are optional.'),
    }


def analyze(track, out=None, force=False, quiet=False):
    track = Path(track)
    out = Path(out) if out else feats_path(track)
    digest = sha256(track)
    if out.exists() and not force:
        old = json.loads(out.read_text(encoding='utf-8'))
        if old.get('sha256') == digest and old.get('version') == VERSION:
            if not quiet:
                print(f'= {out.name}: cache is fresh', file=sys.stderr)
            return old
    doc = {'track': track.name, 'sha256': digest, **analyze_signal(load_mono(track))}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    if not quiet:
        o = doc['onsets']
        print(f'+ {out.name}: {doc["bpm"]} BPM, {len(doc["beats"])} beats, {len(doc["sections"])} sections, '
              f'kick {len(o["kick"])} snare {len(o["snare"])} hat {len(o["hat"])}, '
              f'confidence {doc["quality"]["beat_confidence"]:.2f}, phase {doc["quality"]["downbeat_margin"]:.3f}',
              file=sys.stderr)
    return doc


def load_feats(arg, quiet=False):
    """A `.feats.json` file as is, or a track (analysed or read from its cache)."""
    p = Path(arg)
    if p.name.endswith('.feats.json') or p.suffix == '.json':
        return json.loads(p.read_text(encoding='utf-8'))
    return analyze(p, quiet=quiet)


# ------------------------------------------------------------------ video time
def to_video(doc, offset, duration):
    """Slice the map to the video window [0, duration] and shift by offset (t_video = t_track - offset)."""
    a, b = offset, offset + duration

    def tw(xs):
        return [round(t - a, 3) for t in xs if a - 1 <= t <= b + 1]
    i0, i1 = int(max(0, a) * FPS), int(math.ceil(b * FPS)) + 1
    return {
        'track': doc.get('track', ''), 'offset': offset, 'duration': duration, 'bpm': doc['bpm'], 'fps': FPS,
        'beats': tw(doc['beats']), 'downbeats': tw(doc['downbeats']),
        'sections': [{**s, 'start': round(max(s['start'], a) - a, 3), 'end': round(min(s['end'], b) - a, 3)}
                     for s in doc['sections'] if s['end'] > a and s['start'] < b],
        'env': {k: v[i0:i1] for k, v in doc['env'].items()},
        'onsets': {k: [[round(t - a, 3), s] for t, s in v if a <= t <= b] for k, v in doc['onsets'].items()},
        'quality': doc['quality'],
    }


def export_js(v, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('// audio_feats.py export: track feature map in video time. Generated, do not edit.\n'
                   'window.__AUDIO_FEATS=' + json.dumps(v, ensure_ascii=False, separators=(',', ':')) + ';\n',
                   encoding='utf-8')
    return out


# ------------------------------------------------------------------ cut proposals
def grid_times(v, grid='beat'):
    b = np.asarray(v['beats'], float)
    if grid == 'downbeat':
        return np.asarray(v['downbeats'], float)
    if grid == 'half' and len(b) > 1:
        return np.sort(np.concatenate([b, (b[:-1] + b[1:]) / 2]))
    return b


def cut_before_word(grid, t_word, tol=.02, max_lead=.6):
    """The last beat no later than the phrase's first word.

    tol: a beat up to 20 ms after the word still counts as "on the word". When the nearest earlier beat is more
    than max_lead before the word, the cut is not moved: returns (t_word, False).
    """
    g = np.asarray(grid, float)
    g = g[g <= t_word + tol]
    if not len(g) or t_word - g[-1] > max_lead:
        return round(t_word, 3), False
    return round(float(g[-1]), 3), True


def phrase_starts(data):
    """First word of every phrase from common timing formats.

    Accepts: Whisper JSON {"segments": [{"start", "text", "words": [{"word", "start"}]}]}; a list of phrases
    [{"text"|"word", "start"|"t"}]; or ASR word triples [[word, start, end], ...] (every word is a phrase then).
    Returns [(index, word, t)].
    """
    if isinstance(data, dict) and 'segments' in data:
        out = []
        for i, s in enumerate(data['segments']):
            w = (s.get('words') or [{}])[0]
            word = (w.get('word') or s.get('text') or '').strip().split(' ')[0]
            out.append((i, word, float(w.get('start', s['start']))))
        return out
    if isinstance(data, dict):
        for key in ('cues', 'lines', 'phrases', 'words'):
            if isinstance(data.get(key), list):
                return phrase_starts(data[key])
    out = []
    for i, x in enumerate(data or []):
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            out.append((i, str(x[0]).strip(), float(x[1])))
        elif isinstance(x, dict):
            t = x.get('start', x.get('t', x.get('t0')))
            if t is None and x.get('words'):
                t = x['words'][0].get('start', x['words'][0].get('t0'))
            if t is None:
                continue
            word = str(x.get('word') or x.get('text') or x.get('w') or '').strip().split(' ')[0]
            out.append((i, word, float(t)))
    return out


def propose_cuts(v, starts, grid='beat', tol=.02, max_lead=.6):
    g = grid_times(v, grid)
    rows = []
    for i, word, t in starts:
        c, moved = cut_before_word(g, t, tol, max_lead)
        rows.append({'phrase': i, 'word': word, 'word_t': round(t, 3), 'cut': c, 'lead': round(t - c, 3),
                     'snapped': moved})
    return {'grid': grid, 'tol': tol, 'max_lead': max_lead, 'applied': False,
            'note': 'Proposal only. Cuts on the beat are optional; take them where the edit asks for a hit.',
            'beat_confidence': v['quality']['beat_confidence'], 'cuts': rows}


def summary(d):
    lines = [f"{d.get('track', '')}: {d['duration']} s, {d['bpm']} BPM, beats {len(d['beats'])}, "
             f"downbeats {len(d['downbeats'])}, quality {d['quality']}"]
    lines += [f"  {s['name']:>3} {s['start']:7.2f}-{s['end']:7.2f} {s['energy']}" for s in d['sections']]
    lines += [f'  {k}: {len(v)} hits, {len(v) / max(d["duration"], 1e-9) * 60:.0f} per minute'
              for k, v in d['onsets'].items()]
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Track feature map: beats, downbeats, sections, drum hits, envelopes.')
    sp = ap.add_subparsers(dest='cmd', required=True)
    a = sp.add_parser('analyze', help='analyse tracks, cache next to each as <name>.feats.json')
    a.add_argument('tracks', nargs='+')
    a.add_argument('--out', help='cache path (only with one track)')
    a.add_argument('--force', action='store_true')
    s = sp.add_parser('show', help='summary of a track or a .feats.json')
    s.add_argument('track')
    e = sp.add_parser('export', help='write window.__AUDIO_FEATS in video time for audio-feats.js')
    c = sp.add_parser('cuts', help='propose cuts on the last beat before each phrase (writes JSON only)')
    for p in (e, c):
        p.add_argument('track', help='track or its .feats.json')
        p.add_argument('--offset', type=float, default=0.0, help='track second where the video starts')
        p.add_argument('--duration', type=float, help='video length, s (default: rest of the track)')
        p.add_argument('--out', required=True)
    c.add_argument('--words', required=True, help='Whisper JSON, list of phrases with start, or [[word,start,end]]')
    c.add_argument('--grid', choices=['beat', 'half', 'downbeat'], default='beat')
    c.add_argument('--tol', type=float, default=.02)
    c.add_argument('--max-lead', type=float, default=.6)
    o = ap.parse_args(argv)
    try:
        if o.cmd == 'analyze':
            if o.out and len(o.tracks) > 1:
                ap.error('--out works with one track only')
            for t in o.tracks:
                analyze(t, o.out, o.force)
        elif o.cmd == 'show':
            print(summary(load_feats(o.track)))
        else:
            d = load_feats(o.track, quiet=True)
            dur = o.duration if o.duration else max(0.0, d['duration'] - o.offset)
            v = to_video(d, o.offset, dur)
            if o.cmd == 'export':
                out = export_js(v, o.out)
                print(f'{out}: {len(v["beats"])} beats, kick {len(v["onsets"]["kick"])}, {dur} s from {o.offset} s')
            else:
                doc = propose_cuts(v, phrase_starts(json.loads(Path(o.words).read_text(encoding='utf-8'))),
                                   o.grid, o.tol, o.max_lead)
                Path(o.out).parent.mkdir(parents=True, exist_ok=True)
                Path(o.out).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
                n = sum(r['snapped'] for r in doc['cuts'])
                if doc['beat_confidence'] < 1.3:
                    print(f'! beat confidence {doc["beat_confidence"]}: weak rhythm, proposals are rough')
                print(f'{n} of {len(doc["cuts"])} phrases have a beat <= {o.max_lead} s before the first word -> {o.out}')
    except ImportError as err:
        print(f'missing dependency: {err}. Install: pip install librosa', file=sys.stderr)
        return 1
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        print(f'cannot read the track: {err}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
