---
id: captions-cache-key-text
title: Key the karaoke cache by take hash plus line text
section: captions
lang: any
status: proven
evidence: measurement
tools: [WhisperX, Python]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
A line was rewritten and re-synthesised, but captions show the old wording: the alignment cache checked only the file hash. ASR QA of the final video doesn't look at karaoke.

## Do
1. Cache key = take hash + line text.
2. After any text or take-length change rebuild in order: timeline from new lengths → karaoke → timeline → build. Karaoke reads times from the timeline; skipping step one lays words on old timestamps.
3. Before render, compare karaoke words with the lines file.

```python
import hashlib, json
def cache_key(wav_path, text):
    h = hashlib.sha256(open(wav_path, "rb").read()).hexdigest()
    return hashlib.sha256((h + "\n" + text.strip()).encode()).hexdigest()

kar = json.load(open("karaoke.json")); lines = json.load(open("voice-lines.json"))
for i, line in enumerate(lines):
    words = " ".join(w["w"] for w in kar[i]["words"]).lower()
    assert words.split() == line.lower().replace(",", "").replace(".", "").split(), f"line {i}"
```

## Verify
The comparison script is silent; on the contact sheet caption words match the voice.

## Don't
Don't compare raw strings: numbers and Latin words are written differently by ASR; normalise both sides the same way.

## Evidence
Eight rewritten lines of a long video shipped with old-wording captions; the video was already published.
Counted on one published long video: 8 lines with stale captions after a text edit; with the text in the cache key the same edit invalidates all 8.

## Related
- [Per-line ASR of takes](../qa/qa-asr-per-take.md)
- [Sacrificial tail word](../voice/voice-f5-tail-sacrificial-word.md)
