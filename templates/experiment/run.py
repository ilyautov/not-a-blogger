# SPDX-License-Identifier: MIT
"""Test a piece of advice by running it: N clean `claude -p` runs per condition and model -> runs/*.json -> results.md.

Each condition is a system prompt in conditions/<name>.md; every condition gets the same user message (task/prompt.md).
Each run is a separate CLI call without tools, CLAUDE.md, plugins or MCP, from an empty temp folder, stdin closed,
no session saved. Everything is kept verbatim in runs/<condition>-<model>-<i>.json; existing files are skipped,
so an interrupted series resumes. results.md is rebuilt from runs/ only.

  python3 run.py --dry-run                         # print the commands, call nothing
  python3 run.py --models haiku,sonnet --n 5       # the real series
  python3 run.py --only A-control --n 2            # a subset of conditions
  python3 run.py --analyze-only                    # rebuild results.md from runs/
  python3 run.py --claude-bin /path/to/claude      # another CLI binary (tests use a fake one)
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shlex
import statistics
import subprocess
import tempfile
import time
import unicodedata
from pathlib import Path

E = Path(__file__).resolve().parent
# clean-run flags: no tools, no MCP, no user/project settings, nothing saved. Check them against `claude --help`
# of your CLI version: flags get renamed, and a silently ignored flag means your setup leaks into the experiment.
CLEAN = ['--safe-mode', '--tools', '', '--strict-mcp-config', '--no-session-persistence']


def norm(s) -> str:
    s = unicodedata.normalize('NFKC', str(s)).strip().lower()
    s = re.sub(r'[\s,;]+', ' ', s)
    return s.strip(' .')


def score(result: str | None, expected: list[str]) -> tuple[int | None, list[bool] | None, list[str] | None]:
    """Exact match per question after normalisation. None = the answer could not be parsed (counted separately)."""
    if not result: return None, None, None
    m = re.search(r'\{.*\}', result, re.S)
    try: answers = json.loads(m.group(0))['answers'] if m else None
    except Exception: answers = None
    if not isinstance(answers, list): return None, None, None
    ok = [i < len(answers) and norm(answers[i]) == norm(x) for i, x in enumerate(expected)]
    return sum(ok), ok, [str(a) for a in answers]


def cli_version(bin_: str) -> str:
    try: return subprocess.run([bin_, '--version'], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL).stdout.strip()
    except Exception as e: return f'unknown ({e.__class__.__name__})'


def run_series(a, conditions: list[str], msg: str):
    with tempfile.TemporaryDirectory(prefix='experiment-') as cwd:   # empty folder: no project CLAUDE.md, no files to read; removed at the end
        _run_series(a, conditions, msg, cwd)


def _run_series(a, conditions: list[str], msg: str, cwd: str):
    out = E / 'runs'
    if not a.dry_run: out.mkdir(exist_ok=True)
    version = None if a.dry_run else cli_version(a.claude_bin)
    for model in a.models.split(','):
        for cond in conditions:
            sp = (E / 'conditions' / f'{cond}.md').read_text().strip()
            for i in range(1, a.n + 1):
                f = out / f'{cond}-{model}-{i}.json'
                cmd = [a.claude_bin, '-p', *CLEAN, *shlex.split(a.extra), '--model', model, '--system-prompt', sp, '--output-format', 'json', msg]
                shown = [('<system_prompt>' if c == sp else '<user_message>' if c == msg else c) for c in cmd]
                if a.dry_run: print('would run:', ' '.join(shlex.quote(c) for c in shown), '->', f.name); continue
                if f.exists(): print('skip', f.name); continue
                t0 = time.time(); started = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
                try:
                    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=a.timeout, stdin=subprocess.DEVNULL)
                    rc, so, se = r.returncode, r.stdout, r.stderr
                except subprocess.TimeoutExpired as e:
                    rc, so, se = 'timeout', (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or ''), f'timeout after {a.timeout}s'
                try: cli = json.loads(so)
                except Exception: cli = None
                rec = {'condition': cond, 'run': i, 'model_alias': model, 'started': started, 'seconds': round(time.time() - t0, 1),
                       'cli': version, 'command': shown, 'system_prompt_file': f'conditions/{cond}.md', 'system_prompt': sp, 'user_message': msg,
                       'returncode': rc, 'stdout_raw': so, 'stderr': se[-2000:],
                       'result': (cli or {}).get('result') if isinstance(cli, dict) else None,
                       'model_usage': list(((cli or {}).get('modelUsage') or {}).keys()) if isinstance(cli, dict) else []}
                f.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n')
                print(f.name, rec['seconds'], 's |', (rec['result'] or se or '')[:160].replace('\n', ' '), flush=True)


def analyze(expected: list[str]):
    rows = []
    for f in sorted((E / 'runs').glob('*.json')):
        d = json.loads(f.read_text()); s, ok, ans = score(d.get('result'), expected)
        rows.append({'file': f'runs/{f.name}', 'condition': d['condition'], 'alias': d['model_alias'],
                     'model': d['model_usage'][0] if d.get('model_usage') else d['model_alias'], 'run': d['run'],
                     'score': s, 'ok': ok, 'answers': ans, 'returncode': d['returncode']})
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in rows: groups.setdefault((r['condition'], r['alias']), []).append(r)
    q = len(expected)
    L = ['# Results', '', f'Generated by `run.py --analyze-only` from {len(rows)} files in `runs/`. Do not edit by hand: rerun.',
         f'Score = correct answers out of {q} (`run.py: score()`). "Unparsed" = no JSON answer list; counted, not scored.', '',
         '| condition | model | runs | unparsed | mean score | min–max | per question correct |', '|---|---|---|---|---|---|---|']
    for (cond, alias), rs in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        sc = [r['score'] for r in rs if r['score'] is not None]
        per = [sum(1 for r in rs if r['ok'] and r['ok'][i]) for i in range(q)]
        model = rs[0]['model']
        mean = f'{statistics.mean(sc):.2f}' if sc else '-'
        rng = f'{min(sc)}–{max(sc)}' if sc else '-'
        L.append(f'| {cond} | {model} | {len(rs)} | {len(rs) - len(sc)} | {mean} | {rng} | {" ".join(f"Q{i + 1}:{n}" for i, n in enumerate(per))} |')
    L += ['', '## Every run', '']
    for r in rows:
        L.append(f"- `{r['file']}` ({r['model']}, {r['condition']}): score {r['score'] if r['score'] is not None else 'unparsed'}"
                 f"{'' if r['returncode'] == 0 else ', returncode ' + str(r['returncode'])}; answers {r['answers']}")
    L += ['', '## Reading it', '', 'Compare the gap between conditions with the min–max spread inside each condition.',
          'A gap smaller than the spread is "no effect seen", not "the advice works". See `hypothesis.md` for what was decided in advance.']
    (E / 'results.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:6 + len(groups) + 2]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--models', default='haiku,sonnet')
    ap.add_argument('--n', type=int, default=5)
    ap.add_argument('--only', default='', help='comma-separated condition names (default: every conditions/*.md)')
    ap.add_argument('--claude-bin', default='claude')
    ap.add_argument('--extra', default='', help='extra CLI flags, e.g. "--setting-sources \'\'"')
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--analyze-only', action='store_true')
    a = ap.parse_args()
    expected = json.loads((E / 'task/expected.json').read_text())['answers']
    if not a.analyze_only:
        conds = a.only.split(',') if a.only else sorted(p.stem for p in (E / 'conditions').glob('*.md'))
        missing = [c for c in conds if not (E / 'conditions' / f'{c}.md').exists()]
        if missing: raise SystemExit(f'no such condition: {missing}')
        run_series(a, conds, (E / 'task/prompt.md').read_text().strip())
    if not a.dry_run and (E / 'runs').is_dir(): analyze(expected)


if __name__ == '__main__':
    main()
