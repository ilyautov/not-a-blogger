# data-reel: a reel built on numbers you measured

A 20–30 s vertical reel where every number on screen and in the voice comes from one measurement file,
`real-numbers.json`. The pattern: **measure → real-numbers.json → reel_from_numbers.py → reel.json + lines → scene**.
The example measurement is harmless and generic: how much space a folder takes and what eats it.

## The rule

**Numbers on screen come only from `real-numbers.json`.** Nobody types a number into the script, the scene or the
subtitles. A number appears in the reel only through `reel_from_numbers.py`; `check_numbers.py` fails the build if
a number in `voice/lines.json`, `voice/chunks.json` or `reel.json` cannot be traced back to the measurement. Re-measure, rerun, and the
voice, subtitles, bars and counters follow.

## When to use it

- "I checked it myself" reels: disk usage, how long a build takes, how many tokens a prompt costs, how many tabs are open.
- Any claim with a number where being wrong by one digit costs you the comments section.
- Not for opinions or for numbers from somebody else's article: there is no measurement to lock to.

## Run

Needs Python 3.10+. The reel itself is rendered by the starter (`../../starter/`), so set that up first
(its README: Node `tsc`, Playwright Chromium, ffmpeg). `num2words` (`pip install num2words`) is optional and spells
numbers for the voice; without it digits go to TTS and you fix `voice/chunks.json` by hand.

```bash
cd templates/data-reel
python3 measure_folders.py ~/Downloads --hide-names     # read-only -> ./real-numbers.json in the current folder (aggregates only)
python3 reel_from_numbers.py                            # -> reel.json, voice/lines.json, voice/chunks.json here
python3 check_numbers.py                                # every number traces to real-numbers.json, or exit 1
```

Into a starter copy (work on a copy, never on the starter itself):

```bash
cp -R ../../starter ~/reels/my-data-reel
python3 reel_from_numbers.py --into ~/reels/my-data-reel
cp real-numbers.json ~/reels/my-data-reel/ && python3 check_numbers.py --dir ~/reels/my-data-reel
cp scene.ts ~/reels/my-data-reel/scene/scene.ts
cd ~/reels/my-data-reel
./make.sh fake            # placeholder voice, no TTS needed; or ./make.sh voice / ./make.sh live
./make.sh frames          # dry contact sheets in qa/frames/ before the full render
FINISH_ARGS=--no-asr ./make.sh all
```

Other measurements: `measure_folders.py PATH --du` counts allocated disk space (`st_blocks`, what `du` shows) instead
of file sizes, for every number in the file at once (`size_metric` says which). `--top N` keeps N biggest subfolders
by name; the rest are summed into `other_folders`. Folders the walk could not read are counted (`unreadable_dirs`,
`unreadable_entries`) and the file gets `"complete": false`; `reel_from_numbers.py` then stops unless you pass
`--allow-incomplete`, which writes "incomplete" into the source line, and `check_numbers.py` checks that it did.

## How it fits together

| File | Role |
|---|---|
| `measure_folders.py` | read-only walk (no symlinks followed), writes aggregates: total, per top-level folder, per file kind, older than a year. No file names, no full paths, no contents. `target_label` is the folder's own name or `~` |
| `real-numbers.json` | the measurement, with `measured_at` and `tool`. Not shipped: you generate yours. Written to the folder you run from (`--out` to choose); it carries your subfolder names, so keep it out of the repo (`.gitignore` covers `templates/data-reel/real-numbers.json` and `templates/**/output/`) |
| `lines.template.json` | the script with `{placeholders}`, five lines = five shots |
| `reel_from_numbers.py` | fills placeholders: show form (`9,4`) to `voice/lines.json`, spoken form to `voice/chunks.json` with the starter's `token{N}` markup; writes `reel.json` (`n` values, formatted strings, bars, sound events) |
| `check_numbers.py` | the gate, recomputed from `real-numbers.json`: subtitle numbers; the spoken form of each subtitle number in the matching chunk of `voice/chunks.json` and no other digits or number words there (words for "one" are skipped, they double as "a"; without `num2words` only digits are checked); the raw values in `reel.json` `n` that drive the scene (`total_gb`, `old_pct`, ...), the `n.fmt` labels and every bar's `name`, `gb`, `fmt`. Rephrasing a chunk around its numbers passes |
| `scene.ts` | starter scene: odometer for the total, bars for the top folders, two tiles by kind, a 100-cell grid for "old", a source card. Events `total`, `top`, `kinds`, `old` sit on the spoken number word |

## What to replace

1. **The measurement.** Write your own `measure_*.py` that prints one JSON with `measured_at`, `tool` and only
   aggregates. Keep it read-only. Then change `values()` in `reel_from_numbers.py` to map its fields to placeholders.
2. **The script** in `lines.template.json`. Keep numbers as `{keys}`. Show it to a human before building.
3. **The scene** (`scene.ts`): shot functions `total`, `bars`, `kinds`, `old`, `source`, the palette constants at the
   top, the font. If you change the number of lines, change the `shots` array (one cut per line).
4. **Sound events** in `reel.json` (generated): kinds `click`, `pop`, `thud`, `chord` from the starter's `tools/sound.py`.

## Gotchas

- **Measure read-only, and say so on screen.** A folder-size script that deletes or moves anything is a different
  video and a real risk. `measure_folders.py` only calls `os.walk`, `scandir` and `lstat`.
- **Names on screen are data.** Subfolder names go into the file and the frame. Use `--hide-names` for any folder
  that is not a demo; check the bars before rendering.
- **mtime is "not modified", not "not opened".** The script says "не менялось" on purpose; "never opened" would be a
  false claim. Wording must match what the tool actually measured.
- **Rounding is part of the claim.** Screen and voice use the same rounded value (`show_num`/`say_num`). If the voice
  says "девять и четыре" the screen must show `9,4`, not `9,38`.
- **Russian number words change form** ("один гигабайт", "два гигабайта", "пять гигабайт"). `num2words` does not
  agree the noun; reread `voice/chunks.json` and rephrase ("размер: девять гигабайт") rather than fight grammar.
- **A boring measurement means a different hook, not different numbers.** If the result has no drama, change the
  question or the folder. Never nudge the numbers.
- **Factcheck file.** Keep `real-numbers.json` next to the published reel; it answers "where did you get that?".
- **Pick a folder measured in gigabytes.** Below 1 GB the numbers round to 0 and `reel_from_numbers.py` warns; switch the unit in the script and `values()` for small targets.
- **Remeasured after recording?** `check_numbers.py` catches the mismatch; regenerate and re-voice.
- **Green QA is not approval.** Look at `qa/frames/` and listen to every number before calling it done.

## Related recipes

- `../../recipes/idea/idea-factcheck-file.md`: a file with sources for every claim
- `../../recipes/text/text-fact-lock-before-after.md`: lock facts before rewriting text
- `../../recipes/assembly/assembly-word-anchored-animation.md`: animation on the spoken word
- `../../recipes/qa/qa-dry-frame-review.md`: dry frame review before render
- `../../recipes/hooks/hooks-result-in-first-second.md`: the number is the hook
