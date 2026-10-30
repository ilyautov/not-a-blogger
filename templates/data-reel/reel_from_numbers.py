# SPDX-License-Identifier: MIT
"""real-numbers.json -> reel.json + voice/lines.json + voice/chunks.json for the starter scene.

Every number in the frame and in the voice comes from real-numbers.json through this script. Nobody types a number
by hand: change the measurement, rerun, the script, subtitles and scene follow. check_numbers.py verifies it.

  python3 reel_from_numbers.py                     # reads ./real-numbers.json, writes into this folder
  python3 reel_from_numbers.py --into ../my-reel   # a starter copy: reel.json, voice/lines.json, voice/chunks.json
  python3 reel_from_numbers.py --lang en           # spoken numbers in English (num2words), decimal point instead of comma
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def show_num(v: float, lang: str = 'ru') -> str:
    """How a number looks on screen: integers above 10, one decimal below; Russian uses a decimal comma."""
    s = str(int(round(v))) if abs(v) >= 10 or float(v).is_integer() else f'{v:.1f}'
    return s.replace('.', ',') if lang == 'ru' else s


def say_num(v: float, lang: str = 'ru') -> str:
    """How a number is spoken. num2words if installed, otherwise digits (then fix chunks.json by hand)."""
    x = int(round(v)) if abs(v) >= 10 or float(v).is_integer() else round(v, 1)
    try:
        from num2words import num2words
        return num2words(x, lang=lang)
    except Exception:
        return str(x)


def values(n: dict, lang: str) -> dict:
    """Placeholder -> (number or text). The only place where a number enters the reel."""
    top = n['by_folder'][0] if n['by_folder'] else {'name': '-', 'gb': 0, 'share': 0}
    kind = lambda k: n['by_kind'].get(k, {}).get('gb', 0.0)
    return {'target': n['target_label'], 'total_gb': n['total_gb'], 'files': n['files'],
            'top1_name': top['name'], 'top1_gb': top['gb'], 'top1_pct': round(top['share'] * 100),
            'video_gb': kind('video'), 'archives_gb': kind('archives'), 'images_gb': kind('images'),
            'old_gb': n['older_than_1y_gb'], 'old_pct': round(n['older_than_1y_share'] * 100)}


def fill(template: str, vals: dict, lang: str):
    """One template line -> (shown line, spoken line). A shown token that stands for several spoken words gets the
    starter markup token{N}; spaces inside a shown token become underscores (the starter shows them as spaces)."""
    show, say = template, template
    for k, v in vals.items():
        if '{' + k + '}' not in template: continue
        if isinstance(v, str): sh, sy = v, v
        else: sh, sy = show_num(v, lang), say_num(v, lang)
        nw = len(sy.split())
        token = sh.replace(' ', '_') + (f'{{{nw}}}' if nw != 1 or ' ' in sh else '')
        show, say = show.replace('{' + k + '}', token), say.replace('{' + k + '}', sy)
    left = re.findall(r'\{[a-z0-9_]+\}', say)
    if left: raise SystemExit(f'unknown placeholders {left} in: {template}')
    return show, say


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--numbers', type=Path, default=HERE / 'real-numbers.json')
    ap.add_argument('--template', type=Path, default=HERE / 'lines.template.json')
    ap.add_argument('--into', type=Path, default=HERE)
    ap.add_argument('--lang', default='ru')
    ap.add_argument('--allow-incomplete', action='store_true',
                    help='build from a measurement with unreadable folders (the source line then says so)')
    a = ap.parse_args()
    n = json.loads(a.numbers.read_text()); vals = values(n, a.lang)
    incomplete = n.get('unreadable_entries', 0) if n.get('complete') is False else 0
    if incomplete and not a.allow_incomplete:
        raise SystemExit(f'{a.numbers.name}: incomplete measurement ({incomplete} unreadable entries), the numbers are too '
                         'low. Measure again with access, or pass --allow-incomplete to say so in the source line')
    if n['total_gb'] < 1:
        print(f'warning: {n["total_gb"]} GB in total, numbers in GB will round to 0 on screen; measure a bigger folder '
              'or switch the script and values() to megabytes')
    rows = [fill(t, vals, a.lang) for t in json.loads(a.template.read_text())['lines']]
    (a.into / 'voice').mkdir(parents=True, exist_ok=True)
    (a.into / 'voice/lines.json').write_text(json.dumps([s for s, _ in rows], ensure_ascii=False, indent=1) + '\n')
    (a.into / 'voice/chunks.json').write_text(json.dumps(
        [{'text': y, 'pause': .12 if i < len(rows) - 1 else 0.0, 'tail': False, 'engine': 'omnivoice', 'omni_speed': 1.0} for i, (_, y) in enumerate(rows)],
        ensure_ascii=False, indent=1) + '\n')
    fmt = {k: (v if isinstance(v, str) else show_num(v, a.lang)) for k, v in vals.items()}
    reel = {
        'title': f'Data reel: {n["target_label"]}', 'max_duration': 30,
        'music': {'file': None, 'offset': 0, 'gain': 0.25, 'credit': ''},
        'sound_events': [{'event': 'total', 'kind': 'thud', 'gain': .35}, {'event': 'top', 'kind': 'pop', 'gain': .3},
                         {'event': 'kinds', 'kind': 'click', 'gain': .3}, {'event': 'old', 'kind': 'chord', 'gain': .2}],
        'n': {**{k: v for k, v in vals.items()}, 'fmt': fmt,
              'bars': [{'name': f['name'], 'gb': f['gb'], 'fmt': show_num(f['gb'], a.lang)} for f in n['by_folder']]},
        'source': f'real-numbers.json ({n["tool"]}, {n["measured_at"]}'
                  + (f', incomplete: {incomplete} unreadable entries' if incomplete else '') + ')',
    }
    if incomplete:
        reel['measurement_incomplete'] = incomplete
    (a.into / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False, indent=1) + '\n')
    for s, _ in rows: print(' ', s)
    print('->', a.into / 'reel.json', a.into / 'voice/lines.json', a.into / 'voice/chunks.json')


if __name__ == '__main__':
    main()
