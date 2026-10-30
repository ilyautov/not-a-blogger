# GitHub repository settings (to apply by hand)

Proposed values for Settings → General and the About box. Nothing here is applied automatically; the maintainer sets
them when the repository is opened.

## Description (≤ 350 characters)

```
An AI agent builds reels, carousels and covers; QA measures the finished file; a person says "ship it". 142 recipes with numbers, 12 breakdowns of published videos including flops, a no-Python starter.
```

## Website

```
https://aifrontier.tech
```

## Topics (GitHub allows up to 20; lowercase, hyphens)

```
claude-code
codex
ai-agents
agent-skills
ai-video
video-generation
shorts
reels
youtube-shorts
tiktok
hyperframes
tts
speech-recognition
whisper
ffmpeg
content-creation
video-qa
carousels
russian
```

## Other

- Social preview: upload `assets/social-preview.jpg` (1280×640).
- Features: Issues on, Discussions optional, Wiki off, Projects off.
- Security: enable "Private vulnerability reporting" (SECURITY.md points to it).
- After opening: add the stars badge to both READMEs and create 5–10 `good first issue` items from `ISSUES-SEED.md`.

Apply with the CLI if preferred (run by the maintainer, not by an agent):

```bash
gh repo edit ilyautov/not-a-blogger \
  --description "An AI agent builds reels, carousels and covers; QA measures the finished file; a person says \"ship it\". 142 recipes with numbers, 12 breakdowns of published videos including flops, a no-Python starter." \
  --homepage "https://aifrontier.tech" \
  --add-topic claude-code,codex,ai-agents,agent-skills,ai-video,video-generation,shorts,reels,youtube-shorts,tiktok,hyperframes,tts,speech-recognition,whisper,ffmpeg,content-creation,video-qa,carousels,russian
```
