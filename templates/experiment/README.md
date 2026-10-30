# experiment: test a piece of advice by running it

> **Costs money.** A bare `python3 run.py` makes N paid `claude -p` calls on your account: 2 conditions × 2 models × 5 runs
> = **20 calls by default**. Start with `python3 run.py --dry-run` (prints the commands, calls nothing), then
> `--models haiku --n 1` for one smoke run per condition.

"Add X to your prompt and the model does Y" is a claim you can check in an evening. This template runs the advice
and a control side by side through `claude -p`, N times per model, keeps every raw answer, and builds a table.
The reel then tells what happened, with `runs/*.json` as the receipt.

The example: does *"This is very important for my career"* in the system prompt make the model answer five
questions with known answers more accurately? Replace it with your own advice.

## When to use it

- A viral tip about prompts, models or agents that can be reduced to "with it / without it".
- A reel or post whose punchline is a result. Run first, write the script after: the script follows the data.
- Not for questions of taste ("which answer is nicer"): you need an answer key or a check a script can do.

## Run

Needs Python 3.10+ and Claude Code (`claude` on PATH, logged in). No other dependencies.

```bash
cd templates/experiment
python3 run.py --dry-run                     # see exactly what will be called, nothing runs
python3 run.py --models haiku --n 1          # one smoke run per condition
python3 run.py --models haiku,sonnet --n 5   # the series you decided on in hypothesis.md
python3 run.py --analyze-only                # rebuild results.md from runs/
```

20 calls at default settings take a few minutes. An interrupted series resumes: existing `runs/*.json` are skipped.
To start over, move `runs/` away (do not mix runs from different setups in one table).

## Layout

| File | Role |
|---|---|
| `hypothesis.md` | the advice, the testable claim, models, N and scoring, **written before the first run** |
| `conditions/*.md` | one system prompt per condition. `A-control.md` and `B-advice.md` differ only by the advice |
| `task/prompt.md` | the user message, identical for every condition |
| `task/expected.json` | the answer key, one per question |
| `run.py` | the runs (clean flags, empty temp cwd, stdin closed, JSON output), then scoring and `results.md` |
| `runs/<condition>-<model>-<i>.json` | raw record: command, prompts, CLI stdout, stderr, return code, CLI version, timing |
| `results.md` | generated table: runs, unparsed, mean score, min–max, per-question correct, then every run |

## What to replace

1. `hypothesis.md` first. Fix models, N and the success criterion before you see any output.
2. `conditions/`: keep one control that is the same prompt without the advice. More conditions are fine
   (`C-advice-twice.md`); each file is picked up automatically.
3. `task/prompt.md` and `task/expected.json`. Verify the key by code where you can (the example's arithmetic and
   weekday were checked with Python).
4. `score()` in `run.py` if your check is not "exact answer per question": a regex, a JSON field, a unit test.
   After changing it, read a few runs by hand and count false positives and negatives in the control.

## Gotchas

- **Clean runs or nothing.** Without `--safe-mode --tools "" --strict-mcp-config` and an empty cwd, your CLAUDE.md,
  plugins, MCP servers and project files become part of every condition. Flags get renamed between CLI versions:
  check them in `claude --help` and pass extras via `--extra`.
- **stdin closed.** `claude -p` started from a script can hang waiting for stdin; `run.py` passes `/dev/null`.
- **No seed, default sampling.** Two identical runs can differ; that spread is your noise floor. Report min–max,
  not only the mean, and do not call a gap smaller than the spread an effect.
- **A control condition is not optional.** The original experiment this was ported from added a plausible control
  case after the absurd one, and it changed what could honestly be said.
- **Regex scoring lies quietly.** When the score is "did the answer mention X", run the regex on the control and
  count false positives before trusting it.
- **Keep every run.** Timeouts, unparsed answers and errors go into the table. Picking runs is the fastest way to a
  false reel.
- **Say the limits in the video**: these models, this CLI version, these prompts, this day. Not "AI in general".
- **Do not test on real people or real systems.** No real résumés, accounts, companies or someone else's bot. Use
  made-up inputs and your own prompts.
- **Subscription vs API.** `total_cost_usd` in the CLI JSON is a reference price; whether it is billed depends on
  how you are logged in. Check before running hundreds of calls.

## Related recipes

- `../../recipes/agent/agent-clean-run-setting-sources.md`: what leaks into a "clean" run
- `../../recipes/agent/agent-stdin-dev-null.md`: why stdin is closed
- `../../recipes/agent/agent-evidence-log-wording.md`: word claims to match the log
- `../../recipes/idea/idea-factcheck-file.md`: keep the receipts next to the reel
