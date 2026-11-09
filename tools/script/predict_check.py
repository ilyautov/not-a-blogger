#!/usr/bin/env python3
"""Prediction test and overlap check for a short-video idea: is it the obvious one, or one you already made?

Idea after references/writing.md ("The prediction test", "The overlap check") and scripts/brief.py from
sarpstar/cinecode (MIT, (c) 2026 Sarp Yıldız); the code and wording are our own.

An author does not see their own banality or their own repeats, so two fresh agents judge:
  1. predict   gets ONLY the topic and writes the 5 videos everyone expects;
  2. overlap   compares your candidates with those five and with your past videos
               -> one line per candidate: CLEAR / SHARES (one element repeated) / OVERLAP (the idea itself repeated).

Past videos are any CSV or JSON list with columns: `title` and/or `logline` (one is required), optional `id`,
`first_line`, `last_line`, `form`, `ending`, `published`. Build it once from your project folders or your
channel export; the tool does not crawl anything.

Without --run the tool only writes the prompt (*.prompt.txt): hand it to any agent that has no context of
your session (a fresh chat, a background agent). With --run it calls `claude -p` from an empty temporary
folder with no settings, tools or MCP servers, so the judge sees nothing but the prompt. The prompt texts are
also in prompts/script/prediction-test.md and prompts/script/overlap-check.md.
This is a generator of replacements, not a gate: the person decides.

Example:
  python3 tools/script/predict_check.py predict --topic "an AI makes up passwords" --out research
  python3 tools/script/predict_check.py overlap --topic "an AI makes up passwords" \
          --candidates research/candidates.md --past my-videos.csv --out research
  python3 tools/script/predict_check.py summary --out research
Exit codes: 0; 1 on a missing input (no predict.md before overlap, unreadable past file, no verdict lines).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERDICTS = ('CLEAR', 'SHARES', 'OVERLAP')

PREDICT = """You are given only the topic of a short vertical video (Reels/Shorts, 15-40 s). Nothing else is known.
Topic: "{topic}"

Write five videos on this topic that any viewer and any author would expect: the most obvious ones, the
first that come to mind. One line per video, strictly in this format:
P1 | plot in one sentence | key frames (2-3) | form (skit / list / how-to / breakdown / experiment / motion) | ending
...
P5 | ...
No introduction and no explanations, only five lines."""

OVERLAP = """You check short-video ideas for banality and self-repetition. You did not write the ideas.
Topic from the client: "{topic}". Whatever the topic itself names (a product, a brand, a person, a place) is
not a repeat: a repeat can only be in the idea, the frames, the world or the form.

## Candidates
{candidates}

## Expected videos (written by an agent that knew only the topic)
{predict}

## The author's past videos (id | title | logline | first and last lines)
{past}

One line per candidate, strictly in this format:
<candidate number> | CLEAR | -
<candidate number> | SHARES | which element repeats (ending / form / key frame / world / opening) and with what: P<n> or a past video id
<candidate number> | OVERLAP | what the idea itself repeats (premise and key frames): P<n> or a past video id
CLEAR: nothing matched. SHARES: the idea is new, one element repeats. OVERLAP: the same premise, whatever the details.
No introduction, only the lines for the candidates."""


# ------------------------------------------------------------------ past videos
def load_past(path):
    """Rows from a CSV (header row) or JSON (list of objects, or {"videos": [...]})."""
    p = Path(path)
    text = p.read_text(encoding='utf-8-sig')
    if p.suffix.lower() == '.json':
        data = json.loads(text)
        rows = data.get('videos', data.get('rows', [])) if isinstance(data, dict) else data
    else:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=',;\t') if text.strip() else csv.excel
        rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        r = {str(k).strip().lower(): ('' if v is None else str(v).strip()) for k, v in r.items() if k is not None}
        if r.get('title') or r.get('logline'):
            out.append(r)
    return out


def format_past(rows):
    lines = []
    for i, r in enumerate(rows, 1):
        pub = ' [published]' if r.get('published', '').lower() in ('1', 'true', 'yes', 'y') else ''
        said = ' / '.join(x for x in (r.get('first_line'), r.get('last_line')) if x)
        extra = ', '.join(f'{k}: {r[k]}' for k in ('form', 'ending') if r.get(k))
        cells = [r.get('id') or f'V{i}', (r.get('title') or '')[:80] + pub, r.get('logline', '')[:200],
                 (said + (f' ({extra})' if extra else ''))[:300]]
        lines.append(' | '.join(cells))
    return '\n'.join(lines)


# ------------------------------------------------------------------ agent
def run_claude(prompt, model):
    """A fresh agent without context: empty folder, no settings, skills, tools or MCP servers."""
    if not shutil.which('claude'):
        sys.exit('claude CLI not found; run without --run and give the *.prompt.txt to any fresh agent')
    with tempfile.TemporaryDirectory() as empty:
        p = subprocess.run(['claude', '-p', '--model', model, '--output-format', 'json',
                            '--setting-sources', '', '--strict-mcp-config', '--no-session-persistence',
                            '--tools', ''],
                           input=prompt, capture_output=True, text=True, timeout=900, cwd=empty)
    try:
        return json.loads(p.stdout).get('result', '')
    except (ValueError, AttributeError):
        sys.exit(f'claude -p gave no JSON answer: {(p.stdout + p.stderr)[-500:]}')


def parse(text):
    """Verdict lines `N | CLEAR|SHARES|OVERLAP | why` -> [(N, verdict, why)]."""
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 2 and cells[1].upper() in VERDICTS:
            out.append((cells[0], cells[1].upper(), cells[2] if len(cells) > 2 else ''))
    return out


def save(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n', encoding='utf-8')
    print('->', path)


def print_summary(rows):
    for num, v, why in rows:
        print(f'{num:>4}  {v:<8} {why}')
    keep = [n for n, v, _ in rows if v != 'OVERLAP']
    print(f'\nkeep: {", ".join(keep) or "none, write new candidates"}; '
          f'SHARES: change the repeated element; OVERLAP: drop it, do not argue')
    return keep


def main(argv=None):
    ap = argparse.ArgumentParser(description='Prediction test and overlap check for a short-video idea.')
    ap.add_argument('step', choices=['predict', 'overlap', 'summary'])
    ap.add_argument('--topic', help="the topic in the person's own words, quoted, without your paraphrase")
    ap.add_argument('--candidates', help='file with candidates: number | logline | key frames | world | form | ending')
    ap.add_argument('--past', help='CSV or JSON of past videos (title and/or logline, optional id, first_line, ...)')
    ap.add_argument('--out', required=True, help='folder for prompts and answers (e.g. research/)')
    ap.add_argument('--run', action='store_true', help='call claude -p right away; without it only the prompt is written')
    ap.add_argument('--model', default='sonnet')
    a = ap.parse_args(argv)
    out = Path(a.out)

    if a.step == 'predict':
        if not a.topic:
            ap.error('--topic is required')
        prompt = PREDICT.format(topic=a.topic)
        save(out / 'predict.prompt.txt', prompt)
        if a.run:
            save(out / 'predict.md', run_claude(prompt, a.model))
        return 0

    if a.step == 'overlap':
        if not (a.topic and a.candidates):
            ap.error('--topic and --candidates are required')
        pred_f = out / 'predict.md'
        if not pred_f.exists():
            print(f'no {pred_f}: run the predict step first (its agent must not see your candidates)', file=sys.stderr)
            return 1
        if a.past:
            try:
                rows = load_past(a.past)
            except (OSError, ValueError, csv.Error) as e:
                print(f'cannot read {a.past}: {e}', file=sys.stderr)
                return 1
            past = format_past(rows) or '(none)'
        else:
            rows, past = [], '(no past videos given)'
        save(out / 'past-videos.md', f'# Past videos ({len(rows)})\n\n{past}')
        prompt = OVERLAP.format(topic=a.topic, candidates=Path(a.candidates).read_text(encoding='utf-8').strip(),
                                predict=pred_f.read_text(encoding='utf-8').strip(), past=past)
        save(out / 'overlap.prompt.txt', prompt)
        if not a.run:
            return 0
        save(out / 'overlap.md', run_claude(prompt, a.model))

    f = out / 'overlap.md'
    if not f.exists():
        print(f'no {f}: save the judge answer there first', file=sys.stderr)
        return 1
    rows = parse(f.read_text(encoding='utf-8'))
    if not rows:
        print(f'{f} has no lines like "N | CLEAR|SHARES|OVERLAP | ..."', file=sys.stderr)
        return 1
    print_summary(rows)
    return 0


if __name__ == '__main__':
    sys.exit(main())
