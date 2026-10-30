[Русская версия](../ru/ROADMAP.md)

# Learning roadmap

You can read the textbook front to back, but that takes longer than it needs to. Here it's laid out in four stages.
Each one leaves you with a result in hand and has a "done" signal. Until you have that signal, don't move on: each
stage builds on the one before.

| Stage | Time | What you get | What you need |
|---|---|---|---|
| 1. First evening | 1–2 hours | your own video without a voice, and an understanding of how it's built | Node.js and ffmpeg |
| 2. First week | 3–5 evenings | a video with your own or a synthesized voice, plus a check report | Python 3.11, an Apple Silicon Mac |
| 3. First month | 4–8 videos | published videos and a table of their metrics | platform accounts |
| 4. Beyond | as you go | carousels, covers, your own templates, working with an agent at volume | the same |

## Stage 1. First evening: see how it works

**What you do.**

1. Watch three breakdowns: the most successful one, ["The TV showed an ad"](../../examples/tv-no-ads/README.en.md),
   the first video on the current engine, ["Free up my Friday"](../../examples/free-friday/README.en.md), and a flop,
   ["3 Claude Code keys" as a repeat](../../examples/three-keys-repeat/README.en.md). Notice what each says about the
   hook and about what went wrong.
2. Build a video in [starter-lite](../../starter-lite/README.md): `npm run render`. Change the text in
   `compositions/hook.html` to your own and build again.
3. Read [chapter 00a, "How it works"](00a-how-it-works.md) and do the first three steps of its exercise.

**Done when** you have your own `first-video.mp4` with your text, and you can explain why the video is rendered frame
by frame instead of being screen-recorded.

**If you're stuck.** `npm run render` won't run: check `node --version` (22+ needed) and `ffmpeg -version`, then
reread the install part of the [starter-lite README](../../starter-lite/README.md).

## Stage 2. First week: a video with a voice

**What you do.**

1. Install the full [starter](../../starter/README.en.md) following its "Install" section and run the beep demo:
   `./make.sh fake`, `./make.sh frames`, `FINISH_ARGS=--no-asr ./make.sh all`. A `preview_partial` status is normal
   here.
2. Read [chapter 00](00-first-video.md) in full. It's the route of one video from idea to file.
3. Write a script of 4–8 lines about one situation and run it through a humanizer as in
   [chapter 02](02-text-humanizer.md).
4. Voice it. The simplest way is to record it yourself: put your lines into `voice/chunks.json` and
   `voice/lines.json` (their count must match the number of recordings, and update the word anchors in `scene/scene.ts` to the new lines), record one file per line and import them:
   `./make.sh live voice/my-0.m4a voice/my-1.m4a …`. The step-by-step version is in
   [FIRST-TASK.md](../../starter/FIRST-TASK.md), sections 2–3 (in Russian). For an English video, first run
   `export ASR_LANG=en`: recognition defaults to Russian (see the "Language" note in section 3 of the
   [starter README](../../starter/README.en.md)). Speech synthesis and its traps are covered in
   [chapter 03](03-voice.md).
5. Build the video and read `qa/final-result.json`. If a line failed recognition, fix the text or re-record the take,
   not the threshold.

**Done when** `qa/final-result.json` shows `ready_for_user_preview` on your voice, you listened to the whole video
yourself, and you showed the script to someone before building.

**Recipes for this stage:** [qa-asr-per-take](../../recipes/qa/qa-asr-per-take.md),
[voice-stress-by-rewording](../../recipes/voice/voice-stress-by-rewording.md) (tested on Russian only),
[voice-record-reference-clean](../../recipes/voice/voice-record-reference-clean.md),
[qa-green-is-not-approval](../../recipes/qa/qa-green-is-not-approval.md).

## Stage 3. First month: videos people watch

A technically assembled video and a video people finish are different things. This stage is about the second.

**What you do.**

1. Before each video: [chapter 01](01-idea-hook-script.md) on the situation, a hook in the first second and one example.
2. While building: [chapter 04](04-image-and-frame.md) on the frame, [05](05-camera-editing.md) on camera and editing,
   [06](06-sound-captions.md) on sound and captions.
3. After building: [chapter 07](07-assembly-qa.md). Measure frame fill on the finished mp4 and look at the contact
   sheet.
4. Publish yourself, following [chapter 08](08-vertical-publishing.md). On our small channel, over two weeks, videos
   from the fourth YouTube upload of the day on got almost no views
   ([publishing-first-three-slots](../../recipes/publishing/publishing-first-three-slots.md)). That's one channel's
   observation, not a platform rule: write the day's upload number next to each video and check it on yours. We also
   don't upload two versions of the same video back to back.
5. A week after each video goes out, write down views and comments. Compare against the median of your own videos, not
   someone else's numbers.

**Done when** 4–8 videos are published and you have a table: video, platform, date, views and average percentage
viewed on day seven, multiple of your median, which hook and technique it used. Over 4–8 videos that isn't proof yet,
it's your first hypotheses: which technique to repeat in the next video and compare with everything else kept equal.

**Recipes for this stage:** [qa-frame-fill-mp4](../../recipes/qa/qa-frame-fill-mp4.md),
[qa-dry-frame-review](../../recipes/qa/qa-dry-frame-review.md),
[assembly-word-anchored-animation](../../recipes/assembly/assembly-word-anchored-animation.md),
[sound-music-rotation](../../recipes/sound/sound-music-rotation.md). The full list by symptom:
[recipes/BY-SYMPTOM.md](../../recipes/BY-SYMPTOM.md).

## Stage 4. Beyond

Pick by what you need.

- **Carousels, covers, slide decks.** [Chapter 09](09-carousels-slides.md) and the tools in
  [tools/](../../tools/README.md). One article gives you both a PDF and a carousel.
- **Working with an agent at volume.** [Chapter 10](10-working-with-agent.md): how to set the task, what to check
  yourself and what not to trust the agent with.
- **Your own formats.** Templates in [templates/](../../templates/README.md): 3D skit, numbers-driven reel, sketch
  dialogue, a reel with a real tool.
- **Contributing to the kit.** A breakdown of your own video with numbers, a line about speech-synthesis pitfalls in
  your language, or a measurement that moves a recipe from hypothesis to proven. How: [CONTRIBUTING.md](../../CONTRIBUTING.md).

There's no **done** here. A good sign: you found a pitfall that isn't in [gotchas/](../../gotchas/README.md) and wrote
it down.

## How to read the rest

- A word is unclear: the [glossary](glossary.md).
- Something broke: [recipes/BY-SYMPTOM.md](../../recipes/BY-SYMPTOM.md) finds a recipe by symptom.
- You need an example: [examples/](../../examples/README.en.md); every breakdown links to the techniques it used.
- The textbook as one PDF: [latest release](https://github.com/ilyautov/not-a-blogger/releases/latest).
