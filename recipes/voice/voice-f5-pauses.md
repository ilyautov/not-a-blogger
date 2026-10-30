---
id: voice-f5-pauses
title: Make F5 pauses with a full stop or a hard marker, not a dash
section: voice
lang: any
status: proven
evidence: measurement
tools: [F5-TTS, ffmpeg]
learn: ../../learn/en/03-voice.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The script uses dashes, ellipses, or colons for pauses, and F5-TTS reads the line without air. Worst with "meme" references, which hold no pauses.

## Do
1. Make in-line pauses with sentence ends: `.`, `?`, `!`.
2. Before synthesis replace `: ` with `. `.
3. Don't use dashes, ellipses, or commas for pauses.
4. For a guaranteed pause (or a voice with no pauses) split the line with ` | `: synthesize segments separately, insert 0.4 s of silence between them.
5. Make the first word of each segment sacrificial too (lead-token trimming fires again per segment).

```python
import re
def prep(text: str) -> list[str]:
    text = re.sub(r":\s", ". ", text)          # colon → full stop
    return [s.strip() for s in text.split(" | ") if s.strip()]

# segments → wav, then concat with 0.4 s silence
# ffmpeg -f lavfi -t 0.4 -i anullsrc=r=24000:cl=mono sil.wav
# printf "file seg1.wav\nfile sil.wav\nfile seg2.wav\n" > list.txt
# ffmpeg -f concat -safe 0 -i list.txt -c copy line.wav
```

## Verify
Measure silence between words by signal energy, not WhisperX alignment: the aligner stretches word boundaries over silence.

## Don't
- Don't reuse these numbers for other engines; measure again.
- F5-TTS_RUSSIAN weights are CC BY-NC 4.0.

## Evidence
10 variants of one line, calm reference:
- `.`, `?`, `!` ≈ 0.43 s;
- quotes «» ≈ 0.39 s;
- colon 0.30 s;
- comma, semicolon, dash, ellipsis ≈ 0.08 s, same as no mark.
Meme reference: 0.08–0.14 s on any mark, including the full stop.
After ` | `, lead-token trimming leaves a stray "k" with some references and eats the first consonant with others.

## Related
- [Sacrificial first word](voice-f5-sacrificial-first-word.md)
- [Gaps between lines](voice-gaps-between-lines.md)
