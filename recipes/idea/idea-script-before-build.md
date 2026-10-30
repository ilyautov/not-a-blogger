---
id: idea-script-before-build
title: Show a 3–5 line script and the viewer-knowledge chain before building; don't reuse a hit's skeleton
section: idea
lang: any
status: proven
evidence: measurement
tools: [text editor]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
Before voice synthesis or rendering of any new video. Two failure modes: a script first seen in the edited video costs a full rebuild to change; and a successful video tempts you to clone it (same background, card, block order, new topic), so by episode three viewers see the assembly line.

## Do
1. Before voice and render, show the approver: a 3–5 line script (hook, turn, punch, ending), the first frame, one storyboard of the key frame. Build only after "OK".
2. Before prose, write the knowledge chain: event → apparent explanation → new evidence → changed understanding → verifiable outcome.
3. Swap test: swap two adjacent shots. If causality survives, it is a list of illustrations, not a story.
4. Before each scene ask: was this visual world in the two previous videos? If yes, invent a new one: genre parody (court, checkout, messenger, noir), an object from the story, not a text card. Embed jokes and numbers into scene objects, not overlay plates.
5. Cut a 6–10 s rough assembly from real frames and watch muted: is the conflict visible in frame 1, is there a new fact by second 5?

```text
Hook:   The agent shut down prod on Friday night.
Turn:   The on-call pager, incident statuses as dialogue.
Punch:  The survey number on the pager screen.
Ending: Question to the viewer + codeword.
Frame:  close-up of the pager on the nightstand, 03:12 on the clock.
```

| Time | What the viewer now knows | Frame | Speech | On-screen text | Evidence | Next question |
|---|---|---|---|---|---|---|
| 0–? | what oddity they see | | | | | why did it happen? |
| ?–? | why it matters | | | | | what do we test? |
| ?–? | what changed the version | | | | | what did it lead to? |
| end | answer to the first question | | | | | loop closed |

## Verify
Script approved as text before the first render. Each table row adds new knowledge; the ending answers exactly the question of the first frame. No two of the last three videos share a skeleton.

## Don't
- Don't treat green automated checks as approval of the idea.
- Don't repeat a whole scene. A series frame (rubric, refrain) is fine if the situation inside changes.

## Evidence
- A video that passed 15 green automated checks was still rejected by the approver.
- The third video in a row on one skeleton (dark background, text card, mascot in a circle, plate) was rated "slop".
- The next batch of five, each with its own scene and genre: three of five got the top rating, one "format ok", one "a bit boring, unclear". Counted approver ratings before and after the rule (1 of 3 accepted vs 3 of 5), same approver; no retention measurement on published videos.
- The knowledge-chain table and swap test come from open screenwriting repos and platform docs; their own effect on retention is not measured.

## Related
- [Don't repeat your own hit](idea-no-repeat-own-hit.md)
- [Green QA is not approval](../qa/qa-green-is-not-approval.md)
- [One example per reel](idea-one-example-short-reel.md)
- [Don't treat "clean" as a living script](../text/text-scanner-misses-form-slop.md)
- [Review the final contact sheet yourself](../qa/qa-contact-sheet-final.md)
