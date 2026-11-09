# Prediction test: the five videos everyone expects

- **Purpose:** before you pick an idea, a fresh agent that knows only the topic writes the five most obvious
  videos on it. Your candidates are then compared with them (see [overlap-check.md](overlap-check.md)).
- **Model or agent:** any chat model or CLI agent started without your session, memory or project files.
  `tools/script/predict_check.py predict --run` calls `claude -p` from an empty folder with no settings and no tools.
- **Where tested:** one run on one topic (an AI that makes up passwords). The most obvious candidate of the
  author matched the predicted P1, and the author had already made that video.
- **Status:** hypothesis (one run, no count of ideas saved).

## Prompt

```text
You are given only the topic of a short vertical video (Reels/Shorts, 15-40 s). Nothing else is known.
Topic: "{topic}"

Write five videos on this topic that any viewer and any author would expect: the most obvious ones, the
first that come to mind. One line per video, strictly in this format:
P1 | plot in one sentence | key frames (2-3) | form (skit / list / how-to / breakdown / experiment / motion) | ending
...
P5 | ...
No introduction and no explanations, only five lines.
```

## Why

- "Only the topic" is the whole point: an agent that saw your brief, your notes or your candidates predicts
  your ideas, not the obvious ones.
- The fixed line format (`P1 | plot | key frames | form | ending`) lets the overlap judge point at a
  specific element, not at a vibe.
- Five, not three: the first three are what you would also write first; four and five show where the
  obvious space ends.

## Pitfalls

- Pasting the topic in your own paraphrase leaks your angle into the prediction. Quote the person's words.
- Running it after your candidates exist tempts you to argue with it. Run it in parallel with your first
  sketches, before you choose.
