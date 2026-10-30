# Script from material, not from a scene

- **Purpose:** the agent writes a short-video script starting from a real object (a log, a screen recording, a test
  result, an email), not from a pretty scene.
- **Where tested:** Claude Code, Codex CLI.
- **Status:** hypothesis. The method was assembled after a teardown of a rejected video and a couple of dozen open
  repositories with scripts; it has not yet been compared on published statistics.

## Prompt

```text
Write a script for a short vertical video on the topic "{topic}", about {duration} s long.
Host or hero: {character}.
Write the script in {language}.

Work order, do not reorder the steps:
1. Material. Name the real object the viewer will see for themselves: a screen recording, a log, a test result,
   an email, a receipt, a page of the primary source. If there is no such object, stop and write what material
   needs to be obtained. Do not draw invented evidence.
2. Viewer. One sentence: who finds this familiar, and what question they will have after the first frame.
3. Knowledge chain: event → what looks like the explanation → new evidence → change in understanding → verifiable
   outcome. Each next shot adds a fact, an action or a stake. If two neighbouring shots can be swapped without
   losing meaning, it is a list of illustrations; redo it.
4. Delivery. Pick one way of showing for the whole video: an observable action, a comparison, revealing a
   document, a face and a reaction, a screencast.
5. Only now the text. Numbers and evidence stay on screen; causality, judgement and the twist go to the voice.
   Do not read the screen aloud.
6. The resolution answers exactly the question from the hook and shows the source. A slogan instead of proof is
   not accepted.
7. Fit the duration to the material: cut repetitions and introductory explanations. Keep a call to action only if
   the viewer has a real action or resource.

Output: a "what the viewer now knows" table (see the neighbouring prompt), then the spoken text line by line.
Show me the script before any build.
```

## Why

A video built from a scene passes technical QA and still feels synthetic: there is no event worth watching. Step 1
with its stop condition cuts such topics before voice and render are spent on them. The swap test catches a
"slicing of theses" mechanically, without arguments about taste.

## Pitfalls

- The first version of the video whose teardown gave birth to the method explained the cause by second 6. There was
  no reason to keep watching, and no cuts or music fixed that.
- The agent happily "finds" material in its own imagination. Require a link or a file for every object from step 1.
- Do not invent a retention threshold up front. Compare with your own videos of the same length and topic, not with
  a single hit.
