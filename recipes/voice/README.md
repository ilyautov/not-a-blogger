# Voice and TTS

Speech synthesis (F5-TTS, OmniVoice and others), cleanup, pauses, stress, tails. Recipes follow the [template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [Choose the TTS engine by a blind numbered test](voice-blind-tts-bakeoff.md) | proven | any | Blind test by number; F5 and OmniVoice weights are non-commercial. |
| [F5 pauses: full stop or hard marker, not a dash](voice-f5-pauses.md) | proven | any | Full stop ≈0.43 s, dash/ellipsis ≈0.08 s; hard pause via ` \| `. |
| [Sacrificial, consonant-initial first word](voice-f5-sacrificial-first-word.md) | proven | ru | Long consonant-initial first word that isn't the lead token. |
| [Sacrificial tail word and alignment cut](voice-f5-tail-sacrificial-word.md) | proven | any | Append a tail word, cut at its start by alignment, 50 ms fade. |
| [Short gaps between lines](voice-gaps-between-lines.md) | proven | any | Gaps 0.5–0.8 s, one long breath before the punch. |
| [Live voice for the lead, synthesis for secondary roles](voice-live-for-character.md) | hypothesis | any | Hero recorded live, synthesis for side characters. |
| [Normalise every take to −16 LUFS before mixing](voice-loudness-per-take.md) | proven | any | Per-take loudnorm −16 LUFS / TP −2 before music. |
| [Don't speed up the clone](voice-no-speedup-clone.md) | proven | any | Model speed 1.0 (won A/B); tempo from text. |
| [Phone-recorded reference, clicks removed](voice-record-reference-clean.md) | proven | any | Phone SNR 41 vs 33 dB; adeclick ×2. |
| [Fix deterministic defects by editing text](voice-seed-fix-by-text.md) | proven | any | Fixed seed → byte-identical file: edit the text. |
| [Fix stress by rewording, synthesize in chunks](voice-stress-by-rewording.md) | proven | ru | Replace mis-stressed words; 2–3 sentence chunks, no marks. |
| [Stretch a word with rubberband](voice-stretch-word.md) | proven | any | ×2 with formants, final consonant untouched. |
| [Check tails, rescue uncut takes by energy](voice-tail-rescue-check.md) | proven | any | ASR of last 0.9 s, energy cut; 34 of 246 takes. |
| [Lock the clone reference behind a blind A/B](voice-lock-reference.md) | proven | any | Swapped reference: +2–3 semitones; change only after the person's blind A/B. |
