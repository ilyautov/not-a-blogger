[Русская версия](../ru/README.md)

# Textbook: videos with an agent, no blogging required

Learn to turn an idea into a short video with an AI agent: choose what happens, approve the script, stage the
picture, add sound and inspect the finished file. The course explains the decisions to you; [recipes](../../recipes/README.md)
give the agent exact steps and checks. You approve the script, listen and watch the result, and publish it yourself.

**Start without installing anything:** read [chapter 00](00-first-video.md), open one [real breakdown](../../examples/README.en.md),
and write your idea as “who, what happened, how it ended”. Bring that sentence to your agent.
The [roadmap](ROADMAP.md) gives the stages and their completion checks; its time labels are suggested pacing, not deadlines.

| Your starting point | Next step | What you get |
|---|---|---|
| New to video or agents | Chapter 00, then the [silent demo](../../starter-lite/README.md) | A route through the decisions, then a 15-second MP4; Node 22+ and ffmpeg for rendering, no Python or finished-file QA |
| Comfortable with code | [How it works](00a-how-it-works.md), then the [full starter](../../starter/README.en.md) | A Python 3.11/Node build, a contact sheet and a report; fake/no-ASR first, real voice and model setup separately |
| Already making videos | Pick a chapter, the [style atlas](04-image-and-frame.md#atlas-eight-ways-to-stage-one-story) or [recipes by symptom](../../recipes/BY-SYMPTOM.md) | One technique to try and a check to decide whether it helped |

The twelve numbered chapters (00, 00a, 01–10), roadmap and glossary work as a reference too. Read optional technical
depth when you need it. Chapters use real videos, measurements and mistakes, with exercises and links you can hand
to an agent. Exercise times are estimates; model installation and rendering vary by machine. Examples are not a
promise of reach, and green QA is permission to review, not approval to publish.

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
