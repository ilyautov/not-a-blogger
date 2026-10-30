---
id: image-chapter-backgrounds-parallel
title: Give each chapter its own photo background and generate them in parallel
section: image
lang: any
status: proven
evidence: measurement
tools: [codex-cli, Python]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
The whole video runs on one flat fill with captions; the frame-fill measurement shows it three-quarters empty.

## Do
1. Give each chapter its own metaphor scene (departures board in a hangar, mousetrap baited with a USB stick, closed blast door) as a full-screen background.
2. Generate all backgrounds in parallel in one pass with a shared art-direction block in the prompt so the series keeps one style.
3. Draw text and numbers on top in code; never ask the model to render letters.
4. A chapter with no illustration of its own gets a blurred copy of the neighbouring chapter's background, not black: in one long video bare chapters on black read as empty and the blurred neighbour fixed it (experience, no measurement).

```python
from concurrent.futures import ThreadPoolExecutor
import subprocess
STYLE = "photo, cinematic, single subject, no text, no letters"
shots = {"ch1": "airport departures board in a hangar",
         "ch2": "mousetrap with a usb stick as bait",
         "ch3": "excavation inside a server room",
         "ch4": "closed blast door"}
def gen(item):
    name, subj = item
    return subprocess.run(["your-image-cli", "--prompt", f"{subj}. {STYLE}", "-o", f"art/{name}.png"]).returncode
with ThreadPoolExecutor(4) as ex:
    print(list(ex.map(gen, shots.items())))
```

## Verify
Frame fill measured on the final mp4 (grid, caption band excluded) is clearly above flat-fill videos.

## Don't
- Don't commit generated PNGs; commit scripts and prompts.
- Don't treat the background as action: word-timed motion on top is still required.

## Evidence
- Four backgrounds in parallel in 80 s.
- Video on photo backgrounds: median grid fill 78 %, p10 73 %; a published long video on flat fill: 24 % and 13 %.

## Related
- [Frame fill by mp4](../qa/qa-frame-fill-mp4.md)
- [Real object, real photo](image-real-object-real-photo.md)
- Example: [The agent said the tests passed](../../examples/agent-cheats-long/README.md)
