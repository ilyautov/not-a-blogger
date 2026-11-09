# Overlap check: candidates against the obvious and against your own past

- **Purpose:** a fresh agent compares each idea candidate with the five predicted videos
  ([prediction-test.md](prediction-test.md)) and with a list of your past videos, and returns one verdict
  per candidate: CLEAR, SHARES (one element repeats) or OVERLAP (the premise repeats).
- **Model or agent:** any model started without your session. `tools/script/predict_check.py overlap`
  fills `{candidates}`, `{predict}` and `{past}` from files (`--past` is any CSV or JSON with `title` and/or
  `logline` columns) and, with `--run`, calls `claude -p` from an empty folder.
- **Where tested:** one run on one topic: the author's most obvious candidate came back OVERLAP with P1 and
  with a video the author had already made.
- **Status:** hypothesis (one run).

## Prompt

```text
You check short-video ideas for banality and self-repetition. You did not write the ideas.
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
No introduction, only the lines for the candidates.
```

## Why

- "Whatever the topic itself names is not a repeat" stops the judge from flagging every candidate for
  mentioning the product the person asked about.
- Three verdicts instead of a score: SHARES tells you which element to change, OVERLAP tells you to drop
  the idea. A number would invite tuning the idea until the number moves.
- Past videos go in as one line each with first and last lines: the repeat is usually in the opening or the
  ending, not in the title.

## Pitfalls

- The judge must not be the agent that wrote the candidates: it defends its own ideas.
- A list of past videos that only has titles misses repeats of form and ending; add `first_line`,
  `last_line` or `ending` columns when you can.
- Treat the verdict as a replacement generator, not a gate: when the person asks for a sequel on purpose,
  OVERLAP is expected.
