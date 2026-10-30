---
id: section-short-name          # kebab-case, equals the file name
title: Imperative one-liner      # "Make the first word of a TTS line sacrificial"
section: voice                   # folder in recipes/
lang: any                        # any | ru | en | de ... (language-specific recipes, e.g. TTS quirks)
status: proven                   # proven | hypothesis | outdated
evidence: measurement            # measurement | ab-test | video-metric | viewer-feedback | experience
tools: [ffmpeg]
learn: ../../learn/en/03-voice.md   # chapter that explains the why (optional)
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
One or two lines: the symptom or situation that triggers this recipe.

## Do
Numbered steps. Imperative. Exact parameters.

```bash
# minimal reproducible command or code
```

## Verify
Observable check that it worked: a number, a frame, an ASR string. Prefer a command.

## Don't
What the agent must not change or do while applying this.

## Evidence
Where the numbers come from: "34 of 246 takes", "0.56–0.67× font size". No numbers → status: hypothesis.

Have the same issue in another language? Contribute a sibling recipe next to this one (lang: <code>).
<!-- Keep the line above when lang is not `any`: the lint requires this invitation in language-specific recipes. Delete it for lang: any. -->

## Related
- [other recipe](../section/file.md)
