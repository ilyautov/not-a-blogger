#!/usr/bin/env python3
"""Per-second map of a reference video for a remake: shots, motion inside shots, beat grid, frame sheets.

Input is a file you already have on disk. Do not reupload or republish someone else's video: the
breakdown exists so that you can rebuild the rhythm with your own footage, words and means. Keep the
output folder out of public repositories as well (it contains frames of the reference).

Idea after analyze/breakdown.py from alchaincyf/huashu-art-motion (MIT, (c) 2026 alchaincyf); the code
is written from scratch. Cuts come from two detectors: ffmpeg `scdet` and the frame-difference detector
of `motion_gate.py` next to this file (cuts closer than 0.15 s are merged). Motion inside shots is the
same d = mean |ΔI| at 12 fps / 320 px as in motion_gate, so `fast_ratio` values are comparable. The beat
grid comes from librosa on the percussive part of the sound track; librosa is optional, without it the
beat grid is skipped and the report says so.

Output (in --out, default `<video folder>/breakdown/`):
  breakdown.md / breakdown.json  shots (start, length, fast share, moving area, cut-to-beat residual),
                                 tempo, summary; with --compare a table "reference vs remake";
  sheet.jpg      frames at 2 fps with time stamps (sheet-N.jpg when longer than 24 s);
  keys.jpg       middle frame of every shot: composition reference for the remake;
  heat.jpg       motion heat map per shot (red = pixels that changed) with the moving area in %;
  timeline.png   strip: cuts, beats, motion curve (two strips with --compare).
`--no-images` writes only the Markdown and JSON. `--compare our.mp4` runs the same analysis on the remake
and prints both side by side plus the nearest remake cut for every reference cut; remake images go to
`compare/`. Exit codes: 0; 1 when a file cannot be read or ffmpeg is missing.

Example:
  python3 tools/qa/breakdown.py ref.mp4 --out qa/breakdown --compare output/final.mp4
  python3 tools/qa/breakdown.py ref.mp4 --no-images --scdet-thr 5      # 5 on dark motion graphics, 8 default
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motion_gate import FAST, decode, measure  # noqa: E402

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or shutil.which('ffprobe') or 'ffprobe'

FPS = 12
TW = 320          # analysis width: the same as motion_gate so that fast_ratio matches
MERGE = 0.15      # cuts from the two detectors closer than this are one cut
SHEET_FPS = 2
SHEET_COLS, SHEET_PER_IMAGE = 8, 48


def font(size=16):
    try:
        return ImageFont.load_default(size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def scdet(path, thr):
    """Cut times from ffmpeg scdet."""
    p = subprocess.run([FFMPEG, '-hide_banner', '-nostats', '-i', path, '-an', '-vf',
                        f'scale={TW}:-2,scdet=threshold={thr}', '-f', 'null', '-'], capture_output=True, text=True)
    out = []
    for line in p.stderr.splitlines():
        if 'lavfi.scd.time' in line:
            try:
                out.append(float(line.split('lavfi.scd.time:')[1].split()[0]))
            except (IndexError, ValueError):
                pass
    return sorted(out)


def audio_beats(path):
    """BPM and beat times from the sound track; None without librosa, without sound or without a rhythm."""
    try:
        import librosa
    except ImportError:
        return None
    raw = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', '22050', '-f', 'f32le', '-'],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.float32)
    if len(y) < 22050 * 3 or float(np.abs(y).max()) < 1e-4:
        return None
    yp = librosa.effects.percussive(y, margin=2.0)       # percussive part, so speech does not pull the tempo
    onset = librosa.onset.onset_strength(y=yp, sr=22050)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=22050, units='time')
    tempo = float(np.atleast_1d(tempo)[0])
    if len(beats) < 4 or tempo <= 0:
        return None
    return {'bpm': round(tempo, 1), 'beats': [round(float(b), 3) for b in beats]}


def has_librosa():
    try:
        import librosa  # noqa: F401
        return True
    except ImportError:
        return False


def beat_fit(cuts, beats):
    """How well cuts sit on the beat grid: residual to the nearest beat and half beat, share within ±1 frame at 30 fps."""
    if not beats or not cuts:
        return None
    b = np.array(beats)
    step = float(np.median(np.diff(b)))
    half = np.sort(np.concatenate([b, b[:-1] + np.diff(b) / 2]))
    res = []
    for c in cuts:
        r1 = float(c - b[np.argmin(np.abs(b - c))])
        r2 = float(c - half[np.argmin(np.abs(half - c))])
        res.append((round(r1 * 1000), round(r2 * 1000)))
    tol = 1000 / 30 + 1
    on_beat = sum(abs(r1) <= tol for r1, _ in res) / len(res)
    on_half = sum(abs(r2) <= tol for _, r2 in res) / len(res)
    chance = min(1.0, 2 * tol / 1000 / (step / 2))      # a random cut lands within ±tol of a half beat this often
    return {'beat_step_s': round(step, 3), 'residual_ms': res, 'on_beat_share': round(on_beat, 2),
            'on_half_beat_share': round(on_half, 2), 'chance_half_beat': round(chance, 2),
            'median_abs_ms_half': int(np.median([abs(r2) for _, r2 in res]))}


def merge_cuts(a, b):
    """Merge scdet cuts `a` and frame-difference cuts `b` into [(time, source)]."""
    allc = sorted([(t, 'scdet') for t in a] + [(t, 'diff') for t in b])
    out = []
    for t, src in allc:
        if out and t - out[-1][0] < MERGE:
            out[-1] = (out[-1][0], out[-1][1] if src in out[-1][1] else out[-1][1] + '+' + src)
        else:
            out.append((t, src))
    return out


def run(path, scdet_thr=8.0):
    """Full analysis of one video: summary, shots (with private _heat/_mid), cuts, beat, frames, d."""
    F, (W, H, dur) = decode(path, fps=FPS, width=TW)
    if len(F) < 4:
        raise ValueError('too few frames (need ≥ 4)')
    d, first, inside = measure(F)
    diff_cuts = [round((i + 1) / FPS, 3) for i in np.where(first)[0]]
    sc = [round(t, 3) for t in scdet(path, scdet_thr)]
    cuts = [(t, s) for t, s in merge_cuts(sc, diff_cuts) if 0.2 < t < dur - 0.1]
    beat = audio_beats(path)
    bounds = [0.0] + [t for t, _ in cuts] + [dur]
    shots = []
    for k, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])):
        fa, fb = int(round(a * FPS)), int(round(b * FPS))
        seg_d = d[fa:max(fa, fb - 1)]
        seg_in = inside[fa:max(fa, fb - 1)]
        mv = seg_d[seg_in] if len(seg_d) else np.array([])
        s0 = min(fa + int(0.25 * FPS) if k else fa, max(fa, fb - 3))   # skip the cut tail
        sub = F[s0:fb].astype(np.int16)
        if len(sub) >= 3:
            dd = np.abs(np.diff(sub, axis=0))
            heat = dd.max(axis=0)
            area = float((heat > 25).mean())
            area_mean = float((dd.mean(axis=0) > 4).mean())
        else:
            heat, area, area_mean = np.zeros(F.shape[1:], np.int16), 0.0, 0.0
        shots.append({'i': k + 1, 'start': round(a, 2), 'end': round(b, 2), 'dur': round(b - a, 2),
                      'cut_src': cuts[k - 1][1] if k else 'start',
                      'fast': round(float((mv >= FAST).mean()), 3) if len(mv) else 0.0,
                      'median_d': round(float(np.median(mv)), 2) if len(mv) else 0.0,
                      'area_any': round(area, 3), 'area_steady': round(area_mean, 3),
                      '_heat': heat, '_mid': min(len(F) - 1, (fa + fb) // 2)})
    fit = beat_fit([t for t, _ in cuts], beat['beats'] if beat else None)
    durs = np.array([s['dur'] for s in shots])
    mvv = d[inside]
    summary = {'file': os.path.basename(path), 'size': [W, H], 'duration': round(dur, 2), 'shots': len(shots),
               'cuts_per_10s': round(len(cuts) / dur * 10, 2) if dur else 0.0,
               'shot_mean_s': round(float(durs.mean()), 2), 'shot_median_s': round(float(np.median(durs)), 2),
               'shot_max_s': round(float(durs.max()), 2),
               'fast_ratio': round(float((mvv >= FAST).mean()), 4) if len(mvv) else 0.0,
               'area_any_mean': round(float(np.mean([s['area_any'] for s in shots])), 3),
               'bpm': beat['bpm'] if beat else None, 'beat_fit': fit, 'beat_grid': has_librosa(),
               'cuts_scdet': len(sc), 'cuts_diff': len(diff_cuts)}
    return {'summary': summary, 'shots': shots, 'cuts': cuts, 'beat': beat, 'F': F, 'd': d}


# ---------------------------------------------------------------- images
def label(im, text, size=16, fill=(255, 255, 0)):
    dr = ImageDraw.Draw(im)
    f = font(size)
    dr.rectangle([0, 0, dr.textlength(text, font=f) + 8, size + 6], fill=(0, 0, 0))
    dr.text((4, 2), text, fill=fill, font=f)
    return im


def grid(ims, cols):
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * h), 'white')
    for i, im in enumerate(ims):
        S.paste(im, ((i % cols) * w, (i // cols) * h))
    return S


def frame_rgb(path, ts):
    """One RGB frame per time stamp, TW wide."""
    out = []
    for t in ts:
        raw = subprocess.run([FFMPEG, '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-vf',
                              f'scale={TW}:-2', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        try:
            out.append(Image.open(io.BytesIO(raw)).convert('RGB'))
        except (OSError, ValueError):
            out.append(Image.new('RGB', (TW, TW * 16 // 9), 'gray'))
    return out


def images(r, path, out):
    dur = r['summary']['duration']
    ts = list(np.arange(0, dur, 1 / SHEET_FPS))
    sheet = [label(im, f'{t:.1f}s') for im, t in zip(frame_rgb(path, ts), ts)]
    for k in range(0, len(sheet), SHEET_PER_IMAGE):
        name = f'sheet-{k // SHEET_PER_IMAGE + 1}.jpg' if len(sheet) > SHEET_PER_IMAGE else 'sheet.jpg'
        grid(sheet[k:k + SHEET_PER_IMAGE], SHEET_COLS).save(os.path.join(out, name), quality=82)
    mids = [(sh['start'] + sh['end']) / 2 for sh in r['shots']]
    keys = [label(im, f'#{sh["i"]} {sh["start"]:.1f}-{sh["end"]:.1f}s') for im, sh in zip(frame_rgb(path, mids), r['shots'])]
    grid(keys, 6).save(os.path.join(out, 'keys.jpg'), quality=85)
    heats = []
    for sh in r['shots']:
        base = Image.fromarray(r['F'][sh['_mid']]).convert('RGB')
        hm = np.zeros((*sh['_heat'].shape, 3), np.uint8)
        hm[..., 0] = np.clip(sh['_heat'].astype(np.int32) * 4, 0, 255)
        im = Image.blend(base, Image.fromarray(hm), 0.55)
        heats.append(label(im, f'#{sh["i"]} {sh["dur"]:.1f}s · {sh["area_any"] * 100:.0f}% · fast {sh["fast"]:.2f}'))
    grid(heats, 6).save(os.path.join(out, 'heat.jpg'), quality=85)


def strip(r, W, dur_max, title):
    H = 150
    im = Image.new('RGB', (W, H), (250, 249, 245))
    dr = ImageDraw.Draw(im)
    f = font(14)

    def x(t):
        return int(t / dur_max * (W - 20)) + 10

    dr.text((10, 4), title, fill=(26, 32, 35), font=f)
    if r['beat']:
        for i, b in enumerate(r['beat']['beats']):
            dr.line([x(b), 24, x(b), 60], fill=(200, 200, 200) if i % 4 else (140, 140, 140), width=1)
    for t, src in r['cuts']:
        dr.line([x(t), 22, x(t), 64], fill=(214, 60, 60) if 'scdet' in src else (230, 140, 60), width=3)
    ys = np.clip(r['d'] / 30, 0, 1)
    pts = [(x(i / FPS), 140 - int(v * 70)) for i, v in enumerate(ys)]
    y_fast = 140 - int(FAST / 30 * 70)
    dr.line([(10, y_fast), (W - 10, y_fast)], fill=(200, 220, 120), width=1)
    if len(pts) > 1:
        dr.line(pts, fill=(26, 32, 35), width=1)
    for s in range(0, int(dur_max) + 1, 5):
        dr.text((x(s) - 4, 64), f'{s}', fill=(120, 120, 120), font=f)
    return im


# ---------------------------------------------------------------- report
def md_table(r):
    fit = r['summary']['beat_fit']
    res = {i + 1: fit['residual_ms'][i] for i in range(len(fit['residual_ms']))} if fit else {}
    L = ['| # | start | end | s | cut by | fast | moving area | residual to beat / half beat, ms |',
         '|---|---|---|---|---|---|---|---|']
    for sh in r['shots']:
        rr = res.get(sh['i'] - 1)
        L.append(f'| {sh["i"]} | {sh["start"]:.2f} | {sh["end"]:.2f} | {sh["dur"]:.2f} | {sh["cut_src"]} | {sh["fast"]:.2f} | '
                 f'{sh["area_any"] * 100:.0f}% (steady {sh["area_steady"] * 100:.0f}%) | '
                 f'{f"{rr[0]:+d} / {rr[1]:+d}" if rr else "-"} |')
    return L


def summary_lines(s):
    fit = s['beat_fit']
    L = [f'- {s["size"][0]}×{s["size"][1]}, {s["duration"]} s; {s["shots"]} shots, {s["cuts_per_10s"]} cuts per 10 s; '
         f'mean shot {s["shot_mean_s"]} s (median {s["shot_median_s"]}, longest {s["shot_max_s"]})',
         f'- cuts: scdet {s["cuts_scdet"]}, frame-difference detector {s["cuts_diff"]} (merged, closer than {MERGE} s = one)',
         f'- motion inside shots: fast_ratio {s["fast_ratio"]:.3f} (same metric as motion_gate.py), '
         f'mean moving area {s["area_any_mean"] * 100:.0f}%']
    if s['bpm']:
        L.append(f'- music ≈ {s["bpm"]} BPM (beat {fit["beat_step_s"] if fit else "?"} s)' + (
            f'; cuts on a beat ±1 frame: {fit["on_beat_share"] * 100:.0f}%, on a half beat: {fit["on_half_beat_share"] * 100:.0f}% '
            f'(chance would be ≈{fit["chance_half_beat"] * 100:.0f}%), median residual to a half beat {fit["median_abs_ms_half"]} ms'
            if fit else ''))
    elif not s['beat_grid']:
        L.append('- beat grid skipped: librosa is not installed (pip install librosa)')
    else:
        L.append('- no beat found in the sound (no music, too quiet, or librosa is unsure)')
    return L


def compare_table(a, b, na, nb):
    sa, sb = a['summary'], b['summary']
    rows = [('duration, s', 'duration'), ('shots', 'shots'), ('cuts per 10 s', 'cuts_per_10s'),
            ('shot mean, s', 'shot_mean_s'), ('shot median, s', 'shot_median_s'), ('longest shot, s', 'shot_max_s'),
            ('fast_ratio', 'fast_ratio'), ('moving area, share', 'area_any_mean'), ('BPM', 'bpm')]
    L = [f'| | {na} | {nb} |', '|---|---|---|']
    for name, k in rows:
        L.append(f'| {name} | {sa.get(k)} | {sb.get(k)} |')
    fa, fb = sa['beat_fit'], sb['beat_fit']
    L.append(f'| cuts on a half beat | {fa["on_half_beat_share"] if fa else "-"} | {fb["on_half_beat_share"] if fb else "-"} |')
    L += ['', f'Cuts in time ({na} → nearest in {nb}, Δ s):', '']
    cb = np.array([t for t, _ in b['cuts']]) if b['cuts'] else np.array([])
    row = []
    for t, _ in a['cuts']:
        if len(cb):
            j = int(np.argmin(np.abs(cb - t)))
            row.append(f'{t:.2f}→{cb[j]:.2f} ({cb[j] - t:+.2f})')
    L.append(', '.join(row) or '-')
    return L


def public(r):
    """JSON-safe part of a run() result."""
    return {**r['summary'], 'shot_count': r['summary']['shots'], 'cuts': r['cuts'],
            'shots': [{k: v for k, v in s.items() if not k.startswith('_')} for s in r['shots']],
            'beats': r['beat']['beats'] if r['beat'] else None}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Per-second map of a reference video: cuts, beat, motion, frame sheets.')
    ap.add_argument('video', help='reference video you already have on disk')
    ap.add_argument('--compare', help='second video (your remake) for a side-by-side table')
    ap.add_argument('--out', help='output folder (default: <video folder>/breakdown)')
    ap.add_argument('--scdet-thr', type=float, default=8.0, help='ffmpeg scdet threshold (8; 5 on dark motion graphics)')
    ap.add_argument('--no-images', action='store_true', help='only breakdown.md and breakdown.json')
    a = ap.parse_args(argv)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.video)), 'breakdown')
    if not (shutil.which(FFMPEG) and shutil.which(FFPROBE)):
        print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
        return 1
    try:
        r = run(a.video, a.scdet_thr)
        r2 = run(a.compare, a.scdet_thr) if a.compare else None
    except FileNotFoundError as e:
        if e.filename in (FFMPEG, FFPROBE):
            print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
        else:
            print(f'cannot read {e.filename}', file=sys.stderr)
        return 1
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f'cannot analyse: {e}', file=sys.stderr)
        return 1
    os.makedirs(out, exist_ok=True)
    name, L = r['summary']['file'], []
    L += [f'# Breakdown: {name}', '', *summary_lines(r['summary']), '', '## Shots', '', *md_table(r)]
    js = {'reference': public(r)}
    strips = [strip(r, 1600, r['summary']['duration'], name)]
    if r2:
        na, nb = 'reference', 'remake'
        L += ['', f'## Compared with {r2["summary"]["file"]}', '', *summary_lines(r2['summary']), '',
              *compare_table(r, r2, na, nb), '', '### Remake shots', '', *md_table(r2)]
        js['compare'] = public(r2)
        dm = max(r['summary']['duration'], r2['summary']['duration'])
        strips = [strip(r, 1600, dm, f'{na} {name}'), strip(r2, 1600, dm, f'{nb} {r2["summary"]["file"]}')]
        if not a.no_images:
            os.makedirs(os.path.join(out, 'compare'), exist_ok=True)
            images(r2, a.compare, os.path.join(out, 'compare'))
    L += ['', 'Files: sheet.jpg (2 fps), keys.jpg (middle of every shot), heat.jpg (motion inside the shot), timeline.png '
          '(red = scdet cuts, orange = frame-difference cuts only, grey = beats, curve = frame difference, '
          'green line = "fast" threshold).' + (' Remake images in compare/.' if r2 else ''),
          '', 'Moving area = share of pixels that changed by more than 25/255 at least once within the shot; '
          '"steady" = more than 4/255 per frame on average.',
          '', 'The reference stays on your disk: rebuild its rhythm with your own footage, do not republish it.']
    if not a.no_images:
        images(r, a.video, out)
        T = Image.new('RGB', (1600, 150 * len(strips)), 'white')
        for i, s in enumerate(strips):
            T.paste(s, (0, 150 * i))
        T.save(os.path.join(out, 'timeline.png'))
    with open(os.path.join(out, 'breakdown.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    with open(os.path.join(out, 'breakdown.json'), 'w', encoding='utf-8') as f:
        json.dump(js, f, ensure_ascii=False, indent=1)
    print('\n'.join(L[:8]))
    print(f'-> {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
