---
id: assembly-word-anchored-animation
title: Anchor animation to aligned word times, not timers
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [WhisperX, GSAP, Python]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Scene events are timed by offset ("2.3 s after line start"). Any voice edit shifts everything; elements land on the wrong word.

## Do
1. Run WhisperX alignment per take → `karaoke.json` with word timestamps.
2. Helper `W(cue, "word")` returns the word's time in the line; schedule animation at it.
3. If the word is missing, the helper warns loudly; never substitute a fallback silently.
4. Show the consequence of each value on screen: the command runs along a rail and passes, hits a barrier, or waits for a human.

```python
import json, sys
K = json.load(open("karaoke.json"))
def W(cue: int, word: str, nth: int = 0) -> float:
    hits = [w["start"] for w in K[cue]["words"] if w["w"].lower().strip(".,!?") == word]
    if len(hits) <= nth:
        print(f"WARNING: word '{word}' not found in line {cue}", file=sys.stderr)
        return K[cue]["start"]
    return hits[nth]
# in the scene: tl.from("#barrier", {...}, W(12, "barrier"))
```

## Verify
After re-synthesising one line, events move with the words; build log has no WARNING lines.

## Don't
Don't anchor a scene's main block to a word at the end of the line: it leaves the scene start empty; bring the block in at the cut.

## Evidence
No effect measurement. A silent fallback in the helper once hid a wrong line number and swallowed a whole scene.

## Related
- [Empty scene start](assembly-no-empty-scene-start.md)
- [Karaoke cache key](../captions/captions-cache-key-text.md)
- Example: [AI text tells](../../examples/ai-text-tells/README.md)
- Example: [Hook that blocks a dangerous command](../../examples/hook-vertical-from-long/README.md)
