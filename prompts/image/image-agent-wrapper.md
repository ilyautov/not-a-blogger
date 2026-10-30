# Wrapper task for image generation by an agent

- **Purpose:** make a CLI agent with a built-in image generator produce exactly one image and nothing else: no code,
  no extra files, no reading of project rules.
- **Where tested:** Codex CLI, `codex exec --sandbox workspace-write --skip-git-repo-check`.
- **Status:** proven on 2 videos; three frames generated in parallel in about 77 s.

## Prompt

```text
Generate ONE image with the image generation tool and save it as ./out.png in the current folder.
Aspect ratio 16:9, maximum quality. {image prompt}

Do nothing else: do not write code, do not create other files. At the end print only the absolute path to the file.
```

Run from an empty temporary folder:

```bash
set -euo pipefail
prompt_file="$PWD/wrapper.txt"                  # absolute path, resolved before leaving the project folder
prompt=$(cat "$prompt_file")                    # fails here if the file is missing
[ -n "$prompt" ] || { echo "empty prompt: $prompt_file" >&2; exit 1; }
tmp=$(mktemp -d)
cd "$tmp"
codex exec --sandbox workspace-write --skip-git-repo-check "$prompt"
test -s "$tmp/out.png" || { echo "no image in $tmp" >&2; exit 1; }
```

Read the prompt before `cd`: after the jump into the empty folder a relative `wrapper.txt` no longer exists, and
without `set -e` and the checks the agent gets an empty string while the whole chain still exits 0.

## Why

The empty folder keeps the agent from picking up the project's `AGENTS.md` and starting to "help" by its rules.
"Do nothing else" stops the agent from writing a generation script instead of calling the tool. Printing a single
path makes the output machine-readable: a script picks up the file without parsing text.

## Pitfalls

- The generator returns an image that is only "roughly 16:9". A script after it center-crops the frame to the exact
  size.
- Record the prompt, tool, date and sha256 next to the image in `manifest.json`. A month later you otherwise cannot
  reconstruct how the background was made or check its licence.
- Without the phrase "do nothing else", the agent tends to write code around the generation instead of making one
  tool call.
