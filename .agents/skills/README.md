# Agent skills

[Русская версия](README.ru.md) · [Toolkit](../../README.md)

Three repo-scoped entry points turn a request into the right recipes and tools. They are instructions for your
agent, not new renderers or a hosted service. Keep them in this checkout: they reference its files.

| Skill | Use it for | What it returns |
|---|---|---|
| [nab-video](nab-video/SKILL.md) | Make or revise a short video | An appropriate build path, script/staging approval and an honest final handoff |
| [nab-video-qa](nab-video-qa/SKILL.md) | Review an MP4 or QA report | Checks tied to the exact file, visual findings and what was not checked |
| [nab-publisher-builder](nab-publisher-builder/SKILL.md) | Build your own publisher | A separate implementation or build brief, offline recovery tests and account-test instructions |

The full starter already includes [reel-starter](../../starter/.agents/skills/reel-starter/SKILL.md),
[reels-direction](../../starter/.agents/skills/reels-direction/SKILL.md) and
[camera-moves](../../starter/.agents/skills/camera-moves/SKILL.md). The new entry points reuse them; they don't replace
their production-specific instructions. The three new skills are English; communicate with the person in their language.

## Codex

Open this repository as the project. Codex discovers `.agents/skills/` from the working directory up to the repository
root. Use `/skills` or type `$` to select one; restart if new skills have not appeared. For example:

```text
$nab-video Help me make my first reel. I have Node 22 and ffmpeg; no Python or voice setup.
$nab-video-qa Review starter/output/final.mp4 and its QA report. Tell me what is still unverified.
$nab-publisher-builder Build a separate publisher for my YouTube account. Start with offline recovery tests.
```

Discovery instructions: [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).
No global installation or configuration edit is required for these repo-scoped skills.

## Claude Code

Local Claude Code project skills live in `.claude/skills/`. From the repository root, copy the three folders if the
destinations do not already exist (review an existing copy before replacing it):

```bash
mkdir -p .claude/skills
cp -Rn .agents/skills/nab-video .claude/skills/
cp -Rn .agents/skills/nab-video-qa .claude/skills/
cp -Rn .agents/skills/nab-publisher-builder .claude/skills/
```

Invoke `/nab-video`, `/nab-video-qa` or `/nab-publisher-builder`. See
[Claude Code's local skill documentation](https://code.claude.com/docs/en/skills#choose-where-skills-load).
These copies are project-local; the instructions above do not establish availability in Claude cloud sessions.
After updating the toolkit, refresh copies deliberately. There is no automatic synchronization.

## Other agents and verification limits

Ask a file-capable agent to read the selected `SKILL.md`, the root `AGENTS.md` and follow them in this checkout.
This fallback does not require native skill discovery; it also does not claim native integration with every agent.

Frontmatter/link checks and independent read-only scenarios validate structure and handoff behavior. They do not
prove client-menu discovery, a new rendered video, a real upload or a better artistic result. The publisher builder
does not perform account login or publication. The person still reviews the exact file and initiates publication.
