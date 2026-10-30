# Clone your own voice from seven seconds: OmniVoice snippet

- **Purpose:** the minimal "prompt" for a voice clone is a pair: a short clean recording of your voice and its exact
  transcript. This snippet builds that pair and synthesizes one line.
- **Where tested:** OmniVoice (`k2-fsa/OmniVoice`) on Apple Silicon (`mps`, float16); the same call with `cuda` on
  NVIDIA.
- **Status:** proven on 1 published video: every line in it was the clone, including the one viewers were asked to
  tell apart from the live recording.

## Prompt

```python
import torch, numpy as np, soundfile as sf
from omnivoice import OmniVoice

m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="mps", dtype=torch.float16)  # NVIDIA: "cuda"
prompt = m.create_voice_clone_prompt(
    ref_audio="my-voice.wav",   # ~7 s of your own voice, clean, no music, no room echo
    ref_text="{exact transcript of my-voice.wav, word for word, with the same punctuation}")
wav = m.generate(text="{the line the clone should say}", voice_clone_prompt=prompt)[0]
sf.write("line.wav", np.asarray(wav, dtype=np.float32).squeeze(), 24000)
```

The reference we used was the Russian take from [reference-recording-text.md](reference-recording-text.md); its
`ref_text` was that text verbatim.

## Why

The model aligns the reference sound with `ref_text`. The transcript is the point, not a formality: a transcript
that differs from what was said (a dropped word, a different word order, missing punctuation) shifts the alignment,
and the clone comes out with wrong stresses and misplaced pauses. Seven seconds is enough when the take is clean
and conversational; a longer noisy take is worse than a shorter clean one.

## Pitfalls

- Transcribing the reference by ASR and pasting the result unchecked: ASR drops filler and fixes grammar, and the
  clone inherits the mismatch. Write the transcript by ear.
- A laptop-microphone reference carries clicks the clone reproduces; run a click filter first
  ([recipes/voice/voice-record-reference-clean.md](../../recipes/voice/voice-record-reference-clean.md)).
- Stretched interjections for emphasis break differently per engine; a spelling that worked on F5 came out wrong
  on OmniVoice. Tune by ear ([gotchas/lang/ru.md](../../gotchas/lang/ru.md)).
- Do not carry F5 line rules (sacrificial first word, tail word) over without retesting; the engines fail
  differently ([recipes/voice/voice-blind-tts-bakeoff.md](../../recipes/voice/voice-blind-tts-bakeoff.md)).
- Clone only your own voice or that of a person who gave written consent. Do not put voice references into the
  repository.
- Licence: OmniVoice code is Apache-2.0, but the released weights are CC BY-NC. For ads, client work or any paid
  video use the live recording or an engine with a commercial licence.
