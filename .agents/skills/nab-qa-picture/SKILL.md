---
name: nab-qa-picture
description: Use when inspecting frames, contact sheets, clipping, caption collisions or empty visual areas in a rendered video from not-a-blogger; not for rebuilding it.
---

# Review rendered frames

Use [AGENTS.md](../../../AGENTS.md) in the not-a-blogger checkout. Input: exact final MP4/hash and the brief,
plus existing sheets if they identify this version. With no video, assess only the supplied images/report and state that scope.

Follow [final contact-sheet review](../../../recipes/qa/qa-contact-sheet-final.md): extract frames from the encoded
file, inspect sheets yourself, then open suspicious timestamps at full size. Use
[frame fill](../../../recipes/qa/qa-frame-fill-mp4.md) and
[motion diagnostics](../../../recipes/qa/qa-motion-metric-is-a-hint.md) as supporting evidence, not artistic verdicts.
Check object/action legibility, cropping, overlays, caption space, empty starts and the promised last frame.

Choose sampling for the suspected defect; sparse samples can miss flashes and a still frame cannot prove motion.
If images cannot be opened in this environment, state it. Do not claim continuous viewing, lip sync, sound quality
or audience response from contact sheets. Source dry frames do not establish the final MP4.

Output: reviewed file/hash, sample timestamps/paths, findings with exact frames and limits of coverage. Suggest
focused fixes; inspection alone does not authorize applying them or rerendering. No voice regeneration, full build
or publication as a side effect of a frame-review request.
