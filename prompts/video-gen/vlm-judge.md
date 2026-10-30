# VLM take judge

- **Purpose:** a multimodal model compares frames of two or more takes of the same shot and picks the best one, so a
  human does not have to review every take.
- **Where tested:** nowhere end to end yet. A manual version of these checks (face, mouth, blur, no more than two
  reruns) was used in builder briefs for generative shots.
- **Status:** hypothesis.

## Prompt

```text
You are looking at frames from {N} takes of the same shot. Each take has 6–8 evenly spaced frames, files named take-<number>-<frame>.png.
The shot must show: {character}, {action}, {duration} s.
Character passport: {passport}.

Rate each take on each item, answer "yes/no" plus the number of the evidence frame:
1. Face and clothing match the passport in every frame (no drift, no change).
2. The described action actually happens, not just a camera push-in.
3. The mouth moves only if the shot has speech; with speech, the mouth is in sync (judge by opening phases).
4. No blur ("soap"), extra fingers, fused limbs, melting objects.
5. The camera behaves as specified (stays still if a static camera was requested).
6. No text, logos, watermarks.

Output strictly JSON:
{"best": <number>, "takes": [{"take": <number>, "fails": [<item numbers>], "evidence": "<frame and what is visible>"}],
 "rerun": true|false}
"rerun": true only if no take passed items 1–4.
```

Rule around the judge: no more than two reruns of a shot with a new seed. If that does not help, change the prompt
or solve it in the edit.

## Why

Reviewing generative takes eats more time than the generation itself. Binary items with a frame number can be
checked by a human in seconds, while a free-form "which take is better" gets decided by the model on beauty rather
than on the task. The rerun limit keeps you from burning an evening on seed roulette.

## Pitfalls

- Lip sync cannot be judged reliably from 6–8 frames. Item 3 is only a rough filter; the final call on lips belongs
  to a human watching the clip.
- If several takes pass every item, leave the choice to a human: in a free comparison the model judges on beauty,
  not on the task.
- Assumption, untested: a judge from the same model family as the generator may forgive its own typical artefacts.
  If you have a choice, use a judge from a different family.
