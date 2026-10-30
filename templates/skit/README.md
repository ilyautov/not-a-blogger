# skit: dialogue sketch with word-anchored events

A vertical (1080×1920, 30 fps) two-character dialogue: a cut on every line, mouths from the voice, and **events tied to
words**: a cut to a phone insert on "phone", a chat message, a stamp "WHAT?!", a reaction, a sound. Change a take and
everything that hangs on its words moves with it. The scene is flat 2D canvas (no WebGL), so it renders anywhere.

Same skeleton as the 3D sketches (timeline.json + `setTime(t)` + frame-by-frame render); for a 3D look take
`../3d-skit/` and port the `events` block from this `lines.json`.

## When to use it

- A short skit where props react to what is said: a phone screen, a counter, a stamp, a sound on the punch word.
- You will swap the voice later (synthesized now, your own recording later) and do not want to re-time anything by hand.
- You need a draft today on any machine: no GPU, no TTS, no fonts required for the first run.

## Run

Needs Python 3.10+ with `numpy`, `soundfile`, `playwright` (`python -m playwright install chromium`) and `ffmpeg`.

```bash
cd templates/skit
python3 build_audio.py                  # lines.json -> timeline.json + audio/mix.wav (placeholder babble, synthesized SFX)
python3 render.py --stills 1,4,6        # stills/skit-01.00.jpg ...
bash rebuild.sh                         # all of it: timeline, audio, render, qa/sheet.jpg, loudness
```

Live preview: `python3 -m http.server` here, open `http://localhost:8000/index.html?t=4`.

With real takes: put WAV files next to the template, add `"voice": "voice/l1.wav"` to each line and run
`bash rebuild.sh --asr` (word timestamps from faster-whisper, `pip install faster-whisper`; they are shifted by the
leading silence `load_take()` trims, so events land on the word in the mix). Without `--asr`
words are spread over the take by length: fine for blocking, not for a final cut on a precise word.

## How it fits together

| File | Role |
|---|---|
| `lines.json` | the script: who, text, shot (`two`, `dude`, `bot`, `phone`), optional `voice`, `gap` before the line, `events` |
| `build_audio.py` | lays out lines, finds event words, writes `timeline.json` (shots, lines with words and mouth envelope, marks, phone messages, stamps, reactions) and `audio/mix.wav` (speech, whoosh on every cut, SFX on events, optional ducked music, two-pass loudnorm to −15 LUFS) |
| `scene.js` | draws a frame for time `t`: room, Dude, Bot, phone insert, stamps, word-by-word subtitles, handheld camera from sines |
| `render.py` | headless Chromium, one screenshot per frame into ffmpeg, mux with the mix |
| `rebuild.sh` | the whole chain plus a contact sheet and a loudness readout |

An event: `{"name": "shock", "word": "what", "stamp": "WHAT?!", "sfx": "thud", "react": "shock", "cut": "phone", "msg": {...}}`.
Every field except `name` and `word` is optional. SFX kinds: `whoosh`, `pop`, `ding`, `thud`, `tick`, `cricket`.

## What to replace

1. Text and events in `lines.json`. Write the script first and show it to a human: a copy of a format that worked once
   is not a script.
2. Characters in `scene.js` (`dude()`, `bot()`): any shapes, keep reading `env()` for the mouth and `react()` for poses.
3. The phone insert (`phone()`): it is your story's screen. Draw interfaces from scratch, no real brand UI or logos.
4. Palette `C` and the font (system sans by default).
5. Music: `lines.json -> music.file` with an open-license track; put the credit line in the video description.

## Gotchas

- **A cut shorter than 0.5 s** stops the build (`shots shorter than 0.5 s`): two events too close, or a cut right at a line start.
- **The first word of a TTS take is fragile** (some engines glue or swallow it). Check every take with ASR before layout,
  and keep a sacrificial first word if your engine eats it. See `../../recipes/voice/`.
- **The tail of a take gets clipped** by some TTS engines; `load_take()` keeps 0.12 s after the last loud frame on purpose.
- **Loudness after AAC goes up 1–2 dB on plosives.** If true peak lands near 0 dBFS in the mp4, run
  `../../tools/audio/aac_safe.py` before the final mux.
- **Whoosh on every cut is a feature:** a quiet smoothed-noise "sniff" 0.12 s before each cut. Viewers notice it and comment.
- **Subtitles are drawn word by word in the top zone;** keep props below ~y=600 so they do not collide (the phone does).
- **Green QA is not approval.** Look at `qa/sheet.jpg` and listen to every line ending before calling it done.

## Related recipes

- `../../recipes/assembly/assembly-word-anchored-animation.md`: anchor animation to words
- `../../recipes/assembly/assembly-deterministic-timeline.md`: one timeline for picture and sound
- `../../recipes/sound/sound-sfx-by-meaning.md`, `../../recipes/sound/sound-keep-noise-whooshes.md`
- `../../recipes/face/face-3d-envelope-smoothing.md`: mouth envelope without chatter
- `../../recipes/captions/captions-grow-upward.md`, `../../recipes/qa/qa-contact-sheet-final.md`
- `../../recipes/idea/idea-script-before-build.md`
