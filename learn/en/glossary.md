[Русская версия](../ru/glossary.md)

# Glossary

Short plain-word definitions of the terms the textbook and the recipes use without stopping to explain. Where a
term has a number behind it, the link goes to [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md); where a chapter tells
the story, the link goes to the chapter. The Russian file keeps the same order.

## The workbench

- **Repository.** A folder with code and its instructions, kept on GitHub. You download it; nothing installs by itself.
- **Model / weights.** A model is a trained neural network. Its weights are the big file with what it learned; they
  download separately from the code and often carry a different license (see [THIRD-PARTY.md](../../docs/THIRD-PARTY.md)).
- **Terminal.** The window where you type commands and the computer answers with text. It is not a chat with the AI:
  it runs exactly what you type.
- **Agent.** An AI that can run commands, edit files and check its own results, not just write text. Claude Code,
  Codex and Cursor are agents; [chapter 10](10-working-with-agent.md) is about working with one.
- **Prompt.** The text you give the AI: the task, the limits, what "done" looks like. Ready prompts live in
  [prompts/](../../prompts/README.md).
- **GPU.** The graphics card. Video models count fastest on an NVIDIA card; the starter and the depth model run
  without one, a generative video model is slow or impossible without one.

## Picture and assembly

- **Scene / composition.** One piece of the video with its own layout and timing; the video is a chain of scenes.
  A composition is the whole set with the music and captions laid on top ([chapter 07](07-assembly-qa.md)).
- **Preview vs render.** Preview is the scene playing in the browser so you can look at it. Render is the engine
  drawing every frame and writing a file. They are different commands; a working preview is not a video yet.
- **MP4 export.** The render's result: one `.mp4` file with picture and sound. Proof of export is the file path and
  its length, not a screenshot or an HTML folder.
- **Hook.** The first seconds that make a viewer stay: the result, the conflict or the question up front
  ([chapter 01](01-idea-hook-script.md)).
- **CTA.** Call to action: what you ask the viewer to do at the end, a code word in the comments, a link, a follow.
  Give the material first, then ask ([chapter 08](08-vertical-publishing.md)).
- **LUT / film look.** A LUT is a color table that recolors the whole frame in one pass; a film look is a LUT plus
  grain and softness that make digital frames look shot on film.
- **Depth map.** A grey picture of a photo where bright means near and dark means far, made by a model from the
  single photo ([chapter 04](04-image-and-frame.md)).
- **Parallax.** Near layers move faster than far ones when the camera moves. Cut a photo into layers by its depth
  map and you get motion inside a still picture ([chapter 05](05-camera-editing.md)).
- **Contact sheet.** One image with many small frames from the video in a grid, one per second or two. Lets you see
  the whole video on one page before watching it ([chapter 07](07-assembly-qa.md)).

## Voice

- **TTS.** Text-to-speech: a model reads your text aloud. A voice clone is TTS that imitates a given recording
  ([chapter 03](03-voice.md)).
- **Reference (voice).** The 3–10 second recording of a voice that the clone imitates, with its exact transcript.
  How to record one: [chapter 03](03-voice.md).
- **Take.** One synthesized or recorded version of one line. You make several, check each and keep the best.
- **Seed.** The number that fixes the model's randomness. With our synthesis (F5 with seed 42), the same seed and text
  with the same model, reference, settings and machine gave the same file byte for byte. That's not a guarantee for
  every engine and every piece of hardware. So we fix a bad take by changing the text, not by re-running with the same
  seed; you can change the seed too, but then everything else in the take changes as well ([chapter 03](03-voice.md)).
- **ASR.** Speech recognition: the reverse of TTS, audio back into text. We run it on every take and compare with the
  script; the floor is in [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md).
- **Karaoke / word timestamps.** The start and end time of every spoken word, taken from ASR with alignment. Captions
  and per-word animation are built from them ([chapter 06](06-sound-captions.md)).

## Sound

- **LUFS.** The loudness unit platforms and ears agree on; more negative means quieter. Our target for a finished
  video is in [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md).
- **True peak.** The loudest instant of the sound after encoding, in dBTP. Too close to zero and the file crackles;
  the ceiling is in [QA-THRESHOLDS.md](../../docs/QA-THRESHOLDS.md).
- **Pad (music bed).** A quiet, even background sound under the voice when there is no real track. The starter
  synthesizes one by itself ([chapter 00](00-first-video.md)).
- **Ducking.** Turning the music down while someone speaks and back up in the gaps, so the voice is never covered.
- **Stems.** Separate audio tracks of one mix: voice, music, sound effects. Kept apart so you can relevel one without
  touching the others.

## Checking

- **QA.** Quality check: the scripts and the eyes that look at the finished file before anyone publishes it. A green
  QA means no known defect was found, not that the video is good ([chapter 07](07-assembly-qa.md)).
