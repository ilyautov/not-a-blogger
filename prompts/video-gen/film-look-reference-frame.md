# Film-look shot in two steps: reference frame, then motion to the line's audio

- **Purpose:** a talking character shot with a pushed-35-mm-film look and a calm upper third for captions. Step 1
  gets a still from an image generator; step 2 hands that still plus the line's wav to a video model, which only has
  to move it. Without a reference frame the character's face drifts from shot to shot.
- **Where tested:** step 1 on a CLI image generator (any model that takes a long prose prompt); step 2 on LTX-2
  locally in image + audio mode, 704×1248, 24 fps.
- **Status:** proven on 1 probe (a "film" probe the author accepted as a look). The negative-style phrasing ("not an
  ad, not CGI") was tested only in this wording.

## Prompt

Step 1, reference frame. The subject is one sentence at the end; everything before it is a constant preamble.

```text
Vertical 9:16 frame. The upper third of the frame is calm and dark, with plenty of air above the character's head
(captions go there). The character occupies the lower two thirds. No text, no letters, no logos, no writing on
screens or objects. A frame shot on 35 mm cinema film (high-ISO stock, push-processed): strong visible film grain
across the whole frame, slightly lifted blacks, a light vignette, soft 35 mm optics with no digital sharpness.
Limited palette of three or four colours: dirty green shadows, warm tungsten yellow, dull monitor blue; muted
saturation, no trendy teal-and-orange, no gloss. Hard light: one bare desk lamp from the side, sharp shadows with a
clear edge, blown highlights in places, the background falls almost to black. The feel of a frame from a
low-budget independent film of the early 2000s, not an advert and not CGI. {place: e.g. a cramped night office, a
cluttered desk}. Restrained acting: the face almost still, emotion only in the eyes.
Subject: {character passport}, {where they stand or sit}, {where they look}, {emotion}
```

Step 2, motion for the video model (the model received the English original). The frame from step 1 is the image
input; the line's wav is the audio input.

```text
Grainy 35mm film footage from a low-budget indie movie. {character passport} sits at a cluttered desk at night
under a hard desk lamp. It speaks calmly: {how exactly it moves while speaking}. Restrained acting: the face almost
still, emotion only in the eyes, no exaggerated expressions. Static locked-off camera, heavy film grain.
```

Example filled in for a prop character (a mascot, not a person):

```text
Grainy 35mm film footage from a low-budget indie movie. A small matte terracotta-orange ball robot prop with a dark
visor and two cream glowing eye lights sits on a cluttered desk at night under a hard desk lamp. It speaks calmly:
its eye lights dim and brighten with the speech, the body tilts very slightly. It has no mouth. Practical movie prop,
static locked-off camera, heavy film grain.
```

## Why

An image generator holds a look (grain, palette, light) far better than a video model does, and a still is cheap to
redo until it is right. The video model then gets the face, the light and the composition as pixels, not as words,
so they stay put across shots. The calm upper third is reserved in the prompt, not cropped afterwards: captions are
composited on top in code. The same film-look sentences are repeated in step 2 so the model does not "clean up" the
grain while animating. For a character without a mouth, say what moves instead (lights, tilt), or the model invents
a mouth.

## Pitfalls

- Skipping step 1 and generating t2v per line: the face changed between shots even with an identical passport.
- Speech in the audio must end at the edge of the clip; speech stopping mid-clip made the model fade to black (see
  the neighbouring JSON shot prompt).
- A short "static camera" is ignored on emotional lines; the verbatim `static locked-off camera` holds.
- Pick the reference frame from a contact sheet of several seeds, not from the first acceptable one (see
  [seed-sweep-still.md](seed-sweep-still.md)).
- Generate only an archetype or a mascot, or your own face with your own recording; never a real third party.
  Chunking, padding the wav and local timings: [recipes/face/face-ltx-a2v-local.md](../../recipes/face/face-ltx-a2v-local.md).
