# Vocabulary hint for ASR that checks the voice-over

- **Purpose:** an `initial_prompt` for Whisper-family ASR when it verifies synthesized takes. ASR substitutes a
  familiar word for a rare term and raises a false alarm; a list of the video's terms stops that. The list is built
  from the topic, never from the line being checked.
- **Where tested:** faster-whisper large-v3 (`int8`, `ru`), and WhisperX, which is built on it and passes the same
  field through `asr_options`.
- **Status:** proven on 2 videos: a term misheard in 12 of 12 takes came out right in all 12 with the hint; on a
  40-line sketch 38 lines were recognised verbatim.

## Prompt

The hint is one string in the video's language: a label plus the terms, brand names in the script's spelling.

```text
Vocabulary: {product or tool names as they appear in the script}, {domain terms}, {abbreviations the voice
pronounces}, {words ASR has already misheard in this video}.
```

faster-whisper:

```python
from faster_whisper import WhisperModel

HINT = ("Vocabulary: backend, API, Redis, Docker, Kafka, RabbitMQ, Kubernetes, Postgres, MongoDB, "
        "FastAPI, Prometheus, Grafana, cache, websockets, load balancer, microservices, tracing, metrics.")
m = WhisperModel("large-v3", compute_type="int8")
segs, _ = m.transcribe("line.wav", language="{language code}", initial_prompt=HINT, word_timestamps=True)
print(" ".join(s.text for s in segs))
```

WhisperX (same field, passed at model load):

```python
import whisperx

model = whisperx.load_model("large-v3", "cpu", compute_type="int8", language="{language code}",
                            asr_options={"initial_prompt": HINT})
result = model.transcribe(whisperx.load_audio("line.wav"))
```

## Why

Whisper decodes with its own language model on top of the acoustics, so a rare term loses to a common word that
sounds alike even when the audio is clean. `initial_prompt` biases the decoder toward the listed spellings. The
list must not contain the line itself: a prompt made from the script makes ASR agree with the script, and the check
verifies nothing. Terms from the whole video are safe because they do not tell the decoder which words this take
contains or in what order.

## Pitfalls

- Pasting the line text as the hint: the transcript matches the script perfectly and a swallowed word passes.
- Russian example of the false alarm: «гит» (git) heard as «гид» (guide) in every take while the audio was right;
  with the vocabulary all takes were correct ([gotchas/lang/ru.md](../../gotchas/lang/ru.md)).
- The hint does not fix everything: in the same sketch one brand name followed by a verb was still heard as two
  unrelated words. A transcript that changes between hint variants marks a smeared spot; listen to it.
- ASR does not hear stress errors at all; only listening does.
- Per-take procedure, thresholds and what to do with a real miss:
  [recipes/qa/qa-asr-per-take.md](../../recipes/qa/qa-asr-per-take.md).
