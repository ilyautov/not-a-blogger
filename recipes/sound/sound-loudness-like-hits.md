---
id: sound-loudness-like-hits
title: Master the final to −15 LUFS ±1 with dense music and no dips
section: sound
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, ebur128]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The video is quieter than neighbours in the feed, music drops out or covers the voice, silent gaps between lines.

## Do
1. Final loudness −15 LUFS ±1 integrated (window −16…−14), true peak ≤ −1.5 dBTP. Measure the encoded file, not the master. Values and their origin: [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md).
2. Music bed compressed: LRA 2–3 LU, no pauses.
3. Music under voice clearly quieter than voice; if listeners ask to lower it, drop the level (one case: 0.5 → 0.3).
4. No silence below −35 dB longer than 0.25 s.
5. Before using an EQ carve of music under voice, A/B it against a plain level drop at equal loudness.

```bash
ffmpeg -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|LRA:|Peak:" | tail -3
ffmpeg -i final.mp4 -af "silencedetect=n=-35dB:d=0.25" -f null - 2>&1 | grep silence_duration
```

## Verify
Integrated within −16…−14 LUFS, true peak ≤ −1.5 dBTP, bed LRA 2–3, `silencedetect` at −35 dB / 0.25 s finds nothing.
One command for the loudness and peak part: `python3 tools/qa/loudness.py final.mp4` (exit 1 outside the window).

## Don't
- Don't expect an EQ carve to fix clipped TTS or restore lost words; it is not verified on own voice.
- Don't reach the target through `tanh` or a soft clip: a too-low true peak at the right loudness means squashed peaks, see [no soft clip](sound-no-soft-clip-master.md). The floor is −2.5 dBTP.

## Evidence
- Seven analysed hits: −14.1…−14.7 LUFS; skits LRA 2–3 LU; no silence below −35 dB longer than 0.25 s in any video with speech.
- An open-source project demo: −13.68 LUFS and true peak −0.88 dBTP against a declared −1 ceiling: check the ceiling on the encoded file. AAC lifts peaks 1–2 dB over the master, hence the −1.5 dBTP ceiling (chosen, not measured as the exact safe value).
- Own published videos came out at −15.2…−15.3 LUFS. Hits and own videos both sit inside −16…−14; the starter enforces the same window as −15 ±1.

## Related
- [Loudness per take](../voice/voice-loudness-per-take.md)
- [Music rotation](sound-music-rotation.md)
- [No soft clip on the master](sound-no-soft-clip-master.md)
- [ffmpeg preflight](../qa/qa-preflight-ffmpeg.md)
