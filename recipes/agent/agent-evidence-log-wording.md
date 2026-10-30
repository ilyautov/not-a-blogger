---
id: agent-evidence-log-wording
title: Ask the agent for an evidence log, not for its reasoning
section: agent
lang: any
status: hypothesis
evidence: experience
tools: [Claude Code, API]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The video needs the agent's line of thought (how it located a place from a photo, why it picked this product). A prompt like "your reasoning will be in the video" triggers the API's reasoning-extraction safeguard; the answer is cut, agents fail.

## Do
Ask for an external artifact: an observation log the agent writes to a file as it works. Show this file on screen, line by line, like terminal typing.

```text
While working, keep EVIDENCE.md: one clue per line
(what you saw, where in the photo, what follows, confidence in %).
At the end: the conclusion and which clues support it.
```

## Verify
Runs don't end with a safeguard error; EVIDENCE.md with numbered clues appears.

## Don't
- Don't present the log as the model's verbatim computation: it is what the agent chose to write. Say so in the video.

## Evidence
With the "reasoning in the video" wording agents failed on the reasoning-extraction safeguard; with the "evidence log" the same blind test on two photos passed (misses of 444 m and 53.7 km were reported honestly in the video). Failure rate not counted.

## Related
- [Agent works on copies](agent-work-on-copies.md)
- Example: [Claude geolocates a photo, blind-tested](../../examples/photo-geo-blind-test/README.md)
