---
id: assembly-serialize-heavy-jobs
title: Run synthesis, alignment and render one at a time behind a lock
section: assembly
lang: any
status: hypothesis
evidence: experience
tools: [Python, flock]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
Several agents build videos in parallel, each launching TTS, ASR and a headless browser. The OS kills processes for memory; the render captures black tiles.

## Do
1. Route heavy steps (voice synthesis, alignment, render, frame capture) through a named lock: one voice engine and one browser per machine.
2. Run light steps (script, layout, text checks) in parallel.
3. Synthesise long videos in batches, looping over line numbers, so a crash doesn't restart from zero.

```python
# locked.py — run a command under a named lock
import fcntl, os, subprocess, sys
name, cmd = sys.argv[1], sys.argv[2:]
with open(f"/tmp/{name}.lock", "w") as f:
    fcntl.flock(f, fcntl.LOCK_EX)          # wait for our turn
    sys.exit(subprocess.call(cmd))
# python locked.py voice python synth.py --cue 17
# python locked.py chrome node render.mjs
```

## Verify
With five parallel agents no heavy process is killed; frames have no black tiles.

## Don't
Don't mix synthesis and render in parallel even on a high-memory machine; two slots per step type at most.

## Evidence
No measurements: five agents built five videos in parallel under the lock. Without it, on a long video over 10 minutes processes crashed for memory.

## Related
- [Deterministic timeline](assembly-deterministic-timeline.md)
- Example: [Whole course in 20 minutes (failed)](../../examples/course-retelling/README.md)
