#!/usr/bin/env python3
"""Per-scene checks on a finished mp4: action with the camera subtracted, and composition repeats.

Idea after scripts/scene_check.py (action, repeats) from sarpstar/cinecode (MIT, (c) 2026 Sarp Yıldız);
the code is rewritten from scratch on numpy. Cuts are found by the tool itself; no OpenCV is needed, the
camera is compensated by a brute-force search over shift and scale.

What it measures (one ffmpeg pass: 4 frames/s, grey, 80 px wide, gblur 1.5, as in cinecode):
  action   Between neighbouring samples the best common shift and scale (pan, push-in, pull-out) is found on
           a centre square of 0.8 of the short side, weighted to the centre; what remains after compensation
           is action. A scene is flagged `still` when the median raw difference is < 1.0 (of 255), and
           `camera_led` when the residual is < 1.0 or < 0.3 of the raw difference (the camera carries the
           scene). 0.2 s at each scene edge is not judged. Scenes lie between detected cuts, or are fixed
           windows with --every N.
  repeat   One frame per second, 40 px wide; second j is a repeat when a frame at least 6 s earlier has a
           mean absolute difference < 5. `repeat_share` is the share of repeat seconds. With --loop the
           last 3 s are not counted (a loop matches its start on purpose).

Both checks are WARNINGS. On 20 videos with human verdicts neither number separated approved from rejected
videos (see recipes/qa/qa-picture-checks-warn-only.md), so the exit code is 0 whatever the values. The warning
thresholds are cinecode's (repeat share > 10 %) and "more than half of the time in flagged scenes" for
action. Read the report as "go and look at these seconds", not as a verdict.

Input: an mp4, or a project folder with output/final.mp4 (the report then goes to <folder>/qa/scene-gate.*).
Output: a Markdown summary on stdout; --json / --md write the full report (per-scene table, repeat spans).
--calib verdicts.tsv runs the analysis over `path<TAB>label[<TAB><TAB>limit_seconds]` lines and prints one row
per video, so you can see whether the numbers separate YOUR good videos from your bad ones.
Exit codes: 0 (checks only warn); 1 when the file cannot be read or ffmpeg is missing.

Example:
  python3 tools/qa/scene_gate.py output/final.mp4 --json qa/scene-gate.json
  python3 tools/qa/scene_gate.py starter                     # -> starter/qa/scene-gate.{json,md}
  python3 tools/qa/scene_gate.py --calib my-verdicts.tsv --limit 60
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = os.environ.get('FFPROBE') or shutil.which('ffprobe') or 'ffprobe'

FPS = 4.0
SAMPLE_W = 80
CROP = 0.8
SHIFTS = 6
SCALES = (0.94, 0.97, 1.0, 1.03, 1.06)
EDGE_S = 0.2
ACTION_MIN = 1.0      # cinecode: median residual < 1.0 of 255 means nothing moves in the scene
ACTION_SHARE = 0.3    # cinecode: residual < 30 % of the raw difference means the camera carries the scene
REPEAT_GAP = 6
REPEAT_MAD = 5.0
WARN_REPEAT_SHARE = 0.10
WARN_ACTION_FLAGGED = 0.50


def probe(path: Path):
    j = json.loads(subprocess.check_output([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                            'stream=width,height:format=duration', '-of', 'json', str(path)]))
    s = j['streams'][0]
    return int(s['width']), int(s['height']), float(j['format'].get('duration') or 0)


def decode(path: Path, fps=FPS, width=SAMPLE_W, limit=None):
    """Grey, blurred, small frames: (n, h, w) float32 and (W, H, duration) of the source."""
    W, H, dur = probe(path)
    h = max(16, int(round(width * H / W / 2) * 2))
    cmd = [FFMPEG, '-v', 'error', '-nostdin']
    if limit:
        cmd += ['-t', str(limit)]
    cmd += ['-i', str(path), '-an', '-vf', f'fps={fps},scale={width}:{h}:flags=area,gblur=sigma=1.5,format=gray',
            '-f', 'rawvideo', '-']
    raw = subprocess.check_output(cmd)
    n = len(raw) // (width * h)
    return np.frombuffer(raw[:n * width * h], np.uint8).reshape(n, h, width).astype(np.float32), (W, H, dur)


# ---------------------------------------------------------------- camera compensation
class Aligner:
    """Residual of frame B against A after the best common shift and scale (centre square, centre-weighted)."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        side = int(min(w, h) * CROP) // 2 * 2
        self.cx, self.cy = w / 2, h / 2
        x0, y0 = int(self.cx - side / 2), int(self.cy - side / 2)
        ys, xs = np.mgrid[y0:y0 + side, x0:x0 + side]
        xs, ys = xs.ravel(), ys.ravel()
        r = side / 2
        wt = np.maximum(0.0, 1 - 0.7 * ((xs + 0.5 - self.cx) ** 2 + (ys + 0.5 - self.cy) ** 2) / (r * r))
        keep = wt > 0
        self.xs, self.ys, self.wt = xs[keep].astype(np.float32), ys[keep].astype(np.float32), wt[keep].astype(np.float32)
        self.bidx = (ys[keep] * w + xs[keep]).astype(np.int64)
        coarse = ((xs[keep] + ys[keep]) % 2 == 0) & (ys[keep] % 2 == 0)
        self.coarse = np.where(coarse)[0]
        rng = range(-SHIFTS - 1, SHIFTS + 2)
        self.combos = [(s, dx, dy) for s in SCALES for dx in rng for dy in rng]
        self.pos = {c: i for i, c in enumerate(self.combos)}
        S = np.array([c[0] for c in self.combos], np.float32)[:, None]
        DX = np.array([c[1] for c in self.combos], np.float32)[:, None]
        DY = np.array([c[2] for c in self.combos], np.float32)[:, None]
        ax = np.clip(np.rint(self.cx + (self.xs[None] + 0.5 - self.cx) / S - 0.5 + DX), 0, w - 1).astype(np.int64)
        ay = np.clip(np.rint(self.cy + (self.ys[None] + 0.5 - self.cy) / S - 0.5 + DY), 0, h - 1).astype(np.int64)
        self.idx = ay * w + ax                                     # (combinations, pixels)
        self.coarse_rows = np.array([self.pos[(s, dx, dy)] for s in SCALES for dx in range(-SHIFTS, SHIFTS + 1, 2)
                                     for dy in range(-SHIFTS, SHIFTS + 1, 2)])
        self.raw_row = self.pos[(1.0, 0, 0)]

    def _cost(self, a, bv, rows, cols=None):
        idx = self.idx[rows] if cols is None else self.idx[np.ix_(rows, cols)]
        wt = self.wt if cols is None else self.wt[cols]
        b = bv if cols is None else bv[cols]
        return (np.abs(b[None] - a[idx]) * wt).sum(1) / wt.sum()

    def _fine(self, a, bv, s, dx, dy):
        w, h = self.w, self.h
        ds = np.array([-0.01, 0, 0.01], np.float32)
        sh = np.array([-0.5, 0, 0.5], np.float32)
        S, I, J = np.meshgrid(s + ds, dx + sh, dy + sh, indexing='ij')
        S, I, J = S.reshape(-1, 1), I.reshape(-1, 1), J.reshape(-1, 1)
        fx = np.clip(self.cx + (self.xs[None] + 0.5 - self.cx) / S - 0.5 + I, 0, w - 1.001)
        fy = np.clip(self.cy + (self.ys[None] + 0.5 - self.cy) / S - 0.5 + J, 0, h - 1.001)
        x0, y0 = fx.astype(np.int64), fy.astype(np.int64)
        u, v = fx - x0, fy - y0
        j = y0 * w + x0
        av = (a[j] * (1 - u) + a[j + 1] * u) * (1 - v) + (a[j + w] * (1 - u) + a[j + w + 1] * u) * v
        return float(((np.abs(bv[None] - av) * self.wt).sum(1) / self.wt.sum()).min())

    def residual(self, A: np.ndarray, B: np.ndarray) -> tuple[float, float]:
        """(raw difference, residual after the best shift + scale), both mean |Δ| on 0..255."""
        a, bfull = A.ravel(), B.ravel()
        bv = bfull[self.bidx]
        raw = float(self._cost(a, bv, [self.raw_row])[0])
        c = self._cost(a, bv, self.coarse_rows, self.coarse)
        s0, dx0, dy0 = self.combos[self.coarse_rows[int(c.argmin())]]
        k = SCALES.index(s0)
        rows = [self.pos[(s, dx0 + i, dy0 + j)] for s in SCALES[max(0, k - 1):k + 2] for i in (-1, 0, 1) for j in (-1, 0, 1)]
        c2 = self._cost(a, bv, rows)
        s1, dx1, dy1 = self.combos[rows[int(c2.argmin())]]
        res = min(float(c2.min()), self._fine(a, bv, s1, dx1, dy1))
        return raw, min(raw, res)


@lru_cache(maxsize=4)
def aligner(w, h):
    return Aligner(w, h)


# ---------------------------------------------------------------- cuts and scenes
def find_cuts(F: np.ndarray, al: Aligner) -> list[int]:
    """Indices i where a cut lies between sample i and i+1: a difference spike the camera does not explain."""
    d = np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))
    cuts = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - 6):i], d[i + 1:i + 7]])
        med = float(np.median(nb)) if len(nb) else 0.0
        if d[i] >= max(8.0, 3 * med + 2):
            _, res = al.residual(F[i], F[i + 1])
            if res >= 0.6 * d[i] and not (cuts and cuts[-1] == i - 1):
                cuts.append(i)
    return cuts


def scenes_of(n: int, fps: float, cuts: list[int] | None, every: float | None):
    dur = n / fps
    if every:
        k = max(1, round(dur / every))
        return [(i * dur / k, (i + 1) * dur / k) for i in range(k)]
    b = [0.0] + [(c + 1) / fps for c in cuts] + [dur]
    return [(a, e) for a, e in zip(b[:-1], b[1:]) if e - a > 0]


def action(F: np.ndarray, fps: float, scenes, al: Aligner):
    out = []
    for a, b in scenes:
        i0, i1 = int((a + EDGE_S) * fps + 0.999), int((b - EDGE_S) * fps)
        pairs = range(max(1, i0 + 1), min(len(F), i1 + 1))
        if len(pairs) < 2:
            out.append({'start': round(a, 2), 'end': round(b, 2), 'dur': round(b - a, 2), 'measured': False})
            continue
        vals = [al.residual(F[i - 1], F[i]) for i in pairs]
        raw = float(np.median([v[0] for v in vals]))
        res = float(np.median([v[1] for v in vals]))
        flag = 'still' if raw < ACTION_MIN else ('camera_led' if res < ACTION_MIN or res < ACTION_SHARE * raw else '')
        out.append({'start': round(a, 2), 'end': round(b, 2), 'dur': round(b - a, 2), 'measured': True,
                    'residual': round(res, 3), 'total': round(raw, 3), 'flag': flag})
    return out


# ---------------------------------------------------------------- repeats
def thumbs_1s(F: np.ndarray, fps: float) -> np.ndarray:
    step = max(1, int(round(fps)))
    T = F[step // 2::step]
    h, w = T.shape[1] // 2 * 2, T.shape[2] // 2 * 2
    return T[:, :h, :w].reshape(len(T), h // 2, 2, w // 2, 2).mean(axis=(2, 4))   # 80 -> 40 px


def repeats(T: np.ndarray, gap=REPEAT_GAP, limit=REPEAT_MAD, tail_skip=0, shots_of=None):
    """Repeat seconds: for each second j the closest frame i <= j - gap with MAD < limit, merged into spans."""
    n = len(T)
    flat = T.reshape(n, -1)
    best = {}
    for j in range(gap, n - tail_skip):
        d = np.abs(flat[:j - gap + 1] - flat[j]).mean(axis=1)
        i = int(d.argmin())
        if d[i] < limit:
            best[j] = (i, float(d[i]))
    spans, prev = [], None
    for j in sorted(best):
        i = best[j][0]
        if prev and j == prev[1] + 1 and abs(i - prev[3] - 1) <= 1:
            prev[1], prev[3] = j, i
        else:
            prev = [j, j, i, i]
            spans.append(prev)
    cross = sum(1 for j, (i, _) in best.items() if shots_of is None or shots_of(i) != shots_of(j))
    measured = max(1, n - tail_skip)
    return {'repeat_seconds': len(best), 'repeat_share': round(len(best) / measured, 4),
            'repeat_share_cross_shot': round(cross / measured, 4),
            'spans': [{'at': a, 'to': b + 1, 'repeats': i, 'repeats_to': j + 1} for a, b, i, j in spans]}


# ---------------------------------------------------------------- report
def analyze(path: Path, limit=None, every=None, loop=False):
    F, (W0, H0, dur) = decode(path, limit=limit)
    n = len(F)
    if n < 8:
        raise RuntimeError('too few frames (need at least 2 s of video)')
    al = aligner(F.shape[2], F.shape[1])
    cuts = [] if every else find_cuts(F, al)
    scenes = scenes_of(n, FPS, cuts, every)
    sc = action(F, FPS, scenes, al)
    meas = [s for s in sc if s['measured']]
    tot = sum(s['dur'] for s in meas) or 1.0
    flagged = sum(s['dur'] for s in meas if s['flag'])
    camera_led = sum(s['dur'] for s in meas if s['flag'] == 'camera_led')
    still = sum(s['dur'] for s in meas if s['flag'] == 'still')
    T = thumbs_1s(F, FPS)
    bounds = [s[0] for s in scenes]
    rep = repeats(T, tail_skip=3 if loop else 0, shots_of=lambda sec: int(np.searchsorted(bounds, sec + 0.5, 'right')))
    res_w = sum(s['residual'] * s['dur'] for s in meas) / tot
    r = {'file': str(path), 'size': [W0, H0], 'duration': round(dur, 2), 'analyzed_s': round(n / FPS, 1),
         'cuts': len(cuts), 'scenes': sc,
         'action_flagged_share': round(flagged / tot, 4), 'camera_led_share': round(camera_led / tot, 4),
         'still_share': round(still / tot, 4), 'residual_mean': round(res_w, 3), **rep}
    r['warnings'] = warnings(r)
    r['verdict'] = 'warn' if r['warnings'] else 'info'
    return r


def warnings(r: dict) -> list[str]:
    w = []
    if r['repeat_share'] > WARN_REPEAT_SHARE:
        w.append(f'composition repeats after >= {REPEAT_GAP} s: {r["repeat_share"]:.0%} of seconds '
                 f'(warn above {WARN_REPEAT_SHARE:.0%})')
    if r['action_flagged_share'] > WARN_ACTION_FLAGGED:
        w.append(f'scenes without action (still or camera-led): {r["action_flagged_share"]:.0%} of the time '
                 f'(warn above {WARN_ACTION_FLAGGED:.0%})')
    return w


def report_md(r: dict) -> str:
    L = [f'# scene_gate: {Path(r["file"]).name}', '',
         f'- analyzed {r["analyzed_s"]} s of {r["duration"]} s, cuts {r["cuts"]}, scenes {len(r["scenes"])}',
         f'- action with the camera subtracted: {r["action_flagged_share"]:.0%} of the time flagged '
         f'(still {r["still_share"]:.0%}, camera-led {r["camera_led_share"]:.0%}); mean residual {r["residual_mean"]}',
         f'- composition repeats after >= {REPEAT_GAP} s: {r["repeat_share"]:.0%} of seconds '
         f'({r["repeat_share_cross_shot"]:.0%} in another shot)',
         '- warnings: ' + ('; '.join(r['warnings']) if r['warnings'] else 'none'), '',
         '| # | start | end | residual | total | flag |', '|---|---|---|---|---|---|']
    for i, s in enumerate(r['scenes'], 1):
        if s['measured']:
            L.append(f'| {i} | {s["start"]:.2f} | {s["end"]:.2f} | {s["residual"]} | {s["total"]} | {s["flag"] or "ok"} |')
        else:
            L.append(f'| {i} | {s["start"]:.2f} | {s["end"]:.2f} | - | - | short |')
    if r['spans']:
        L += ['', 'Repeats (seconds -> what they look like):'] + [
            f'- {x["at"]}-{x["to"]} s ~ {x["repeats"]}-{x["repeats_to"]} s' for x in r['spans'][:15]]
    L += ['', 'These are warnings: on 20 videos with human verdicts the numbers did not separate approved from rejected.']
    return '\n'.join(L) + '\n'


def resolve(arg: str):
    """mp4 -> (mp4, None); project folder -> (folder/output/final.mp4, folder/qa)."""
    p = Path(arg).expanduser()
    if p.is_dir():
        return p / 'output' / 'final.mp4', p / 'qa'
    return p, None


def calib(tsv: Path, args) -> int:
    rows = []
    for line in tsv.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        path, label = parts[0], parts[1]
        lim = float(parts[3]) if len(parts) > 3 and parts[3] else args.limit
        mp4, _ = resolve(path)
        try:
            r = analyze(mp4, limit=lim, every=args.every, loop=bool(args.loop))
        except Exception as e:  # noqa: BLE001 - one unreadable file must not stop the calibration
            print(f'! {path}: {e}', file=sys.stderr)
            continue
        rows.append((label, path, r))
        print(f'{label:5} action {r["action_flagged_share"]:.2f} residual {r["residual_mean"]:.2f} '
              f'repeat {r["repeat_share"]:.2f} repeat_x {r["repeat_share_cross_shot"]:.2f} cuts {r["cuts"]}  {path}',
              flush=True)
    if args.json:
        Path(args.json).write_text(json.dumps(
            [{'label': a, 'path': b, **{k: v for k, v in r.items() if k not in ('scenes', 'spans')}} for a, b, r in rows],
            ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Per-scene checks on an mp4: action minus camera, composition repeats '
                                             '(warnings only).')
    ap.add_argument('target', nargs='?', help='mp4, or a project folder with output/final.mp4')
    ap.add_argument('--limit', type=float, help='analyze only the first N seconds')
    ap.add_argument('--every', type=float, help='fixed scene windows of N s instead of detected cuts')
    ap.add_argument('--loop', action='store_true', help='the video is a loop: skip the last 3 s in the repeat check')
    ap.add_argument('--json', help='full report as JSON')
    ap.add_argument('--md', help='full report as Markdown')
    ap.add_argument('--calib', help='TSV path<TAB>label: one summary row per video')
    a = ap.parse_args(argv)
    try:
        if a.calib:
            return calib(Path(a.calib), a)
        if not a.target:
            ap.error('an mp4 or a project folder is required')
        mp4, qa = resolve(a.target)
        if not mp4.exists():
            print(f'no such file: {mp4}', file=sys.stderr)
            return 1
        r = analyze(mp4, limit=a.limit, every=a.every, loop=a.loop)
    except FileNotFoundError as e:
        print(f'ffmpeg/ffprobe not found: {e}', file=sys.stderr)
        return 1
    except (subprocess.CalledProcessError, RuntimeError) as e:
        print(f'cannot read {a.target}: {e}', file=sys.stderr)
        return 1
    md = report_md(r)
    js_path = Path(a.json) if a.json else (qa / 'scene-gate.json' if qa else None)
    md_path = Path(a.md) if a.md else (qa / 'scene-gate.md' if qa else None)
    if js_path:
        js_path.parent.mkdir(parents=True, exist_ok=True)
        js_path.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    if md_path:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding='utf-8')
    print(md.split('\n\n|')[0] + (f'\n-> {js_path}' if js_path else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
