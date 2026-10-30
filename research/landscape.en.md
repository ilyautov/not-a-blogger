[Русская версия](landscape.md)

# Neighbors in the space

Open-source projects that solve similar problems. This isn't a ranking or an ad, but a map: what already exists, under
which license, and how it differs from this kit. Checked 2026-10-23. Know a neighbor that's missing? Add a row via PR.

## Video made by an agent

| Project | License | What it is | Difference from this kit |
|---|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | HTML → video for agents, a block registry | an engine; we build on it and describe techniques on top |
| [browser-use/video-use](https://github.com/browser-use/video-use) | MIT | an agent edits existing footage | works with shot material; we usually build the frame from scratch |
| [nateherkai/herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) | MIT, except the author's brand assets | a reel-editing kit on HyperFrames | English-language, tied to the author's brand |
| [latent-spaces/brag](https://github.com/latent-spaces/brag) | MIT | a project launch video from one skill | a narrow format: a 20-second promo |
| [nexu-io/html-video](https://github.com/nexu-io/html-video) | Apache-2.0 | programmatic video HTML → MP4, templates | templates without video metrics |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | AGPL-3.0 | agentic video production, 12 pipelines | we don't take code from it because of AGPL |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | MIT | topic → finished short in one click | a "topic → stock → TTS" factory; this is exactly what we consider a source of slop |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | Unlicense | cutting out pauses | a single operation, complements this kit well |
| [mifi/editly](https://github.com/mifi/editly) | MIT | declarative editing JSON → video | no techniques and no QA |
| [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas) | MIT | animations in TS code | an engine |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Remotion License, not OSI | video in React | the license restricts companies with more than 3 people |

## Text

| Project | License | What it is | Difference |
|---|---|---|---|
| [ilyautov/humanizer-ru](https://github.com/ilyautov/humanizer-ru) | MIT | editing Russian text for agents, a scanner, eval | our sibling project, plugged in by link |
| [blader/humanizer](https://github.com/blader/humanizer) | MIT | an English-language humanizer based on the Wikipedia guide | English |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | MIT | skill + detector + fixtures | English; an exemplary contribution setup |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | MIT | a single SKILL.md with clichés | English |

## Carousels and presentations

| Project | License | What it is | Difference |
|---|---|---|---|
| [slidevjs/slidev](https://github.com/slidevjs/slidev) | MIT | slides from Markdown | a full framework; we use one HTML file with no build step |
| [marp-team/marp-cli](https://github.com/marp-team/marp-cli) | MIT | Markdown → PDF/PPTX/PNG | good for decks, no text gates |
| [presenton/presenton](https://github.com/presenton/presenton) | Apache-2.0 | an open alternative to Gamma | a service with a UI |
| [vercel/satori](https://github.com/vercel/satori) | MPL-2.0 | HTML/CSS → SVG for cards | a renderer library |
| [Hainrixz/open-carrusel](https://github.com/Hainrixz/open-carrusel) | MIT | Instagram carousels via chat with Claude | no text checks before rendering |

## Voice

| Project | License | Note |
|---|---|---|
| [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | code MIT, weights CC BY-NC | the basis of our TTS gotchas |
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | Apache-2.0 | a lightweight TTS without the NC restriction, Russian not tested |

## What we didn't find anywhere

- a Russian-language "video by an agent" kit;
- a repository that publishes the real view counts of its videos, flops included;
- a catalog of Russian TTS and ASR gotchas.

That is exactly where this kit fits.
