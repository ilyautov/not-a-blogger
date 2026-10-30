# QA

Frame metrics, ASR, contact sheets, readiness statuses. Recipes follow the [template](../../templates/recipe.md).
Every number a check fails on (loudness, true peak, stillness, ASR floor, frame fill) lives in one table:
[QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md). Recipes quote it, they don't redefine it.

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [ASR per take with topic vocabulary](qa-asr-per-take.md) | proven | ru | large-v3 with topic vocabulary, not the line text; a term misheard in 12 of 12. |
| [Review the final contact sheet yourself](qa-contact-sheet-final.md) | proven | any | fps=1/4 tile=6x6 on the final mp4, review it yourself even with green agent QA; 26 % half-empty frames passed audio verify. |
| [Review mid-scene frames before render](qa-dry-frame-review.md) | proven | any | 104 frames before render: 6 layout defects and 2 invented numbers. |
| [Measure frame fill on the mp4](qa-frame-fill-mp4.md) | proven | any | Empty frames and 16×8 grid on the mp4; 22% empty with green QA. |
| [Green QA is not approval](qa-green-is-not-approval.md) | proven | any | Technically built ≠ accepted ≠ cleared to publish. |
| [ffmpeg preflight](qa-preflight-ffmpeg.md) | hypothesis | any | blackdetect, freezedetect, scene detection, ebur128; VLM only with a checklist. |
| [Stillness lint with camera off](qa-still-lint.md) | proven | any | ≤ 3 s per scene, camera off, word timestamps required. |
| [Word-timestamp sync check](qa-word-sync-check.md) | hypothesis | any | Plate within ±0.3 s of its noun, a cut every 3 s, captions uncovered; 3–25 failures per finished video. |
| [Treat the motion metric as a hint, not a gate](qa-motion-metric-is-a-hint.md) | proven | any | 18 videos with human verdicts: neither fast_ratio nor active_ratio separates approved from rejected; one alarm only. |
| [Gate the voice before showing](qa-voice-gate.md) | proven | any | TP ≥ −2.5 dBTP, LRA ≥ 2.5, gap σ ≥ 0.1 s, ≤ 6.3 syll/s, F0 ≤ 250 Hz; diagnostic, not a verdict. |
