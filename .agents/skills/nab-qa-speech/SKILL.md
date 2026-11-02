---
name: nab-qa-speech
description: Use when checking spoken wording, take alignment, pauses, voice regressions or word-linked overlays in not-a-blogger; not for generating replacement takes.
---

# Check speech and alignment

Read [AGENTS.md](../../../AGENTS.md) in the not-a-blogger checkout. Input: exact final audio/video, approved
script, take timings/ASR and clean voice track where needed. Bind reports to this version's hash.

Use [per-take ASR](../../../recipes/qa/qa-asr-per-take.md),
[voice gate](../../../recipes/qa/qa-voice-gate.md) and
[word sync](../../../recipes/qa/qa-word-sync-check.md) with the actual build artifacts. Respect language-specific
normalization and the [threshold table](../../../docs/QA-THRESHOLDS.md). A pitch profile calibrated on one voice is
not a universal pass rule; music can invalidate pitch measured from a mixed track. Heuristic sync warnings remain warnings.

Separate recognized text, measured timing/levels and actual listening. ASR does not measure stress or comic delivery.
Without usable speech, alignment, dependencies or a clean stem, report the relevant check as unavailable. Fake tones
and `--no-asr` cannot establish spoken-word accuracy; preserve partial status. For report-only requests, don't claim
you listened to an unavailable file.

Output: per-line mismatches/timestamps, measured values, declared normalization and missing checks. Propose take
repair or caption/timing fixes with affected lines, but do not resynthesize, retime the whole track, render or publish
while performing this inspection. Human voice/artistic acceptance remains separate.
