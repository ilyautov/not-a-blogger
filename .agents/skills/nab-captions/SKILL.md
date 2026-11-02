---
name: nab-captions
description: Use when exporting SRT/VTT or adjusting on-screen caption text, word timing or layout from existing speech in not-a-blogger; not for resynthesizing the voice.
---

# Captions from existing speech

Read [AGENTS.md](../../../AGENTS.md) in the not-a-blogger checkout. Input: approved words, actual word timings,
target frame and desired output: SRT/VTT or captions burned into a scene/video. Keep existing voice and unrelated scenes.

For subtitle files, use the existing exporter described in [tools/README.md](../../../tools/README.md):

```bash
python3 tools/captions/to_srt.py voice-track.json --srt output/final.srt --vtt output/final.vtt
```

Replace the example paths with supplied artifacts; this exports files, not a new MP4. Check text, ordering, gaps
and line boundaries against the input. Missing alignment is a missing input, not permission to guess word timing.

For burned captions use [caption recipes](../../../recipes/captions/README.md) and
[word/overlay checks](../../../recipes/qa/qa-word-sync-check.md). Check actual font size, safe space, contrast,
overlaps and cache invalidation in the changed frames. Preserve spoken wording; propose discrepancies instead of
silently rewriting speech to match a prettier subtitle. Separate source-frame checks from final encoded-file checks.

Output: subtitle files or a scoped caption change, changed timestamps/text and what was inspected. State explicitly
whether a new MP4 was produced. Do not resynthesize speech, replace artwork or run a full rebuild for an SRT-only request.
