# 3d-skit: two-character 3D sketch in three styles

A vertical (1080×1920, 30 fps) dialogue sketch: two characters, one cut per line, mouths driven by the voice,
reactions on a timeline, subtitles in the upper third. One shared skeleton, three interchangeable looks:

| Style | File | Look | Render speed (laptop GPU) |
|---|---|---|---|
| `voxel` | `styles/voxel.js` | blocky characters with pixel-art faces, glowing keyboard floor, blurred terminal wall, DOF | ~0.03–0.06 s/frame |
| `ps1` | `styles/ps1.js` | 360×640 retro console: vertex wobble, affine textures, Bayer dither, 15-bit color, 12 fps animation | ~0.05 s/frame |
| `clean` | `styles/clean.js` | smooth toy look, physical materials, RoomEnvironment light, soft shadows | ~0.03–0.06 s/frame |
| EEVEE (optional) | `blender/render_eevee.py` | Blender render of the same timeline: soft shadows, reflections, motion blur | ~50× slower than three.js |

The characters are placeholders on purpose: **Dude** (a generic guy in a hoodie) and **Bot** (a neutral robot).
Neither is anyone's mascot. Replace them with your own.

## When to use it

- A short skit where the joke lives in the dialogue and the edit, not in realistic faces.
- You want every frame reproducible: change a line, re-render, the rest stays identical.
- You want to try several looks on the same script before committing to one.

Not a fit: realistic humans (see `../../recipes/face/`), long scenes with complex hand acting (there is no hand rig).

## Run

Needs Python 3.10+ with `numpy`, `soundfile`, `playwright` (`python -m playwright install chromium`) and `ffmpeg`.

```bash
cd templates/3d-skit
python3 build_timeline.py                           # script.json -> timeline.json + audio/mix.wav (placeholder babble)
python3 render.py --style clean --stills 1,4,8      # quick look: stills/clean-01.00.jpg ...
python3 render.py --style voxel --gpu               # full video: output/voxel.mp4 (muxed with audio/mix.wav)
python3 render.py --style ps1                       # without --gpu: SwiftShader on CPU, slow but works anywhere
```

Live preview in a browser: `python3 -m http.server` in this folder, then open
`http://localhost:8000/index.html?style=voxel&t=3.5` (`t` = time in seconds).

Optional EEVEE pass (Blender 4.5 LTS or newer):

```bash
blender --background --factory-startup --python blender/render_eevee.py -- --stills 1,5 --scale 50
blender --background --factory-startup --python blender/render_eevee.py -- --frames
```

## How it fits together

```
script.json ──build_timeline.py──> timeline.json ─┐
  (who, text, shot preset,            (lines + mouth envelope per frame,
   reactions, optional voice file)     shots, reactions)
                                   audio/mix.wav  │
                                                  ▼
index.html?style=… ──> common/core.js (timeline, rig animation, camera presets, subtitles)
                   └─> styles/<style>.js (world + Dude + Bot) ──render.py──> output/<style>.mp4
```

- `script.json`: one entry per line. `shot` is a framing preset: `dude`, `dude_tight`, `bot`, `bot_tight`, `wide`.
  `react` adds reactions in seconds relative to the line start: `shock`, `slump`, `facepalm`, `happy`, `smug`, `sweat`, `point`, `shrug`.
- `voice`: path to a real take (WAV). Without it a line gets a placeholder babble, so cuts, mouths and framing can be
  checked before any TTS. Timing always follows the audio: a longer take moves every later cut.
- `common/core.js`: `animateRig()` turns reactions into poses (one shared vocabulary for all styles), `frameShot()` puts
  the face at ~45 % from the top so the upper third stays free for subtitles.
- A style module only builds a world and two rigs (`{root, torso, neck, arms: [{sh, el}], face(state)}`) and calls `run()`.

## What to replace

1. Lines in `script.json` (and your takes in `voice:`). Show the script to a human before building: 3–5 lines and one storyboard.
2. Characters: `makeDude()` / `makeBot()` in the style you keep. Keep the rig fields, the shared animation will work.
3. Palette: the `P` object at the top of each style. Do not reuse another creator's brand colors or mascot.
4. The set: the keyboard floor, the night office or the room corner are generic stand-ins for your story's place.
5. A font: `index.html` uses system sans; add your own `@font-face` (OFL fonts are fine, keep the license file next to it).

## Gotchas (from the projects this template was cut from)

- **Jitter comes from frequencies, not amplitude.** Idle motion uses two smooth sines under ~0.4 Hz. Adding 5–8 Hz
  harmonics made characters look like they shiver. The mouth envelope is speed-limited for the same reason.
- **Raw RMS on the jaw chatters.** Always attack/release + speed limit (`envelope()` in `build_timeline.py`).
- **Keep `setTime(t)` pure.** No state between frames, no `Math.random()`. Otherwise stills and the full render disagree.
- **Leave air above the head.** A subtitle lying on the hair still reads, but looks cramped. Framing presets keep ~5 % headroom.
- **Voxel hands in a close-up look like cubes stuck to the shoulders.** Show "crossed arms" with the face (squint) instead.
- **PS1 look needs the low frame rate:** characters at 12 fps and the camera at 15 fps; at 30 fps it reads as a cheap filter.
- **Physical sheen is brighter in WebGL than in EEVEE.** If you port materials from Blender, cut sheen to about a third.
- **Blender API drifts between versions:** compositor nodes and EEVEE settings were renamed in alpha builds; use an LTS
  release. The glTF exporter writes one animation clip per object, play all of them if you export to three.js.
- **Lip shapes (visemes):** Rhubarb Lip Sync (MIT) in phonetic mode is an option; on Russian it produced 6 of 9 mouth
  shapes and has no native arm64 macOS binary (runs under Rosetta). The envelope approach here needs no extra tool.
- **Hyperreal variant (generative video, e.g. LTX):** not included. In tests: 576×1024 output upscaled ×1.9 looks soapy,
  faces drift between shots, every re-generation is a new actor and pose, ~4 minutes per 2 s of video, and the model
  license has its own terms. Keep it for inserts; see `../../recipes/face/face-ltx-a2v-local.md`.
- **Check hand poses on a stills sheet.** A "pointing" hand read as the middle finger: index finger diagonal to the
  side, thumb out, hand in three-quarter view, and the finger appears only once the arm has settled. One case.
- **A held object hides behind the head.** A card in a voxel character's hand disappeared behind the head from the
  camera's side: hold it higher and counter-rotate it towards the camera. One case.
- **The mascot must read as its species.** A primitive-built gorilla was read as a bear until it got a crest, brow
  ridge, flat nose and trapezius hump; see `../../recipes/brand/brand-3d-mascot-alpha-clips.md`.
- **Shots shorter than 0.4 s** fail the assert in `build_timeline.py`: merge the line or lengthen it.

## Related recipes

- `../../recipes/face/face-3d-envelope-smoothing.md`: mouth envelope without jitter
- `../../recipes/camera/camera-handheld-sines.md`: handheld camera from sines
- `../../recipes/assembly/assembly-deterministic-timeline.md`: one timeline drives picture and sound
- `../../recipes/sound/sound-keep-noise-whooshes.md`: whoosh on every cut
- `../../recipes/qa/qa-asr-per-take.md`, `../../recipes/qa/qa-contact-sheet-final.md`: check takes and the final frames
- `../../recipes/idea/idea-remake-rhythm-not-words.md`: remake a hit's rhythm, never its words
- `../../recipes/face/face-no-real-person.md`: no real person's likeness in generated characters

Licenses of vendored files: `../THIRD-PARTY.md`.
