# Third-party material in templates/

Checked on 2026-10-23. Rule: only permissive licenses (MIT, Apache-2.0, CC0, OFL) are copied into this folder, with
the license file next to them. Everything else is a link: you download it yourself and accept its license.

All template code written for this repository (scripts, scenes, styles, the Blender script) is MIT, like the repo.
No images, audio, video, fonts, model weights or voice samples are stored here; textures are drawn by code at runtime
and placeholder sounds are synthesized by the scripts.

## Vendored (copied, unmodified)

| What | Version | License | Where | Source |
|---|---|---|---|---|
| three.js core build | 0.169.0 | MIT, `vendor/three/LICENSE` (© 2010-2024 three.js authors) | `3d-skit/vendor/three/build/three.module.min.js` | npm `three@0.169.0` |
| three.js addons: EffectComposer, RenderPass, BokehPass, OutputPass, ShaderPass, MaskPass, Pass, CopyShader, BokehShader, OutputShader, RoomEnvironment | 0.169.0 | MIT (same file) | `3d-skit/vendor/three/examples/jsm/...` | npm `three@0.169.0` |

## Used but not included (links only)

| What | License | Why not here | Get it |
|---|---|---|---|
| Rhubarb Lip Sync (phoneme mouth shapes) | MIT | a platform binary, no arm64 build; the templates use an RMS envelope instead | https://github.com/DanielSWolf/rhubarb-lip-sync |
| Poly Haven HDRIs and textures | CC0 | large binaries; `clean` style uses three.js `RoomEnvironment` instead | https://polyhaven.com |
| Fonts (e.g. Onest, Inter) | OFL | binaries; templates fall back to the system sans | https://fonts.google.com |
| Music tracks by CC BY artists (e.g. Kevin MacLeod, Lee Rosevere) | CC BY | attribution-only licenses and audio files are kept out; `skit` takes `music.file` from you and needs a credit line | https://incompetech.com, https://freemusicarchive.org |
| LTX-Video / LTX-2 weights (hyperreal style mentioned in `3d-skit/README.md`) | LTX community license, not OSI | weights and a non-permissive license | https://github.com/Lightricks/LTX-Video |
| TTS weights (OmniVoice, F5-TTS and others) and any voice reference | varies, often non-commercial | weights and voices are never stored; bring your own | see `../recipes/voice/` |
| Characters, mascots, logos or palettes of the original author | personal / brand | not reusable; templates ship neutral "Dude" and "Bot" | — |

## External programs the templates call (not included, not linked into our code)

| Program | License | Used by | Note |
|---|---|---|---|
| Blender | GPL-2.0-or-later | `3d-skit/blender/render_eevee.py` (optional) | our script only calls the `bpy` API from inside Blender; rendered frames are yours |
| Chromium via Playwright | BSD-3 / Apache-2.0 | `render.py` in `3d-skit`, `skit` | `pip install playwright && python -m playwright install chromium` |
| FFmpeg | LGPL/GPL depending on build | render and audio steps | called as a separate process |
| faster-whisper | MIT | `skit/build_audio.py --asr` (optional) | model downloaded on first use |
| num2words | LGPL-2.1 | `data-reel/reel_from_numbers.py` (optional import) | without it digits are used |
| Claude Code CLI | Anthropic terms | `experiment/run.py` | your own login |
| macOS `osascript`, `lsappinfo`, `say` | part of macOS | `real-tool-reel/tool/focus_nag.py --live` | macOS only |
