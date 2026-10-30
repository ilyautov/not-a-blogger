# real-tool-reel: a real tool works in the video

A short reel where the punch line is a small program that actually runs on your machine: the laptop speaks, a tab
closes by itself, a file appears. The screen recording or phone footage of the real run is the proof; the edited
reconstruction is only the frame around it. The example tool, `tool/focus_nag.py`, tells you off when you open a
distracting site and closes the tab on the third strike (macOS, Safari / Chrome).

## When to use it

- "I asked an agent to build X" reels: the result must run on camera, not in a mockup.
- You can give the tool away (a gist, a repo, a code word): a working artifact is the best call to action.
- Not for tools that touch accounts, money, messages or other people. If it needs a login or sends anything, it is
  not a demo tool.

## Pattern

1. **Build the tool small and safe.** Standard library, one file, readable in a minute. **Dry run by default**: the
   real action needs an explicit flag (`--live`). The logic is separated from the OS calls so it can be tested.
2. **Write the scenario as a dry-run feed** (`tool/demo.tsv`): the beats of the video as input lines. The printed
   actions are your shot list, and the same file is the test.
3. **Shoot the real run** with `SHOOT.md`: permission prompt, the action, the terminal log.
4. **Edit**: real footage for the proof shots, your usual scene for the hook and the explanation.
5. **Give the tool away** with a README that lists every permission it asks for and how to revoke it.

## Run the example

Needs Python 3.9+. The dry run works anywhere; `--live` needs macOS.

```bash
cd templates/real-tool-reel/tool
python3 focus_nag.py --feed demo.tsv                 # dry run of the scenario: prints strikes and actions
printf 'Safari https://youtube.com\n' | python3 focus_nag.py
python3 focus_nag.py --live --check                  # macOS: shows what it sees once, triggers the Automation prompt
python3 focus_nag.py --live                          # real run; Ctrl+C to stop
```

## What to replace

1. `tool/config.json`: `blocklist`, `lines` (`say:<text>` uses macOS `say`; or record your own and point to a file
   next to the script, e.g. `sounds/1.aiff`; recordings are not kept in this repo), `voice`, `work_url`.
2. `tool/demo.tsv`: your video's beats.
3. Or replace the tool entirely, keeping the shape: logic class with `step()` -> list of actions, a `DryRun` source
   that prints, a `Mac` (or other OS) executor behind `--live`.
4. `SHOOT.md`: the bracketed beats.

## Gotchas

- **Permissions are part of the story.** The example needs only Automation (Terminal -> browser). Front app comes
  from `lsappinfo`, so Accessibility and Screen Recording are not needed; if macOS asks for them, deny and debug.
- **Strike 3 re-checks the tab before closing it.** After the last line plays, the tab is closed only if the same
  browser is still in front and its front tab still shows the URL that earned the strike (checked and closed in one
  AppleScript call). Switch tabs during the line and nothing is closed or opened; so do not switch on camera.
- **Poll interval vs. your pauses.** The tool looks every `interval_s`; act slower than that on camera.
- **Firefox and some Chromium forks do not expose the tab URL** to AppleScript. Brave and Edge accept the Chrome
  dialect (`"Brave Browser": "chrome"` in `browsers`), untested.
- **Private windows are visible too**: the URL is read the same way. Say so in the tool README.
- **Run as a LaunchAgent** and the permission is asked for `python3`, not Terminal.
- **Never film your publishing browser profile** or anything with accounts; use a clean profile.
- **The reconstruction is not the proof.** If the tool did not run on camera, do not say it did.

## Related recipes

- `../../recipes/cta/cta-promise-free-tool.md`: a working tool as the call to action
- `../../recipes/cta/cta-deliver-before-asking.md`, `../../recipes/cta/cta-page-per-codeword.md`
- `../../recipes/agent/agent-verify-cli-in-binary.md`: check what the tool really does before claiming it
- `../../recipes/qa/qa-green-is-not-approval.md`
