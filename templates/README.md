# Templates

Starter skeletons: copy a folder, run it as is to see it work, then replace the content with your own. Each one runs
end to end with placeholders (no TTS, no GPU, no downloads beyond the listed tools) and has a README with what to
replace and the gotchas met while building the original videos.

| Template | What you get | Heavy deps | Smoke test |
|---|---|---|---|
| [`3d-skit/`](3d-skit/README.md) | 3D two-character skit: talking characters, one cut per line, reactions; styles `voxel`, `ps1`, `clean` (three.js), optional Blender EEVEE script | Playwright Chromium, ffmpeg; Blender optional | timeline + one still per style |
| [`skit/`](skit/README.md) | 2D canvas dialogue skit with events on words: phone insert, stamps, SFX, reactions | Playwright Chromium, ffmpeg | timeline + still |
| [`data-reel/`](data-reel/README.md) | reel on numbers you measured: measure → `real-numbers.json` → `reel.json` → starter scene; numbers on screen only from the measurement | the starter (`../starter/`) | measure, generate, number gate; scene compiles with `tsc` |
| [`experiment/`](experiment/README.md) | test a piece of advice: hypothesis, conditions, N clean `claude -p` runs, raw `runs/*.json`, `results.md` table | Claude Code CLI | full series against a fake CLI |
| [`real-tool-reel/`](real-tool-reel/README.md) | pattern for "a real tool works on camera": a safe macOS example tool (dry run by default) and a shoot checklist | macOS for `--live` only | logic + dry run |

`recipe.md` here is the template for new recipes in `../recipes/`, not a project skeleton.

Licenses of everything inside this folder: [THIRD-PARTY.md](THIRD-PARTY.md). Generated files (timelines, audio,
renders, measurements, runs) are ignored by `.gitignore`; rebuild them instead of committing.

Tests: `python3 -m pytest tests/test_templates.py` from the repo root (each test skips when its tool is missing).
