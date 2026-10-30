---
id: hooks-voice-by-045
title: Show the background from frame 0 and start the voice by 0.45 s
section: hooks
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [GSAP, ffmpeg]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The video opens on an empty frame or silence: background fades in, voice starts after a second.

## Do
1. Background and main object visible at frame 0, no fade from black.
2. Captions animate in from 0.15 s.
3. Voice starts no later than 0.45 s.
4. Rewrite a conditional first line ("If you…") as a statement.
5. Set everything visible at frame 0 in CSS, not via a tween from zero.

```js
// everything visible at frame 0 already has opacity:1 in CSS
tl.from(".hook-line", { y: 40, opacity: 0, duration: 0.35, stagger: 0.08 }, 0.15);
// voice track offset 0.45 s:
// ffmpeg -i voice.wav -af "adelay=450|450" voice_d.wav
```

## Verify
Frame 0 export (`ffmpeg -i final.mp4 -frames:v 1 f0.png`) is not empty; first ASR word starts before 0.45 s.

## Don't
Don't treat 0.45 s as a ceiling to aim for: in niche hits the first word is at 0.0 s.

## Evidence
- Original cut: voice at 1.2 s. After moving it to 0.45 s, together with a first-second hit and a closing question, the video was accepted and published on three platforms. The voice's separate contribution was not measured.
- Another video with the voice not starting on frame 1 got this remark despite overall praise.
- 0.45 s is the value found for one video, not a retention measurement.

## Related
- [Hook in the first second](hooks-result-in-first-second.md)
- [Empty scene start](../assembly/assembly-no-empty-scene-start.md)
