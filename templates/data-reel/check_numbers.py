# SPDX-License-Identifier: MIT
"""Gate: every number in the subtitles, the voice and reel.json must come from real-numbers.json.

Checks, against values recomputed from real-numbers.json with the same code as reel_from_numbers.py:
  - voice/lines.json: every number in the subtitles is a show form of a measured value;
  - voice/chunks.json: one chunk per line, the spoken form of every number of that line is in its chunk, and the
    chunk has no other digits or number words (rephrasing around the numbers is fine);
  - reel.json: the raw values in n (total_gb, old_pct, ... drive the counters and the grid), n.fmt labels and
    n.bars (name, gb, fmt: bar lengths) match the measurement;
  - an incomplete measurement ("complete": false: unreadable folders) is only accepted if reel.json says so
    (reel_from_numbers.py --allow-incomplete).
Exits 1 and lists the offenders if a number was typed by hand or the measurement changed after reel_from_numbers.py.
  python3 check_numbers.py                 # files in this folder
  python3 check_numbers.py --dir ../my-reel
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reel_from_numbers import say_num, show_num, values  # noqa: E402

NUM = re.compile(r'\d+(?:[.,]\d+)?')
# words for 1 double as "a"/"one of" ("одна папка", "one folder"): not counted as stray numbers
ONE = {'один', 'одна', 'одно', 'одну', 'одной', 'одного', 'одним', 'one', 'a', 'an'}


def wjoin(s: str) -> str:
    """Words only, lowercase, single spaces: "Девять, и четыре" -> "девять и четыре"."""
    return ' '.join(re.findall(r'\w+', s.lower()))


def same(a, b) -> bool:
    if isinstance(a, str) or isinstance(b, str) or a is None or b is None: return a == b
    return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-9)


def number_words(lang: str) -> set[str]:
    """Words num2words uses for numbers in this language; empty without num2words (then only digits are checked)."""
    try:
        from num2words import num2words
    except ImportError:
        return set()
    out = set()
    for x in [*range(0, 21), *range(30, 100, 10), *range(100, 1000, 100), 1000, 2000, 5000, 10 ** 6, 0.5, 1.5, 2.5]:
        try: out |= set(re.findall(r'\w+', num2words(x, lang=lang).lower()))
        except Exception: pass
    return out - ONE


def check(d: Path, lang: str = 'ru') -> list[str]:
    n = json.loads((d / 'real-numbers.json').read_text()); vals = values(n, lang)
    nums = [v for v in vals.values() if not isinstance(v, str)] + [f['gb'] for f in n['by_folder']]
    say = {}                                                       # show form -> spoken forms of the same value
    for v in nums: say.setdefault(show_num(v, lang), set()).add(say_num(v, lang).lower())
    allowed = set(say)
    texts = sorted([v for v in vals.values() if isinstance(v, str)] + [f['name'] for f in n['by_folder']], key=len, reverse=True)
    bad = []

    def strip_texts(s: str) -> str:                                # digits inside folder names are not claims
        for t in texts: s = s.replace(t, ' ')
        return s

    lines = json.loads((d / 'voice/lines.json').read_text())
    line_nums = []
    for i, line in enumerate(lines):
        found = NUM.findall(strip_texts(re.sub(r'\{\d+\}', '', line).replace('_', ' ')))
        line_nums.append(found)
        bad += [f'voice/lines.json[{i}]: {x}' for x in found if x not in allowed]

    chunks_p = d / 'voice/chunks.json'
    if chunks_p.exists():
        chunks = json.loads(chunks_p.read_text())
        if len(chunks) != len(lines):
            bad.append(f'voice/chunks.json: {len(chunks)} chunks for {len(lines)} lines')
        words = number_words(lang)
        for i, (ch, found) in enumerate(zip(chunks, line_nums)):
            rest = ' ' + wjoin(strip_texts(ch['text'] if isinstance(ch, dict) else str(ch))) + ' '
            for x in found:
                forms = sorted({' ' + wjoin(f) + ' ' for f in say.get(x, ())}, key=len, reverse=True)
                hit = next((f for f in forms if f in rest), None)
                if hit is None:
                    bad.append(f'voice/chunks.json[{i}]: subtitle says {x}, voice does not say '
                               + (' / '.join(f.strip() for f in forms) or x))
                else:
                    rest = rest.replace(hit, ' ', 1)
            stray = NUM.findall(rest) + [w for w in rest.split() if w in words]
            if stray: bad.append(f'voice/chunks.json[{i}]: spoken numbers not from the measurement: {" ".join(stray)}')
    else:
        bad.append('voice/chunks.json: missing (run reel_from_numbers.py)')

    reel = json.loads((d / 'reel.json').read_text()); rn = reel.get('n', {})
    if n.get('complete') is False and reel.get('measurement_incomplete') != n.get('unreadable_entries', 0):
        bad.append(f'real-numbers.json: incomplete measurement ({n.get("unreadable_entries", 0)} unreadable entries) '
                   'and reel.json does not say so (measure again with access, or reel_from_numbers.py --allow-incomplete)')
    if n.get('complete') is False and 'incomplete' not in str(reel.get('source', '')):
        bad.append('reel.json source: the measurement is incomplete, but the source line the viewer sees does not say '
                   '"incomplete" (keep the line reel_from_numbers.py wrote)')
    fmt = rn.get('fmt', {})
    for k, v in vals.items():
        if not same(rn.get(k), v): bad.append(f'reel.json n.{k}: {rn.get(k)} (real-numbers.json says {v})')
        want = v if isinstance(v, str) else show_num(v, lang)
        if fmt.get(k) != want: bad.append(f'reel.json n.fmt.{k}: {fmt.get(k)} (real-numbers.json says {want})')
    bars = rn.get('bars', [])
    if len(bars) != len(n['by_folder']):
        bad.append(f'reel.json n.bars: {len(bars)} bars, real-numbers.json has {len(n["by_folder"])} folders')
    for b, f in zip(bars, n['by_folder']):
        if b.get('name') != f['name'] or not same(b.get('gb'), f['gb']) or b.get('fmt') != show_num(f['gb'], lang):
            bad.append(f'reel.json bar {b.get("name")}: gb {b.get("gb")}, fmt {b.get("fmt")} '
                       f'(real-numbers.json says {f["name"]}: {f["gb"]}, {show_num(f["gb"], lang)})')
    return bad


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', type=Path, default=HERE); ap.add_argument('--lang', default='ru')
    a = ap.parse_args()
    bad = check(a.dir, a.lang)
    if bad:
        print('numbers not traceable to real-numbers.json:'); [print(' ', x) for x in bad]; sys.exit(1)
    n = json.loads((a.dir / 'real-numbers.json').read_text())
    print('check_numbers: every number traces to real-numbers.json', f'({n["measured_at"]})')


if __name__ == '__main__':
    main()
