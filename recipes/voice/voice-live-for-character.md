---
id: voice-live-for-character
title: Give the lead role to a live voice, keep synthesis for secondary characters
section: voice
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [OmniVoice, Chatterbox, F5-TTS]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A character with personality (boss, skit hero) needs a voice, and synthesis by description or a clone gives flat, "sad" prosody.

## Do
1. Voice the skit hero live, recorded on a phone.
2. Synthesize secondary characters (assistant, mascot); flat delivery is acceptable there.
3. One meme shout in the ending may be synthetic, optionally stretched.
4. If the hero must be synthetic, use an actor reference with the right delivery: the reference sets the character, not an "emotion" knob.

## Verify
The listener does not call the hero's voice "sad" or "bad dubbing".

## Don't
- Don't try to fix flat prosody with timbre or exaggeration settings.
- Weight licenses: F5-TTS_RUSSIAN CC BY-NC 4.0, OmniVoice CC BY-NC. For commercial use pick an Apache-2.0 engine (e.g. VoxCPM2).

## Evidence
- Boss character: three synthesis versions (OmniVoice by description twice, Chatterbox clone at exaggeration 2.0), all rejected as "sad". Chatterbox exaggeration barely mattered.
- Talking head on an F5 clone: six variants (different references, with/without speed-up, with/without enhancer), all rejected.
- Skit "live hero + synthetic secondary + shout at the end" accepted as "turned out great".
- One listener's ratings; no publication metrics to compare.

## Related
- [Clean reference](voice-record-reference-clean.md)
- [Stretch a shout](voice-stretch-word.md)
- [Talking head on LTX](../face/face-ltx-a2v-local.md)
- Example: [I handed my Instagram to the agent](../../examples/instagram-to-claude-skit/README.md)
