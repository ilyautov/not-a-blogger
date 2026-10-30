---
id: qa-preflight-ffmpeg
title: Run the final through blackdetect, freezedetect, scene detection and ebur128
section: qa
lang: any
status: hypothesis
evidence: experience
tools: [ffmpeg, PySceneDetect]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Black frames, frozen stretches and off-target loudness are spotted by eye after publishing. A free-prompt VLM judge gives false positives.

## Do
1. Run structural checks before any VLM: black and frozen frames, detected cuts vs planned cut points, loudness.
2. Crop the caption strip before `freezedetect` if captions are burned in.
3. If you add a VLM critic, give it the contact sheet and a question checklist, not a free "rate the video".

```bash
ffmpeg -i final.mp4 -vf "blackdetect=d=0.3,freezedetect=d=2" -an -f null - 2>&1 | grep -E "black_|freeze_"
scenedetect -i final.mp4 detect-content list-scenes -o qa/
ffmpeg -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```

## Verify
No unexpected black or frozen stretches; detected cuts match the plan; loudness on target.

## Don't
Don't expect `freezedetect` to catch a frozen frame with changing burned-in captions unless the strip is cropped.

## Evidence
No own measurements: set taken from a review of local QA tools. The 2026 benchmark conclusion it relies on: a free VLM judge gives false positives, a checklist fewer.

## Related
- [Loudness like hits](../sound/sound-loudness-like-hits.md)
- [Final contact sheet](qa-contact-sheet-final.md)
