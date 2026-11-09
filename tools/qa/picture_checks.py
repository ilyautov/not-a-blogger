#!/usr/bin/env python3
"""Two picture checks on any mp4: motion in the first 2 seconds (hook) and single-frame flashes (pops).

Idea after scripts/qc.py (hook) and scripts/scene_check.py (pops) from sarpstar/cinecode (MIT, (c) 2026 Sarp
Yıldız); the code is written from scratch on numpy.

  hook   The first 2 s should move from the first frame. Mean |Δ| of neighbouring frames (160 px wide, grey,
         0..255) must be >= 0.5, and every pair of steps must reach at least 0.02 (cinecode: grain on a still
         frame is 0.2-0.3, obvious motion 0.8-5). Also reports how long the video stands still from the start.
  pops   Single-frame flashes and blinks: frame n differs from both neighbours (>= 4 of 255, 48 px wide, every
         frame) while the neighbours are similar to each other (their difference < 0.35 of that step).

Both are WARNINGS. On 20 videos with human verdicts the hook check failed three approved word-by-word text
reels and passed rejected ones, and every pop it found in approved videos was an intended effect (a pulse, a
shake, film flicker). See recipes/qa/qa-picture-checks-warn-only.md. Exit code 0 unless --strict is given.

Input: an mp4 (anything ffmpeg reads). Output: JSON on stdout (or --json file).
Exit codes: 0; with --strict 2 when a check warns; 1 when the file cannot be read or ffmpeg is missing.

Example:
  python3 tools/qa/picture_checks.py output/final.mp4
  python3 tools/qa/picture_checks.py output/final.mp4 --limit 30 --json qa/picture.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or shutil.which('ffprobe') or 'ffprobe'

HOOK_S = 2.0
HOOK_MEAN = 0.5
HOOK_LOW = 0.02
POP_STEP = 4.0
POP_SKIP = 0.35


def gray_frames(video, width, seconds=None):
    """All frames at the native rate, grey, `width` px wide: (frames float32 (n, h, w), fps)."""
    info = json.loads(subprocess.check_output([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                               'stream=width,height,r_frame_rate', '-of', 'json', str(video)]))
    info = info['streams'][0]
    num, _, den = info['r_frame_rate'].partition('/')
    fps = float(num) / float(den or 1)
    h = max(2, int(round(width * int(info['height']) / int(info['width']) / 2) * 2))
    cmd = [FFMPEG, '-v', 'error', '-nostdin'] + (['-t', str(seconds)] if seconds else [])
    cmd += ['-i', str(video), '-an', '-vf', f'scale={width}:{h}:flags=area,format=gray', '-f', 'rawvideo', '-']
    raw = subprocess.check_output(cmd)
    n = len(raw) // (width * h)
    return np.frombuffer(raw[:n * width * h], np.uint8).reshape(n, h, width).astype(np.float32), fps


def hook_stats(F, fps, min_mean=HOOK_MEAN, min_low=HOOK_LOW):
    """Hook check on already decoded frames of the first seconds."""
    if len(F) < 3:
        return {'ok': False, 'steps': 0, 'mean': 0.0, 'low': 0.0, 'first_step': 0.0, 'note': 'no frames'}
    v = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))
    low = float(min(max(v[i:i + 2]) for i in range(max(1, len(v) - 1))))
    mean = float(v.mean())
    still = next((i for i, x in enumerate(v) if x >= min_low), len(v))
    return {'ok': bool(mean >= min_mean and low >= min_low), 'steps': int(len(v)), 'mean': round(mean, 3),
            'low': round(low, 4), 'first_step': round(float(max(v[:2])), 3),
            'still_from_start_s': round(still / fps, 3), 'min_mean': min_mean, 'min_low': min_low}


def hook_motion(video, seconds=HOOK_S, min_mean=HOOK_MEAN, min_low=HOOK_LOW):
    F, fps = gray_frames(video, 160, seconds)
    return hook_stats(F, fps, min_mean, min_low)


def pop_stats(F, fps, step=POP_STEP, skip=POP_SKIP):
    """Pops on already decoded frames: frame n unlike both neighbours, neighbours alike."""
    if len(F) < 3:
        return {'ok': True, 'count': 0, 'pops': [], 'fps': fps, 'frames': int(len(F))}
    into = np.abs(F[1:-1] - F[:-2]).mean(axis=(1, 2))
    out = np.abs(F[2:] - F[1:-1]).mean(axis=(1, 2))
    across = np.abs(F[2:] - F[:-2]).mean(axis=(1, 2))
    m = np.minimum(into, out)
    hit = np.where((m >= step) & (across < skip * m))[0]
    pops = [{'frame': int(i + 1), 't': round((i + 1) / fps, 3), 'step': round(float(m[i]), 2)} for i in hit]
    return {'ok': not pops, 'count': len(pops), 'pops': pops[:50], 'fps': fps, 'frames': int(len(F)),
            'step': step, 'skip': skip}


def frame_pops(video, step=POP_STEP, skip=POP_SKIP, seconds=None):
    F, fps = gray_frames(video, 48, seconds)
    return pop_stats(F, fps, step, skip)


def picture_checks(video, seconds=None):
    r = {'hook_motion': hook_motion(video), 'frame_pops': frame_pops(video, seconds=seconds)}
    r['warnings'] = [k for k in ('hook_motion', 'frame_pops') if not r[k]['ok']]
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description='Hook motion in the first 2 s and single-frame flashes on any mp4 '
                                             '(warnings only).')
    ap.add_argument('video')
    ap.add_argument('--limit', type=float, help='pops: only the first N seconds')
    ap.add_argument('--json', help='write the JSON report to this file as well')
    ap.add_argument('--strict', action='store_true', help='exit 2 when a check warns (not recommended as a gate)')
    a = ap.parse_args(argv)
    if not Path(a.video).exists():
        print(f'no such file: {a.video}', file=sys.stderr)
        return 1
    try:
        r = {'file': os.path.basename(a.video), **picture_checks(a.video, a.limit)}
    except FileNotFoundError as e:
        print(f'ffmpeg/ffprobe not found: {e}', file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f'cannot read {a.video}: {e}', file=sys.stderr)
        return 1
    out = json.dumps(r, ensure_ascii=False, indent=2)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(out + '\n', encoding='utf-8')
    print(out)
    return 2 if a.strict and r['warnings'] else 0


if __name__ == '__main__':
    sys.exit(main())
