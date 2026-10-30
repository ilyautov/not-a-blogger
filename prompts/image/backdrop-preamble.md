# Atmospheric backdrop: AI draws only the background

- **Purpose:** a preamble for generating a cinematic backdrop for a video. An image without a single letter, with an
  empty area for a title that code adds later.
- **Where tested:** the built-in image generator of Codex CLI (via `codex exec`, see the neighbouring prompt).
- **Status:** proven on 2 videos: a probe and a long video that the author accepted and published. A series of
  three frames kept a consistent art direction.

## Prompt

The preamble is concatenated with the subject: `PREAMBLE + subject`.

```text
Cinematic 16:9 frame for a video title card. Dark scene, deep shadows, a single light source from the side, light
haze and highlights on wet surfaces. Accent colour: {accent color}, used in the rim light and small details,
everything else almost monochrome, with a warm spark. Composition with empty air on the left or at the top for
large typography. Photorealism, wide lens, shallow depth of field. NO text, NO letters, NO captions, NO logos, NO
interfaces or screens with text. Subject: {subject}
```

`{accent color}` is a name plus a hex code, for example `acid lime (#d6ff43)`: the model reads the name, the code
keeps the series consistent. The accent goes only into highlights; the base stays near-monochrome.

The subject is always the last sentence and always one sentence: a metaphor for the topic, the camera angle and the
side with "air" for the text. Examples:

```text
{character} as a mechanic in a dark garage next to a race car, low angle from the floor, night rain beyond the open gate, air on the left for the title
```
```text
a heavy steel vault door in a dark corridor, the lock lit in the accent colour, air on the right
```
```text
an archaeological dig inside a server room: rock layers with old hard drives and tapes sticking out, a spotlight from above
```

## Why

An image generator writes letters poorly and does not know your layout, so text, numbers and interface are always
drawn by code on top. Non-Latin scripts are worse still: generators mangle Cyrillic into pseudo-letters, so a
Russian title is never asked of the model, it is composited on the finished backdrop. The ban on text is repeated in capitals five times: a single "no text" is not enough for the
model. The "air" side in the subject leaves room for the title, so the backdrop does not have to be cropped blindly.

## Pitfalls

- Without the air side, the main object lands in the centre and the title falls right on top of it.
- Our dark palette was for a long time copy-paste inertia, not a decision. If your brand palette is light, change
  the first two sentences of the preamble, not just the accent colour.
- Screens and monitors in the subject provoke the model into drawing pseudo-text. Write "screen without text" or
  drop the screen.
- A backdrop is background, not content. A video made only of pretty backdrops with no events in frame was called
  static by the author.
