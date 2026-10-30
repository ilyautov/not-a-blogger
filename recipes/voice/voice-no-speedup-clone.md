---
id: voice-no-speedup-clone
title: Don't speed up the clone; get tempo from short phrases
section: voice
lang: any
status: proven
evidence: ab-test
tools: [F5-TTS, ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The clone sounds too slow for a reel and you are tempted to raise the model `speed` (e.g. to 1.15).

## Do
1. Keep the model speed at 1.0.
2. Get tempo from text: short phrases, fewer fillers, gaps 0.5–0.8 s.
3. If a long video is slow overall, apply moderate `atempo` to the finished takes, not to generation speed.

```bash
# moderate speed-up of a finished take, only if unavoidable
ffmpeg -y -i line.wav -af "atempo=1.12" line_fast.wav
```

## Verify
Blind A/B of three speeds on one line: 0.9 / 1.0 / 1.15.

## Don't
- Don't raise generation speed: stress and intonation drift.
- If the text doesn't fit the reel length, cut text, not speed.
- F5-TTS_RUSSIAN weights are CC BY-NC 4.0.

## Evidence
- A/B speed 1.15 / 1.0 / 0.9: 1.0 chosen; 1.15 was called "awful".
- Long video on a calm reference, after "feels like it needs speeding up": rebuilt with `atempo` ×1.12 on finished takes and gaps 0.3 / 0.4 / 1.3 s: 9:53 → 8:34.

## Related
- [Gaps between lines](voice-gaps-between-lines.md)
- [Blind TTS bake-off](voice-blind-tts-bakeoff.md)
