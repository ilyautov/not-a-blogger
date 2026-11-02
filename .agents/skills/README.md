# Agent skills

[Русская версия](README.ru.md) · [Toolkit](../../README.md)

**15 focused skills + 3 coordinators.** Pick the smallest task you need. Each skill identifies its input, output
and boundary, then loads the relevant recipes/tools. These are project instructions, not additional render engines.
Keep them in this checkout: their references depend on it.

## Make one part

| Skill | Input → result |
|---|---|
| [nab-script](nab-script/SKILL.md) | Material/approved draft → spoken lines or a hook diff |
| [nab-shot-plan](nab-shot-plan/SKILL.md) | Approved lines → visible action, shots and first/last frames |
| [nab-assets](nab-assets/SKILL.md) | Shot plan/style → images or explicit generation prompts and provenance |
| [nab-motion](nab-motion/SKILL.md) | Existing scenes/timings → camera, action, cuts or transitions |
| [nab-voice](nab-voice/SKILL.md) | Approved text/permitted voice → selected takes and alignment |
| [nab-sound](nab-sound/SKILL.md) | Voice/events → music, SFX and mix evidence |
| [nab-captions](nab-captions/SKILL.md) | Words/timings → SRT/VTT or scoped caption changes |
| [nab-render](nab-render/SKILL.md) | Approved assets/audio/scenes → MP4, hash and build report |

## Check one part

| Skill | Input → result |
|---|---|
| [nab-qa-file](nab-qa-file/SKILL.md) | Exact MP4 → file/encoding/decode/loudness checks |
| [nab-qa-picture](nab-qa-picture/SKILL.md) | Final frames → contact sheet findings and timestamps |
| [nab-qa-speech](nab-qa-speech/SKILL.md) | Speech/script/alignment → per-line mismatches and missing checks |

## Publication materials and publisher components

| Skill | Input → result |
|---|---|
| [nab-publish-prep](nab-publish-prep/SKILL.md) | Finished video/provenance → titles, captions, credits and handoff |
| [nab-publisher-queue](nab-publisher-queue/SKILL.md) | Separate project/schema → offline queue and approval/ownership tests |
| [nab-publisher-adapter](nab-publisher-adapter/SKILL.md) | Queue contract/one platform → adapter implementation or specification |
| [nab-publisher-recovery](nab-publisher-recovery/SKILL.md) | Attempt evidence or project → incident findings or recovery implementation |

## Coordinate a whole workflow

| Skill | Input → result |
|---|---|
| [nab-video](nab-video/SKILL.md) | Coordinate video production; load only the current stage |
| [nab-video-qa](nab-video-qa/SKILL.md) | Combine applicable checks for the same finished file |
| [nab-publisher-builder](nab-publisher-builder/SKILL.md) | Coordinate the separate publisher build from its components |

A captions-only task preserves voice/scenes; a picture review does not trigger a rebuild; offline queue work
needs no browser adapter. The coordinators choose relevant stages instead of loading every skill. Instructions are
English; communicate with the person in their language. The full starter's existing
[reel-starter](../../starter/.agents/skills/reel-starter/SKILL.md),
[reels-direction](../../starter/.agents/skills/reels-direction/SKILL.md) and
[camera-moves](../../starter/.agents/skills/camera-moves/SKILL.md) remain supporting references.

## Codex

Open this repository as the project. Codex discovers `.agents/skills/` from the working directory up to the repository
root. Use `/skills` or type `$` to select one; restart if new skills have not appeared. Examples:

```text
$nab-captions Export SRT/VTT from my existing word timings. Keep the voice and scenes.
$nab-qa-picture Inspect the final MP4 frames; do not rebuild it.
$nab-publisher-queue Implement only the offline queue/approval store with fake-service tests.
$nab-video Help me make my first reel. I have Node 22 and ffmpeg, no Python.
```

Discovery: [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).
No global installation or configuration edit is required for these repo-scoped skills.

## Claude Code

Local project skills live in `.claude/skills/`. From this repository's root, copy missing folders:

```bash
mkdir -p .claude/skills
for skill_source in .agents/skills/nab-*; do
  skill_target=".claude/skills/${skill_source##*/}"
  if [ ! -e "$skill_target" ] && [ ! -L "$skill_target" ]; then
    cp -R "$skill_source" .claude/skills/
  fi
done
```

Existing copies are skipped, including old coordinators. After a toolkit update, review the changes and deliberately
refresh existing copies; there is no automatic synchronization. Invoke `/nab-captions`, `/nab-qa-picture` or another
skill by its directory name. See [Claude Code's local skill documentation](https://code.claude.com/docs/en/skills#choose-where-skills-load).
These project-local copies do not establish availability in Claude cloud sessions.

## Other agents and verification limits

Ask a file-capable agent to read only the selected `SKILL.md`, plus root `AGENTS.md`, and work in this checkout.
Native discovery is not required for this fallback. No special subagent system is required to use the skills.

Frontmatter/reference checks, copy fixtures and independent read-only scenarios cover structure, routing and handoffs.
They do not establish client-menu discovery, a newly rendered video, improved artistic quality or a real upload.
Publisher skills analyze/build components; they do not access live accounts or submit videos. Publication is initiated
by the person after review of the exact file. Existing partial-QA and approval boundaries remain unchanged.
