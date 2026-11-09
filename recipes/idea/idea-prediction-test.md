---
id: idea-prediction-test
title: Let a fresh agent predict the five obvious videos on the topic, then drop candidates that overlap them or your past
section: idea
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [Python, Claude Code]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
The person gave a topic and you are about to pitch ideas. Your first ideas are the ones anyone would have, and you
do not see that you already made a similar video two months ago.

## Do
1. Start the prediction right away, in parallel with your own sketches: a fresh agent gets only the topic in the
   person's words and writes five expected videos (plot, key frames, form, ending).
2. Sketch 8–10 angles, drop the first three, keep up to five that are unexpected but true to the material. One line
   each in `research/candidates.md`: `number | logline | key frames | world | form | ending`.
3. Keep a list of your past videos as CSV or JSON (`title` and/or `logline`, ideally `first_line`, `last_line`).
4. Run the overlap check with a second fresh agent. Verdicts: CLEAR → work on it; SHARES → change the repeated
   element (ending, form, key frame, world or opening); OVERLAP → drop it, don't argue.
5. Show the person 2–3 strongest non-OVERLAP candidates, each with one phrase on what it does that the predicted
   five don't. Fewer than two left: write new candidates and check again.

```bash
python3 tools/script/predict_check.py predict --topic "<the person's words>" --out research --run
python3 tools/script/predict_check.py overlap --topic "<same>" --candidates research/candidates.md \
        --past my-videos.csv --out research --run
python3 tools/script/predict_check.py summary --out research
```

Without `--run` the tool writes `*.prompt.txt` for any agent without your context
([prediction prompt](../../prompts/script/prediction-test.md), [overlap prompt](../../prompts/script/overlap-check.md)).

## Verify
`research/predict.md` was written before `research/candidates.md` existed (file times), and every candidate shown to
the person has a CLEAR or SHARES line in `research/overlap.md`, with the SHARES element changed.

## Don't
- Don't let the predicting agent see your candidates, brief or notes: it will predict you, not the obvious.
- Don't treat a verdict as a ban when the person asked for a sequel on purpose.
- Don't count what the topic itself names (the product, the place) as a repeat.

## Evidence
- Viewer feedback: a video built as a copy of a successful one on the same skeleton was rejected by the person as
  slop, even with a new topic; a reel made on a "top-3 template" was called AI slop.
- One run of this test (topic: an AI that makes up passwords): the author's most obvious candidate came back OVERLAP
  with predicted P1 and with a video the author had already made.
- No count yet of how many shown ideas the person accepted with and without the test; to promote, compare 10 pitches.
- Method retold from sarpstar/cinecode (MIT), `references/writing.md` and `scripts/brief.py`; code is our own.

## Related
- [≥ 4 of 6 parameters differ from the reference](idea-four-of-six-differ.md)
- [Don't make a sequel on the same template](idea-no-repeat-own-hit.md)
- [Script before build](idea-script-before-build.md)
