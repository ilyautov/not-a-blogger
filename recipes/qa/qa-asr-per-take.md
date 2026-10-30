---
id: qa-asr-per-take
title: Run ASR on every take with a topic vocabulary, never with the line text
section: qa
lang: ru
status: proven
evidence: measurement
tools: [faster-whisper, WhisperX]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
ASR of the final mix hides a lost first word and clipped tails. Per-line ASR raises false alarms: the recognizer's language model substitutes a familiar Russian word for a rare term.

## Do
1. Run ASR on every `voice-N.wav` before assembly and compare with the line.
2. Re-check a suspicious take with large-v3 and `initial_prompt` holding the topic vocabulary.
3. The vocabulary = general topic terms, **never the line text**: a prompt from the line makes the check circular; ASR just agrees with the script.
4. A transcript that changes from prompt to prompt marks a smeared spot: listen to it.
5. Among takes that pass, don't pick the shortest: pick the one closest to the median duration of all takes of that line, and drop takes faster than 6.3 syllables/s or with median pitch above 250 Hz (`pick_take.py --max-f0 250`).
6. Don't trust a similarity threshold alone: the 0.9 ratio in `pick_take.py` and the starter is a floor, not a pass ([QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md)).

```python
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", compute_type="int8")
VOCAB = "система контроля версий гит и Гитхаб, терминал, коммит"   # topic terms, in the video's language
segs, _ = m.transcribe("voice-133.wav", language="ru", initial_prompt=VOCAB)
print(" ".join(s.text for s in segs))
```

## Verify
False alarms disappear with the prompt; real defects remain and are audible.

## Don't
- Don't put the line text into `initial_prompt`.
- Don't rely on ASR for stress/accent errors: it doesn't see them at all; only listening does.

## Evidence
- "гит" (git) was recognised as "гид" (guide) in 12 of 12 takes; with the topic vocabulary all 12 correct.
- The medium model "lost" a whole sentence nobody had lost; large-v3 heard it correctly.
- Two real suspects had similarity 0.975 and 0.988: a 0.90 threshold would miss them.
- Picking the shortest passing take on every line made two videos 15 % faster than the approved references (voice audit of 351 lines).
- On a long video three of 97 takes missing the first word were found only by per-line ASR.

## Related
- [Sacrificial first word](../voice/voice-f5-sacrificial-first-word.md)
- [Tail check](../voice/voice-tail-rescue-check.md)
- [Karaoke cache key](../captions/captions-cache-key-text.md)
- Prompt: [vocabulary hint for faster-whisper and WhisperX](../../prompts/voice/asr-vocabulary-hint.md)
- Example: [Assistant cancels a call](../../examples/mascot-cancels-call/README.md)

Have the same issue in another language? Contribute a sibling recipe next to this one (lang: <code>).
