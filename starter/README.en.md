[Русская версия](README.md)

# Reel from code: the reference build

Output: a vertical MP4, 1080×1920, 30 fps, H.264 + AAC. The scene is drawn in TypeScript + Canvas, the sound is
assembled in Python, frames are captured by a local Chromium. There is no publishing and no paid API in this build.

Two examples: a demo about the build itself (three lines) and a separate story about a subscription in
`examples/subscription/`. Start with [FIRST-TASK.md](FIRST-TASK.md): the exact task to give an agent for the
subscription sample, then the full task on your own topic. For a first run by hand, repeat the demo below; the second
example is described in [SECOND-REEL.md](SECOND-REEL.md). Environment, network and disk: [RESOURCES.md](RESOURCES.md);
failures and rollback: [DIAGNOSTICS.md](DIAGNOSTICS.md); what you hand over: [DELIVERY.md](DELIVERY.md).

The files next to this one (FIRST-TASK, SECOND-REEL, DIAGNOSTICS, DELIVERY, AGENTS) are in Russian for now. An agent
reads them fine; translations are welcome as a pull request.

## 1. Install

Tested profile: macOS 26.2, Apple Silicon, Python 3.11, Node 24.21. You need Node 18+ and ffmpeg/ffprobe.
Linux is not tested. Windows is not supported because `locked.py` uses `fcntl`. The 2D scene needs no LTX or NVIDIA
models.

With Homebrew installed, the missing tools are:

```sh
brew install python@3.11 node ffmpeg
```

In a terminal, go to the `starter` folder of this repo (or to your copy of it, see SECOND-REEL.md):

```sh
npm ci
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock-macos-arm64.txt
.venv/bin/python -m playwright install chromium
export PY="$PWD/.venv/bin/python"
./make.sh fonts
./make.sh doctor
```

`doctor` checks imports, system programs, the compiler and that the browser starts. On FAIL, fix the reason it
names; WARN (empty `assets/fonts`, no faster-whisper) doesn't block the fake run. If `make.sh` says there is no
python3.11, set `PY`. Set `PY` again in every new terminal window. The Onest and PT Serif fonts download together
with their OFL licenses. `requirements.txt` pins direct dependencies; `requirements-lock-macos-arm64.txt` is the
full tested environment. On another OS use `requirements.txt` and check compatibility yourself.

On Linux (not tested), skip the lock file and let Playwright install Chromium's system libraries:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
```

## 2. First result without TTS and ASR

```sh
./make.sh fake
./make.sh frames
FINISH_ARGS=--no-asr ./make.sh all
open output/final.mp4
cat qa/final-result.json
```

You get a video with beeps instead of speech. The expected status is `preview_partial`, `technical_pass: false`:
you've checked the build and the staging, not the speech yet. The contact sheet is `qa/sheet.jpg`.

Install time, model downloads and your own work are not part of the render time. On a prepared Mac the demo with a
voice used to build in about two minutes; on another machine it will differ.

## 3. Your own voice, no cloning

Read `voice/chunks.json`. Record each line as a separate WAV/M4A and name them `my-0.m4a`, `my-1.m4a`, `my-2.m4a`.
The words must match the text, and the first and last words must be complete in the recording. Don't name your
sources `raw-N.wav`.

```sh
./make.sh live voice/my-0.m4a voice/my-1.m4a voice/my-2.m4a
./make.sh frames
./make.sh all
open output/final.mp4
```

The importer converts recordings to 24 kHz mono, then `trim.py` trims pauses, recognizes words and builds the
timing. On first use Whisper large-v3 downloads its weights into the Hugging Face cache; that is a separate network
step. `ASR_MODEL=small` is fine for a trial, but check the text match on the model you actually use, and by ear.

**Language.** Speech recognition defaults to Russian. For another language set the Whisper language code once per
terminal window: `export ASR_LANG=en` (applies to both `trim.py` and `finish.py`), or pass a flag:
`voice/trim.py --lang=en`, `FINISH_ARGS="--lang en" ./make.sh all`. Text matching keeps letters and digits of any
script (Cyrillic, Latin, Greek, Devanagari…; ё = е, stress marks ignored); an empty script or an empty recognition
scores 0, never a pass. An end-to-end run with Whisper has been checked in Russian only; other scripts are covered by
normalisation tests alone. Languages written without spaces (Chinese, Japanese, Thai) compare a whole phrase as one
word, so the ratio there is coarse: check by ear. The demo lines in `voice/chunks.json` are Russian, and so are the
sacrificial tail `TAIL` and the number dictionary `NUM` in `trim.py` (and `NUM` in `tools/finish.py`); replace those
for your language too.

## 4. Optional: OmniVoice on Apple Silicon

TTS code and TTS weights come under different terms. Read [THIRD-PARTY.md](THIRD-PARTY.md) and the card of the
specific weights. A voice to clone: 10–20 seconds of a clean recording without music or echo, with a TXT next to it
holding the exact transcript. Don't put a personal reference into a public archive.

```sh
python3.11 -m venv .runtime/tts-omnivoice/venv
.runtime/tts-omnivoice/venv/bin/python -m pip install -r requirements-omni-lock-macos-arm64.txt
export OMNI_PY="$PWD/.runtime/tts-omnivoice/venv/bin/python"
export OMNI_MODEL="$PWD/.runtime/tts-omnivoice/model"
"$OMNI_PY" -c 'from huggingface_hub import snapshot_download; import os; snapshot_download("k2-fsa/OmniVoice", revision="c5fdb5ccb189668d56333f77ba2629f4cd7535f4", local_dir=os.environ["OMNI_MODEL"])'
export OMNI_REF="$PWD/voice/my-ref.wav"
export OMNI_DEVICE=mps
./make.sh doctor --voice
./make.sh voice
./make.sh frames
./make.sh all
```

The install command was checked against https://huggingface.co/k2-fsa/OmniVoice and the versions are pinned.
Synthesis was tested on MPS and CPU on one Mac; CUDA is not tested. `gen_omni.py` loads weights sequentially on Mac:
an asynchronous first load hung on the GIL in the test environment.

`OMNI_SPEED` sets the pace, for example 1.1. Fix a wrong stress by rewording the text or swapping the word, then
listen. Seed 42 reduces randomness but doesn't guarantee byte-identical output on another device.
Re-voice one line: `python3 locked.py voice -- "$OMNI_PY" voice/gen_omni.py 1`, then `trim.py 1`.

## 5. How it fits together

- `voice/chunks.json`: what is spoken, numbers as words; `pause` is the silence after a line.
- `voice/lines.json`: what is shown, digits and Latin script. `Mi_Box{2}` ties one shown word to two spoken ones.
- `voice/trim.py`: ASR, trimming, joining; its output `voice-track.json` holds cues and per-word start/end.
- `voice/raw-N.json`: the passport of a source take (text, engine, settings, sha256), written by `gen_omni.py` and
  `import_live.py`. `trim.py` stops if the take or the line text no longer matches it.
- `scene/scene.ts`: the picture source; `build/scene.js` is generated by tsc.
- `reel.json`: duration limit, music and an optional `sound_events` for a new scene.
- `tools/render.py`: a local HTTP server, `setTime(t)`, frames and `picture.mp4`.
- `tools/sound.py`: voice, ducking, SFX, the stems `speech.wav`/`music.wav`/`sfx.wav` and `master.wav`.
- `tools/finish.py`: the final AAC/MP4, technical QA and SHA256.
- `AGENTS.md`, `CLAUDE.md`, `BRIEF.md`, `.agents/skills/reel-starter/SKILL.md`: the portable task for an agent.
- `.agents/skills/reels-direction/SKILL.md`: a self-contained map of techniques R1–R18 and the limits of checking.
- `.agents/skills/camera-moves/SKILL.md` and `camera-kit.js`: 30 camera moves, formulas and an ES module. It isn't
  wired into the sample scene automatically.
- `analytics.csv`: an empty measurement table to fill in by hand; the build creates no posts and no mailings.

Voice → `voice-track.json` → `story.json` → scene/events → sound/render → `final.mp4` → a person checks it.
Event times come from words. If a word went missing, fix the event, don't plug in an arbitrary second.
For numbers, extend `NUM` in `trim.py` and `finish.py`. Unmatched ASR words are interpolated; that doesn't prove
every word was spoken. Check each line's ratio and the final ASR, then listen.

Randomness in the scene comes from a fixed PRNG; `setTime(t)` depends on time only. Captions are a separate layer;
the camera moves the main object. Styles and shots of the sample scene are yours to change.

Music: with `music.file=null` a built-in pad is synthesized. For an external track set the path, offset, gain and
credit, and check that track's terms. Stems are written before final mastering and differ in loudness from the MP4.

## 6. Commands and edits

```sh
./make.sh doctor
./make.sh scene
./make.sh frames
./make.sh sound
./make.sh render
./make.sh finish
```

Text/voice: `live` or `voice` → `frames` → `all`. Scene/events: `frames` → `all`. Music only: `sound` → `finish`.
On-screen text only: `voice/trim.py track` → `frames` → `all`, checking that words still match.
A render slice for a trial: `python3 locked.py render -- "$PY" tools/render.py --from 0 --to 4`. It overwrites
`picture.mp4`, so run a full `render` before `finish`.

`all` rebuilds scene, sound, picture and final. It doesn't synthesize voice. It is a plain sequential chain, not an
incremental runner. Voice and render go through a shared queue `/tmp/not-a-blogger-*.lock`
(`python3 locked.py <name> -- <command>`; without `--` it prints a hint and exits). Don't change `LOCK_DIR` between
parallel builds or you get separate queues.

Before a substantial edit, stop the build and save the working state:

```sh
./make.sh checkpoint save before-edit
./make.sh checkpoint list
./make.sh checkpoint restore before-edit
```

A checkpoint is private: `.checkpoints/` includes local `voice/*.wav/m4a/txt` and the MP4/QA. Models, environments
and profiles are excluded; the public sources are listed in `SOURCE-MANIFEST.json`. Restore first checks schema,
paths and SHA256 and saves a safety copy. Included files added after the snapshot will be removed. If a restore is
interrupted, use the safety copy name from its output. `all` has no overall transaction. Details, limits and
failures: DIAGNOSTICS.md.

## 7. QA and limits

- `ready_for_user_preview` + `technical_pass=true`: all mandatory checks passed, with real speech and final ASR.
- `preview_partial` + `technical_pass=false`: beeps or ASR skipped; a normal finish for a technical trial.
- `technical_failed` + non-zero exit code: a mandatory threshold failed. Fix the reason named in `checks`.
- `artistic_approval` and `publication_approved` are always `false`: automation never sets them.

Checks: decodes, faststart, 1080×1920/30 fps, duration within `max_duration`, size ≤100 MB, −15±1 LUFS,
TP ≤−1.5 dBTP on the final AAC, static ≤3 s, ASR match ≥0.9 for the final video and for every take
(`takes_asr_ge_0_9` from `voice/asr-N.json`; a floor, not a pass). A take result made stale by editing the line text
or `line-N.wav` doesn't count: the status stays `preview_partial` until you re-trim with `voice/trim.py N`.
Where each threshold came from and which were measured: [QA-THRESHOLDS.md](../docs/QA-THRESHOLDS.md).
The static check is the mean difference of 135×240 grey frames with the camera on: camera motion can hide a dull scene.
For a separate check, run from the repository root:

```bash
python3 tools/lint/still_lint.py starter --step 0.5 --max-still 3
```

Both bundled Canvas scenes expose the optional `window.setQAMode(enabled: boolean)` contract.
With `true`, it removes camera movement, whip transitions and grain while retaining object animation and captions;
normal rendering and `false` retain the authored look. The linter enables it before sampling.
Without the hook, it resets the CSS transform of a `#world` DOM camera. For a custom camera use
`--pre-js "window.cam.reset()"` (JS after every `setTime`); `--keep-camera` retains the camera.
Check `camera_control` in `qa/still-lint.json`: `setQAMode`, `dom-world`, `kept` or `unsupported`.
The last means camera removal is unverified; review the effect of a custom `--pre-js` separately.
Step must be finite and > 0; threshold and maximum stillness must be finite and >= 0.

ASR doesn't check stress, intonation or artistic value. Watch and listen to the
whole finished file. An assistant can check frames and audio tracks separately; that is not the same as watching
and listening straight through.

Starter code is MIT. Models, personal recordings and third-party music are not covered. Links in THIRD-PARTY.md.

## 8. If you get stuck

Save the command, the exit code and the last lines of the error, then go through the table in
[DIAGNOSTICS.md](DIAGNOSTICS.md). The most common stops on a first run:

**`make.sh` says there's no python3.11, or npm can't see package.json.** The terminal isn't in the `starter` folder:
`ls` should show `make.sh` and `package.json`; `cd` there. If the venv exists, `export PY="$PWD/.venv/bin/python"`;
set it again in every new terminal window.

**`doctor` says FAIL.** TypeScript: run `npm ci` or set `TSC=/path/to/tsc`. Chromium:
`.venv/bin/python -m playwright install chromium` (on Linux `install --with-deps chromium`). node, ffmpeg, ffprobe: install them (`brew install node ffmpeg`)
and reopen the terminal. The first Playwright and Whisper install needs internet; a network or certificate error is
not fixed by turning security off.

**Frames are in `qa/frames`, but `all` stopped or there's no MP4.** Contact sheets and previews are not an export;
the result is only `output/final.mp4`. Read `qa/final-result.json`: on `technical_failed`, `checks` names the exact
threshold to fix. For beeps without ASR run `FINISH_ARGS=--no-asr ./make.sh all`; `preview_partial` is expected
then. Save state before editing the scene: `./make.sh checkpoint save before-edit`.

**Your machine is too small for a model.** The 2D demo needs no GPU: `fake` → `frames` → `all` builds a video on
any Mac with Python 3.11 and Node 18+. OmniVoice (section 4) is optional; your own recording (section 3) replaces
it. Whisper large-v3 is heavy: try `ASR_MODEL=small`, but check the text match on your chosen model and by ear.
Add one step of complexity at a time instead of installing every model at once.

**Voice and recognition act strangely.** A wrong stress in OmniVoice is fixed in the text or by swapping the word,
not with parameters. When ASR disagrees with the text, listen to `raw-N.wav` first: recognition makes mistakes of
its own. Pitfalls of specific models are in [../gotchas/](../gotchas/) and in [../recipes/voice/](../recipes/voice/).
