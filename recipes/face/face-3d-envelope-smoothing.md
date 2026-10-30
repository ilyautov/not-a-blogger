---
id: face-3d-envelope-smoothing
title: Smooth the speech envelope before animating a 3D character's mouth
section: face
lang: any
status: proven
evidence: measurement
tools: [three.js, numpy]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Low-poly three.js characters open their mouths by speech loudness and jitter ("the models twitch").

## Do
1. Compute the speech loudness envelope per frame window.
2. Smooth it (fast attack, slow release) before driving mouth opening and head sway.
3. Keep the render frame a pure function of time: precompute the envelope and read it by frame index.

```python
import numpy as np, soundfile as sf
x, sr = sf.read("line.wav"); x = x if x.ndim == 1 else x.mean(1)
fps = 30; hop = sr // fps
env = np.array([np.sqrt((x[i:i+hop]**2).mean()) for i in range(0, len(x) - hop, hop)])
env /= env.max() + 1e-9
att, rel = 0.6, 0.15                      # fraction of the way to target per frame
sm = np.zeros_like(env)
for i in range(1, len(env)):
    k = att if env[i] > sm[i-1] else rel
    sm[i] = sm[i-1] + k * (env[i] - sm[i-1])
np.save("mouth.npy", sm)                   # in scene: mouth.scale.y = 0.2 + 0.8 * sm[frame]
```

## Verify
The per-frame mouth-opening plot has no jumps of half the range within one frame.

## Don't
Don't keep iterating on primitive characters: if after 3+ iterations they still "look like the wrong people", build models once via image-to-3D or Blender and reuse them across the series.

## Evidence
- Unsmoothed envelope jumped from 0.495 to 0.216 in one step.
- Low-poly scene render with three.js primitives: ~0.03 s per frame.
- The skit was accepted and published after smoothing.

## Related
- [Skit cut rhythm](../transitions/transitions-skit-cut-rhythm.md)
- [Live voice for the character](../voice/voice-live-for-character.md)
- Example: [I handed my Instagram to the agent](../../examples/instagram-to-claude-skit/README.md)
