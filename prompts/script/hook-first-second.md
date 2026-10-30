# First-second hook on three tracks

- **Purpose:** design the first second of a video on picture, voice and caption at once, with a result or a conflict
  at second zero.
- **Where tested:** Claude Code, while preparing scripts for short videos.
- **Status:** hypothesis. The "result at 0.0 s" rule grew out of feedback on weak openings; no A/B test against the
  earlier hooks was run.

## Prompt

```text
Suggest 5 options for the first second of a video on the topic "{topic}" ({duration} s, hero {character}).
Write the voice line and the caption in {language}.

Each option has three tracks, and they do NOT repeat the same phrase:
- Picture: something odd or an action that is clear without sound within a fraction of a second.
- Voice: one short line containing a conflict or a stake. No status updates, no greetings.
- Caption: 2–5 words that help understand the picture without sound.

Second zero must carry one of three types: a finished result, a scandal or an intrigue. Context and explanation
move to seconds 3–5.

The hook promises only what the video actually shows at the end. For each option, name the final shot that delivers
on the promise. No such shot = strike the option.

Forbidden: "Remember this phrase", "Let me tell you", "First, second, third", the question "Did you know...?".
At the end, pick the best option and explain the choice in one line.
```

## Why

Three tracks give the viewer scrolling without sound and the viewer with sound different information instead of one
phrase three times. Tying the hook to the final shot cuts clickbait that promises more than the video has. Moving
context to seconds 3–5 removes the most common opening, "first let me explain what this is about".

## Pitfalls

- A hook written before the material promises something the video does not have. Material and resolution first,
  hook second.
- An opening like "here is what I tested today" was called weak by the author: it has no result, only an
  announcement.
- If the material gives no strong first shot, change the angle of the story instead of slipping in a pretty
  background.
