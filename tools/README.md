# Tools

Standalone Python 3.10+ scripts. Each answers `--help` and works as a library: logic lives in functions,
`main(argv)` only parses arguments. Nothing imports across folders; inside `covers/` and `carousels/` the scripts
share their helpers (`fonts.py`, `infographics.py`, `cards.py`), so copy a folder whole. No hardcoded paths; ffmpeg comes from `PATH`
or the `FFMPEG`/`FFPROBE` variables. The exit code is non-zero when a violation is found, so the tools fit into CI
and `make.sh`.

Install: `pip install -r requirements.txt` at the root. Heavy dependencies (faster-whisper, torch) are installed
separately, see the comments in `requirements.txt`. Tests: `python3 -m pytest` at the root.

| Tool | What it does | In → out | Command | Technique |
|---|---|---|---|---|
| `voice/ru_tts_text.py` | **Russian only.** Prepares Russian text for TTS: `: `→`. `, «AI»→«эй-ай», strips U+0301 stress marks; warns about «!» (keep ~10 % of lines), «ИИ» (rewrite as «нейросеть» in the right case), digits, a short first word, dashes | lines / file → text, rules, warnings (JSON) | `python3 tools/voice/ru_tts_text.py "Отчёт: готов" --json` | only a sentence end gives a TTS pause; dashes and ellipses don't. One for your language is welcome, see [gotchas/lang](../gotchas/lang/README.md) |
| `voice/pick_take.py` | picks the best of several takes: ASR match with the script, word stretch against the median, pauses, clipped ending, speech rate (≤ 6.3 syll/s), optional pitch ceiling, stress heuristic; ties go to the take closest to the median duration, not the shortest; word keys for the stretch check use the same Unicode letter normalization as the script match, so it works in any script. **Tuned on Russian** (`--lang ru`, default). `--lang en` (any Whisper/num2words code) sets ASR and number words and compares letters of any script; stress is Russian-only and speech rate counts Cyrillic + Latin vowels (0 = not measured in other scripts). An empty script or empty ASR scores 0 and fails | WAV takes + text → JSON report, copy of the best | `python3 tools/voice/pick_take.py --text "..." cand/0-*.wav --copy-to voice/raw-0.wav` | generate 3–5 takes and pick by measurement, not by ear |
| `audio/gaps.py` | prints voice pauses longer than a threshold (energy below peak − 40 dB or below −70 dBFS; an all-silent track is one long pause, an empty file exits 2) | WAV → list (start, duration) | `python3 tools/audio/gaps.py voice-track.wav --max-gap 0.8` | pauses between lines ≤ 0.8 s, otherwise the video sags |
| `audio/tail_trim.py` | cuts a "sacrificial" word at the end of a take by energy; leaves tails outside 0.25–1.4 s alone | WAV → `<name>.cut.wav` | `python3 tools/audio/tail_trim.py voice/raw-3.wav` | TTS clips line endings: add a throwaway word and cut it |
| `audio/aac_safe.py` | finds peaks above the ceiling after AAC and locally lowers the master, optionally muxes the video; with `--out-video` it works at 48 kHz (the mux rate, master resampled first) and the verdict comes from measuring the finished mp4 (`final` in `--json`) | WAV (+ mp4) → WAV (+ mp4) | `python3 tools/audio/aac_safe.py --in master.wav --out master-aac.wav --ceiling -3.2` | AAC lifts live-voice peaks up to +2 dB above the master |
| `audio/sfx.py` | 14 procedural SFX (whip, riser, chime, glitch…), deterministic by seed | kind + params → WAV | `python3 tools/audio/sfx.py whip --out whip.wav --length 0.32` | whooshes on cuts without samples or licenses |
| `qa/loudness.py` | integrated LUFS, true peak and LRA (ffmpeg `ebur128=peak=true`) against the table: `final` −15 ±1 LUFS, TP ≤ −1.5 dBTP; `take` −16 ±1 LUFS, TP ≤ −2 | mp4/wav (one or more) → JSON line per file, exit 1 on fail | `python3 tools/qa/loudness.py output/final.mp4` | measure the encoded mp4, not the master; thresholds in `docs/QA-THRESHOLDS.md` |
| `qa/frame_fill.py` | share of the frame covered by content in the finished video (`fill` mode) or 16×8 grid occupancy (`grid`); empty stretches | mp4 → summary, JSON | `python3 tools/qa/frame_fill.py output/final.mp4 --json qa/fill.json` | measure fill by mp4 pixels, not by the DOM |
| `qa/voice_qa.py` | voice gate on the final file: true peak and LRA (ebur128), spread of gaps between lines, syllables/s per line, median pitch per line from a clean voice track | mp4/wav + lines JSON (+ voice wav) → JSON, exit 1 on fail | `python3 tools/qa/voice_qa.py output/final.mp4 --lines voice/timing.json --voice voice/voice.wav` | catches a soft-clip master, metronome gaps, rushed takes and falsetto; thresholds in `docs/QA-THRESHOLDS.md` |
| `qa/seam.py` | seam of a looping clip: last→first frame difference against the median difference of neighbouring frames | mp4 → line or JSON, exit 1 when seam > 2 × median | `python3 tools/qa/seam.py bg/loop.mp4` | a loop for repeat viewing must not jump at the restart |
| `qa/jitter.py` | jitter metric: jerk of the inter-frame difference, cuts excluded | mp4 → JSON line | `python3 tools/qa/jitter.py output/final.mp4 --max-ratio 0.5` | jitter = an unsmoothed animation envelope or duplicated frames |
| `qa/motion_gate.py` | share of fast motion inside shots (`fast_ratio`, `active_ratio`), cuts with camera compensation, dead shots, worst 30-s window; one alarm "dead as a slide deck" (exit 2), `--calib` against your own verdicts | mp4 → Markdown summary, JSON | `python3 tools/qa/motion_gate.py output/final.mp4 --json qa/motion.json` | a hint, not a gate: on 18 videos with human verdicts neither ratio separated approved from rejected |
| `qa/breakdown.py` | per-second map of a reference for a remake: shots (scdet + frame difference), motion per shot, beat grid (librosa, optional), sheet / keys / heat / timeline images, `--compare` reference vs remake | mp4 (+ mp4) → `breakdown/` with md, JSON, jpg, png | `python3 tools/qa/breakdown.py ref.mp4 --compare output/final.mp4 --out qa/breakdown` | copy the rhythm, not the file: the reference stays on your disk |
| `lint/motion_lint.py` | static lint of a GSAP scene: ease, durations, axes, stagger, camera, spring, depth; bans `Math.random` | scene.js + duration → JSON | `python3 tools/lint/motion_lint.py scene.js --duration 30` | catches "flat card with a fade" before rendering |
| `lint/still_lint.py` | dead time over real scene frames (the `window.setTime(t)` contract, as in `starter/`) | project folder → `qa/still-lint.json`, contact sheet | `python3 tools/lint/still_lint.py starter --max-still 3` | a scene shouldn't stand still longer than 3 s; a camera push doesn't fix stillness |
| `image/depth.py` | Depth-Anything-V2-Small depth map, offline | image → `<name>.depth.png` | `python3 tools/image/depth.py art/room.jpg` | depth parallax instead of Ken Burns |
| `image/depth_layers.py` | slices an image into depth layers, cleans masks, fills holes by inpainting | image + map → `<name>.L0..N.png` (RGBA) | `python3 tools/image/depth_layers.py art/room.jpg --cuts 70 150` | 3–4 alpha layers for parallax |
| `captions/to_srt.py` | word timings → SRT and WebVTT, N words per caption (`--words 3`), `--max-duration 3`, new caption on a pause, a line change or a sentence end | starter `voice-track.json`, ASR `[[word, start, end]]`, skit `timeline.json`, Whisper `segments`, or a list of `{text, start, end}` → `.srt` / `.vtt`, exit 1 when no words | `python3 tools/captions/to_srt.py voice-track.json --srt output/final.srt --vtt output/final.vtt` | upload captions as a file instead of burning them, or alongside |
| `publish-prep/credits.py` | attribution block for the video description from a list of assets; fails on a missing or unknown license and on CC BY without an author; a bare `license_url` counts only on the exact host `creativecommons.org` with a license path; NC = warning, error with `--commercial`; ND = warning | assets JSON → text or Markdown (`--format md`), problems in stderr, `--json` report, exit 1 on error | `python3 tools/publish-prep/credits.py assets.json --commercial` | every third-party file has a source and a license; vocabulary in `docs/THIRD-PARTY.md` |
| `project/artifacts.py` | delivery passport: status from `qa/final-result.json` and file sha256 | project folder → `ARTIFACTS.json` | `python3 tools/project/artifacts.py starter` | technical status ≠ approval; a person decides on publishing |

## Carousels, covers, slides

Each folder has its own `requirements.txt` and a README with the input format. Neutral-topic samples live in
`carousels/examples/` and `covers/examples/`.

| Folder | What it does | Commands in |
|---|---|---|
| [`carousels/`](carousels/README.md) | 1080×1350 cards from JSON with text gates before rendering; Markdown longread → A4 PDF; PDF sliced into a carousel; SVG infographics for WeasyPrint | `carousels/README.md` |
| [`covers/`](covers/README.md) | a coded headline over an AI background with a scrim; SVG covers with an icon | `covers/README.md` |
| [`slides/`](slides/README.md) | single-file HTML deck (arrow keys, "N / M", print to PDF) and a Markdown generator | `slides/README.md` |

System WeasyPrint and poppler (`pdftoppm`, `pdfinfo`) are required, plus cairo for `covers/cover.py`. Without them
rendering tests are skipped.

## Models and licenses

- `image/depth.py` works only with **Depth-Anything-V2-Small** (Apache-2.0). Base and Large are CC BY-NC; the script
  warns. No weights in the repo: `huggingface-cli download depth-anything/Depth-Anything-V2-Small-hf` or run with
  `--download`.
- `voice/pick_take.py` uses faster-whisper (MIT); the model (default `large-v3`, `small` is enough for trials)
  downloads on first run.
- Tests that need models are marked `slow` and skipped when the weights aren't available locally.
