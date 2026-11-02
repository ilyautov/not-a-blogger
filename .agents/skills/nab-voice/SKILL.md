---
name: nab-voice
description: Use when recording, synthesizing, selecting or repairing spoken takes for an approved short-video script in not-a-blogger; not for music mixing or caption layout.
---

# Produce spoken takes

Read [AGENTS.md](../../../AGENTS.md) in the not-a-blogger checkout and the chosen build's voice instructions.
Input: approved lines, language, permitted voice/reference and configured engine. Establish missing setup before
promising a real voice; a fake tone demo is not speech synthesis.

Read [voice recipes](../../../recipes/voice/README.md), the relevant
[language pitfalls](../../../gotchas/README.md) and [TTS text rules](../../../prompts/voice/tts-script-rules.md).
Keep the chosen reference fixed, make one take per line and avoid changing tempo globally to fit the edit.
Check takes with [per-take ASR](../../../recipes/qa/qa-asr-per-take.md), then inspect tails, stress and pauses with
the available listening evidence. ASR cannot establish intonation or stress. Any rewording needs script approval.

Use existing [take tools](../../../tools/README.md) and the build's actual commands; inspect their help rather than
inventing another synthesis interface. Rebuild only affected takes. Record engine/reference identity, timing,
chosen take and what was not checked; no private reference audio belongs in a contribution.

Output: take paths, timing/alignment and selection/QA evidence, with any missing dependencies or checks. Do not
replace music, alter scenes/captions or render the whole video merely to repair a spoken line.
