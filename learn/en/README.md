[Русская версия](../ru/README.md)

# Textbook: videos with an agent, no blogging required

This textbook is for humans. The recipes in [recipes/](../../recipes/README.md) are written for the agent: short,
with parameters and a check. Here we explain the why, using real videos from [examples/](../../examples/README.en.md),
with the numbers told as a story and the mistakes we learned from. Every section ends with a link to a recipe you
can hand to your agent.

Each chapter opens with a real published video, walks through the techniques as "the problem, how we spotted it,
what we do, where it breaks", and ends with a 15–30 minute exercise and a "Don't" list.

Not sure where to start: the [learning roadmap](ROADMAP.md) lays the textbook out in four stages, from the first
evening to the first month, with a "done" signal at each. If you read front to back, start with chapter 00: it takes
you through the whole path in one evening. Chapter 00a explains how it all works under the hood. Read the rest as you
hit each stage.

The whole textbook as one PDF is in the [latest release](https://github.com/ilyautov/not-a-blogger/releases/latest).
To build it yourself: `python3 scripts/build_textbook_pdf.py` (needs the dependencies from
[tools/carousels/requirements.txt](../../tools/carousels/requirements.txt) and poppler: `brew install poppler`).

## Contents

| # | Chapter | What it covers |
|---|---|---|
| — | [Learning roadmap](ROADMAP.md) | Four stages: first evening, first week, first month, beyond; what to do and when to move on |
| 00 | [Your first video in one evening](00-first-video.md) | A ten-stage route from idea to publishing, with a "done" signal at each stage |
| 00a | [How it works](00a-how-it-works.md) | A video as a program, the pipeline step by step, the frame as a function of time, Pygmalion → Diffusion Studio → HyperFrames, which engine to pick when |
| 01 | [Idea, hook, script](01-idea-hook-script.md) | A situation instead of a tool, hits by the median, remaking the rhythm, a hook at 0.0 s, the knowledge chain |
| 02 | [Text and the humanizer](02-text-humanizer.md) | Cleaning the script before voicing, fresh model tells, surgical edits, the fact lock, slop of form |
| 03 | [Voice and TTS](03-voice.md) | The hero's live voice, choosing an engine blind, stress, sacrificial words, pauses, checking takes |
| 04 | [Image, frame, face and character](04-image-and-frame.md) | One zone without chrome, real photos, backgrounds, parallax, generative inserts, faces |
| 05 | [Camera, editing, transitions](05-camera-editing.md) | Why a slow push-in isn't motion, shot size through cuts, handheld camera, cut rhythm |
| 06 | [Sound and captions](06-sound-captions.md) | Whooshes on cuts, SFX by meaning, music rotation, −15 LUFS ±1, captions: growing upward, contrast, font, karaoke cache |
| 07 | [Assembly and QA](07-assembly-qa.md) | The frame as a function of time, per-word animation, heavy steps one at a time, green QA isn't "done", fill and stillness |
| 08 | [Vertical, publishing, call to action and analytics](08-vertical-publishing.md) | Re-layout instead of crop, upload pitfalls, the "made for kids" flag, the code word, the hit metric, platforms don't transfer |
| 09 | [Carousels, covers, slide decks](09-carousels-slides.md) | Content separate from look, gates before and after render, fonts, the cover, an HTML deck with a PDF backup |
| 10 | [The agent as editor, brand and character](10-working-with-agent.md) | How to brief the agent, what not to trust it with, how to check its work |
| — | [Glossary](glossary.md) | TTS, ASR, LUFS, take, seed, hook, render and the other words the chapters use without stopping |

## How a chapter is built

- **Example.** A poster and a short story about the video: what was in it and how it turned out.
- **Techniques.** Each subsection: the problem on the example, the number that showed it to us, what we do, where
  the technique breaks. The last line links to the "Agent recipe".
- **Exercise.** Something to do yourself in 15–30 minutes, without installing models where possible.
- **Don't.** A short list of the chapter's pitfalls.

## Where else to look

- Video breakdowns with metrics, failures included: [examples/](../../examples/README.en.md).
- One-line pitfalls with a number: [gotchas/](../../gotchas/README.md).
- Anonymized niche research and the blind TTS test: [research/](../../research/README.en.md).
- The template your first video is built on: [starter/](../../starter/README.en.md).
