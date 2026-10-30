#!/usr/bin/env python3
"""Share of fast motion inside shots, measured on the finished mp4.

What it is NOT: a quality gate. Calibration on 18 of the author's videos with human verdicts
(approved / rejected / mixed) showed that neither `fast_ratio` nor `active_ratio` separates the
approved videos from the rejected ones: rejected videos moved as much as approved ones, and the
best-received long-form was nearly as still as the worst one. The tool is a hint (numbers per shot,
dead shots, worst window) plus ONE alarm: "dead as a slide deck", `active_ratio` below --dead.
That alarm rests on a single negative example; read it as "go and look", not as a verdict.
Meaning, voice and rhythm are judged by a person.

Method (idea after film_gate.py from alchaincyf/huashu-art-motion, MIT, (c) 2026 alchaincyf; the code
here is written from scratch):
  * frames at 12 fps, grey, 320 px wide; d = mean |ΔI| between neighbouring frames (0–255);
  * cuts are removed: a spike of d over its neighbours that camera motion does not explain
    (similarity transform from LK optical flow + RANSAC; if the frame still differs after
    compensation, it is a cut). Without OpenCV every spike counts as a cut;
  * fast_ratio = share of frame pairs inside shots with d ≥ --fast (default 9): "something visibly
    moves right now". A slow push 1.00→1.06 over 5 s gives d ≈ 1–2 and does not count;
  * active_ratio = share of frame pairs inside shots where ≥ 1 % of the frame changed by > 20/255;
  * worst 30-second window by fast_ratio, dead shots (≥ 2 s without a single fast frame).
Stillness is deliberately not an alarm: "stop → jump → stop" is a good rhythm.

Input: a video file. Output: Markdown summary in stdout, full report with --json / --md.
`--limit N` analyses the first N seconds, `--mask 0.86,1.0` excludes a horizontal band (fractions of
height, e.g. captions). `--calib <tsv>` runs a set of videos with your own verdicts and prints whether
the metric separates them: rows `path<TAB>verdict[<TAB>note[<TAB>limit_s]]`, verdicts `good` / `bad` /
anything else, paths relative to the TSV file.
Exit codes: 0; 2 only for the "dead" alarm; 1 when the file cannot be read or ffmpeg is missing.

Example:
  python3 tools/qa/motion_gate.py output/final.mp4 --json qa/motion.json --md qa/motion.md
  python3 tools/qa/motion_gate.py long.mp4 --limit 240 --mask 0.86,1.0
  python3 tools/qa/motion_gate.py --calib my-verdicts.tsv
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

try:
    import cv2
except ImportError:  # camera compensation off: every spike counts as a cut
    cv2 = None

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or shutil.which('ffprobe') or 'ffprobe'

FPS = 12
WIDTH = 320
FAST = 9.0          # "fast" frame threshold; 6–12 give the same ordering on the calibration set
STILL = 0.3
DEAD_ACTIVE = 0.10  # alarm threshold: the one rejected-as-static video had 0.078, the nearest approved one 0.161
ACTIVE_PX = 20      # a pixel "moves" when |Δ| > 20/255
ACTIVE_AREA = 0.01  # a frame pair is "alive" when ≥ 1 % of the frame moves
WINDOW_S = 30


def probe(path):
    """Return (width, height, duration_s)."""
    r = subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height:format=duration', '-of', 'json', path],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    s = j['streams'][0]
    return int(s['width']), int(s['height']), float(j['format'].get('duration') or 0)


def decode(path, fps=FPS, width=WIDTH, limit=None, start=0.0):
    """Grey frames (n, h, width) at `fps`, plus (orig_w, orig_h, duration)."""
    W, H, dur = probe(path)
    h = max(2, int(round(H * width / W / 2) * 2))
    cmd = [FFMPEG, '-v', 'error']
    if start:
        cmd += ['-ss', str(start)]
    if limit:
        cmd += ['-t', str(limit)]
    cmd += ['-i', path, '-an', '-vf', f'fps={fps},scale={width}:{h}:flags=area', '-pix_fmt', 'gray',
            '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (width * h)
    return np.frombuffer(raw[:n * width * h], np.uint8).reshape(n, h, width), (W, H, dur)


def camera_residual(a, b):
    """Mean difference after compensating camera motion (shift + scale + rotation). None = cannot estimate."""
    if cv2 is None:
        return None
    pts = cv2.goodFeaturesToTrack(a, maxCorners=250, qualityLevel=0.01, minDistance=6, blockSize=5)
    if pts is None or len(pts) < 15:
        return None
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(a, b, pts, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    if ok.sum() < 12:
        return None
    M, inl = cv2.estimateAffinePartial2D(pts[ok].reshape(-1, 2), nxt[ok].reshape(-1, 2), method=cv2.RANSAC,
                                         ransacReprojThreshold=1.0)
    if M is None or inl.sum() < 20 or inl.sum() / len(pts) < 0.35:
        return None
    w = cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return float(np.abs(b.astype(np.int16) - w.astype(np.int16)).mean())


def measure(F):
    """Return d (neighbour difference), first (pair i starts a cut), inside (pair lies inside a shot)."""
    n = len(F)
    d = np.abs(np.diff(F.astype(np.int16), axis=0)).mean(axis=(1, 2))
    cut = np.zeros(n - 1, bool)
    for i in range(n - 1):
        nb = np.concatenate([d[max(0, i - 6):i], d[i + 1:i + 7]])
        med = float(np.median(nb)) if len(nb) else 0.0
        if d[i] >= max(8.0, 3 * med + 2):
            r = camera_residual(F[i], F[i + 1])
            cut[i] = r is None or r >= 0.6 * d[i]
    first = cut & ~np.concatenate([[False], cut[:-1]])
    trans = cut.copy()              # ±1 pair around a cut (compression, transition blur)
    trans[1:] |= cut[:-1]
    trans[:-1] |= cut[1:]
    return d, first, ~trans


def verdict(active, dead=DEAD_ACTIVE):
    return 'dead' if active < dead else 'info'


def analyse(path, limit=None, mask=None, fast=FAST, fps=FPS, dead=DEAD_ACTIVE):
    F, (W0, H0, dur) = decode(path, fps=fps, limit=limit)
    n = len(F)
    if n < 4:
        raise ValueError('too few frames for the metric (need ≥ 4)')
    if mask:
        h = F.shape[1]
        y0, y1 = int(mask[0] * h), int(mask[1] * h)
        F = np.ascontiguousarray(np.concatenate([F[:, :y0], F[:, y1:]], axis=1))
    d, first, inside = measure(F)
    mv = d[inside]
    F16 = F.astype(np.int16)
    area = np.array([(np.abs(F16[i + 1] - F16[i]) > ACTIVE_PX).mean() for i in np.where(inside)[0]])
    active_ratio = float((area >= ACTIVE_AREA).mean()) if len(area) else 0.0
    fast_ratio = float((mv >= fast).mean()) if len(mv) else 0.0
    sens = {str(t): round(float((mv >= t).mean()), 4) if len(mv) else 0.0 for t in (6, 9, 12)}
    bounds = [0] + [i + 1 for i in np.where(first)[0]] + [n - 1]
    shots = []
    for s, e in zip(bounds[:-1], bounds[1:]):
        if e - s < 2:
            continue
        seg = d[s:e][inside[s:e]]
        shots.append({'start': round(s / fps, 2), 'end': round(e / fps, 2), 'dur': round((e - s) / fps, 2),
                      'fast': round(float((seg >= fast).mean()), 3) if len(seg) else 0.0,
                      'median_d': round(float(np.median(seg)), 2) if len(seg) else 0.0})
    dead_shots = [s for s in shots if s['dur'] >= 2 and s['fast'] == 0]
    dead_time = sum(s['dur'] for s in dead_shots)
    win = int(WINDOW_S * fps)
    worst = None
    if n - 1 > win:
        fm = ((d >= fast) & inside).astype(float)
        im = inside.astype(float)
        cs_f, cs_i = np.concatenate([[0], np.cumsum(fm)]), np.concatenate([[0], np.cumsum(im)])
        best = (2.0, 0)
        for a in range(0, n - 1 - win + 1, fps):
            k = (cs_f[a + win] - cs_f[a]) / max(cs_i[a + win] - cs_i[a], 1)
            best = min(best, (k, a))
        worst = {'start': round(best[1] / fps, 1), 'fast_ratio': round(float(best[0]), 4)}
    return {
        'file': os.path.basename(path), 'size': [W0, H0], 'duration': round(dur, 2), 'analyzed_s': round(n / fps, 1),
        'fast_threshold': fast, 'fast_ratio': round(fast_ratio, 4), 'fast_ratio_by_threshold': sens,
        'still_ratio': round(float((mv < STILL).mean()), 4) if len(mv) else 0.0,
        'median_d': round(float(np.median(mv)), 2) if len(mv) else 0.0,
        'cuts': int(first.sum()), 'cuts_per_10s': round(float(first.sum()) / (n / fps) * 10, 2),
        'shots': shots, 'dead_shots': len(dead_shots), 'dead_share': round(dead_time / (n / fps), 3),
        'active_ratio': round(active_ratio, 4), 'area_mean': round(float(area.mean()), 4) if len(area) else 0.0,
        'worst_30s': worst, 'dead_threshold': dead, 'verdict': verdict(active_ratio, dead),
        'camera_compensation': cv2 is not None,
    }


def report_md(r):
    L = [f'# motion_gate: {r["file"]}', '',
         ('- **DEAD as a slide deck**' if r['verdict'] == 'dead' else '- no "dead" alarm')
         + f' (active_ratio {r["active_ratio"]:.3f}, threshold {r["dead_threshold"]}; fast_ratio {r["fast_ratio"]:.3f}). '
         'There is no good/bad gate: on human verdicts the metric does not separate the groups.',
         f'- active_ratio = share of frame pairs inside shots where ≥ 1 % of the frame moves; '
         f'mean moving area {r["area_mean"] * 100:.1f}%',
         f'- analysed {r["analyzed_s"]} s of {r["duration"]} s, {r["size"][0]}×{r["size"][1]}'
         + ('' if r['camera_compensation'] else '; OpenCV missing, every spike counted as a cut'),
         f'- fast frames at threshold 6/9/12: {r["fast_ratio_by_threshold"]}',
         f'- cuts {r["cuts"]} ({r["cuts_per_10s"]} per 10 s), median d inside shots {r["median_d"]}',
         f'- dead shots (≥ 2 s without a fast frame): {r["dead_shots"]}, {r["dead_share"] * 100:.0f}% of runtime']
    if r['worst_30s']:
        L.append(f'- worst {WINDOW_S}-second window: from {r["worst_30s"]["start"]} s, fast_ratio {r["worst_30s"]["fast_ratio"]:.3f}')
    L += ['', '| # | start | end | s | fast | median d |', '|---|---|---|---|---|---|']
    for i, s in enumerate(r['shots'], 1):
        mark = ' !' if s['dur'] >= 2 and s['fast'] == 0 else ''
        L.append(f'| {i}{mark} | {s["start"]:.2f} | {s["end"]:.2f} | {s["dur"]:.2f} | {s["fast"]:.2f} | {s["median_d"]} |')
    L += ['', 'The metric sees only motion inside shots. Meaning, text and structure it does not see: green is not approval.']
    return '\n'.join(L) + '\n'


def read_calib(tsv):
    """Rows (path, verdict, note, limit) from a TSV; relative paths resolve against the TSV folder."""
    base = os.path.dirname(os.path.abspath(tsv))
    rows = []
    with open(tsv, encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 2:
                continue
            path = os.path.expanduser(parts[0])
            path = path if os.path.isabs(path) else os.path.join(base, path)
            note = parts[2] if len(parts) > 2 else ''
            lim = float(parts[3]) if len(parts) > 3 and parts[3].strip() else None
            rows.append((path, parts[1].strip(), note, lim))
    return rows


def calib_table(rows):
    """Markdown table for (verdict, name, note, report) rows plus a separation line per metric."""
    rows = sorted(rows, key=lambda x: x[3]['fast_ratio'])
    L = ['| verdict | video | fast_ratio (9) | at 6 / 12 | active_ratio | moving area | dead shots, % time | cuts/10 s |',
         '|---|---|---|---|---|---|---|---|']
    for label, name, note, r in rows:
        s = r['fast_ratio_by_threshold']
        L.append(f'| {label} {note} | {name} | {r["fast_ratio"]:.3f} | {s["6"]:.3f} / {s["12"]:.3f} | '
                 f'{r["active_ratio"]:.3f} | {r["area_mean"] * 100:.1f}% | {r["dead_share"] * 100:.0f} | {r["cuts_per_10s"]} |')
    for key in ('fast_ratio', 'active_ratio'):
        good = [r[key] for lab, _, _, r in rows if lab == 'good']
        bad = [r[key] for lab, _, _, r in rows if lab == 'bad']
        if good and bad:
            L.append(f'\n{key}: worst of good {min(good):.3f}, best of bad {max(bad):.3f}: '
                     + ('separates' if min(good) > max(bad) else 'does NOT separate'))
    return '\n'.join(L) + '\n'


def calib(tsv, a):
    rows = []
    for path, label, note, lim in read_calib(tsv):
        try:
            r = analyse(path, limit=lim or a.limit, mask=a.mask, fast=a.fast, dead=a.dead)
        except (OSError, ValueError, subprocess.CalledProcessError) as e:
            print(f'! {os.path.basename(path)}: {e}', file=sys.stderr)
            continue
        rows.append((label, r['file'], note, r))
        print(f'{label:5} {r["fast_ratio"]:.4f} active {r["active_ratio"]:.3f} dead {r["dead_share"]:.2f} '
              f'cuts/10s {r["cuts_per_10s"]}  {r["file"]}', flush=True)
    out = calib_table(rows)
    print(out)
    if a.md:
        write_text(a.md, out)
    if a.json:
        write_text(a.json, json.dumps([{'label': lab, 'note': note, **{k: v for k, v in r.items() if k != 'shots'}}
                                       for lab, _, note, r in rows], ensure_ascii=False, indent=1))
    return 0


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Share of fast motion inside shots on the finished mp4: a hint plus one alarm.')
    ap.add_argument('video', nargs='?', help='video file (omit with --calib)')
    ap.add_argument('--limit', type=float, help='analyse only the first N seconds')
    ap.add_argument('--mask', help='exclude a horizontal band, fractions of height "y0,y1" (e.g. 0.86,1.0 for captions)')
    ap.add_argument('--fast', type=float, default=FAST, help=f'd threshold for a "fast" frame pair ({FAST:g})')
    ap.add_argument('--dead', type=float, default=DEAD_ACTIVE, help=f'alarm when active_ratio is below ({DEAD_ACTIVE})')
    ap.add_argument('--json', help='write the full report here')
    ap.add_argument('--md', help='write the Markdown report here')
    ap.add_argument('--calib', help='TSV "path<TAB>verdict[<TAB>note[<TAB>limit_s]]": run all and test separation')
    a = ap.parse_args(argv)
    a.mask = tuple(float(x) for x in a.mask.split(',')) if a.mask else None
    try:
        if a.calib:
            return calib(a.calib, a)
        if not a.video:
            ap.error('a video file or --calib is required')
        r = analyse(a.video, limit=a.limit, mask=a.mask, fast=a.fast, dead=a.dead)
    except FileNotFoundError as e:
        if e.filename in (FFMPEG, FFPROBE):
            print('ffmpeg not found: install it or set FFMPEG/FFPROBE', file=sys.stderr)
        else:
            print(f'cannot read {e.filename}', file=sys.stderr)
        return 1
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f'cannot analyse {os.path.basename(a.video)}: {e}', file=sys.stderr)
        return 1
    md = report_md(r)
    if a.md:
        write_text(a.md, md)
    if a.json:
        write_text(a.json, json.dumps(r, ensure_ascii=False, indent=1))
    print(md if not a.md else md.split('\n\n|')[0] + f'\n-> {a.md}')
    return 2 if r['verdict'] == 'dead' else 0


if __name__ == '__main__':
    sys.exit(main())
