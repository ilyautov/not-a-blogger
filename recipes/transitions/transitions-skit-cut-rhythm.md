---
id: transitions-skit-cut-rhythm
title: Cut a skit every 1.5–2.5 s and show reactions in close-up
section: transitions
lang: any
status: hypothesis
evidence: measurement
tools: [ffmpeg, three.js]
learn: ../../learn/en/05-camera-editing.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A character skit is one static shot: dialogue runs, the frame stands, reactions are invisible.

## Do
1. Cut on lines, on average every 1.5–2.5 s.
2. Reactions get a face close-up (star eyes, horror, sweat drop).
3. A role label above each character.
4. One location that changes at plot turns.
5. Censor profanity with an asterisk and pop it in a red all-caps bar.
6. End with a meta twist instead of a call to action.
7. Smooth mouth animation, or frequent close-ups expose jitter.

```bash
# compare your rhythm with the reference
ffmpeg -i skit.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -c pts_time
```

## Verify
Cuts per duration are close to the reference; every reaction has a close-up.

## Don't
Don't treat these numbers as proven for your own videos: they describe other creators' hits.

## Evidence
- Analysed skit hit: 41 cuts in 67 s, about one per 1.6 s.
- Voxel skits at 710k and 178k views: 22 cuts in 49 s and 19 in 45 s, shot length 2.1–2.3 s.
- Effect of rhythm on own videos not measured.

## Related
- [Envelope smoothing for a 3D character](../face/face-3d-envelope-smoothing.md)
- [Remake the rhythm, not the words](../idea/idea-remake-rhythm-not-words.md)
