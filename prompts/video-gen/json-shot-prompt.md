# JSON shot prompt for a video model

- **Purpose:** assemble each shot's prompt from fields (passport, place, action, camera, negative) instead of writing
  it from scratch. Works for t2v, i2v and a2v.
- **Where tested:** LTX-2 locally (assembly from constants, camera field); an i2v service with a negative prompt.
- **Status:** partial. Assembly from constants and the camera anchor are proven on 1 probe (several a2v, i2v and
  t2v shots). The `negative_prompt` field is a hypothesis: requests with it never reached the model.

## Prompt

```json
{
  "shot": "{number}-{short name}",
  "mode": "a2v | i2v | t2v",
  "passport": "{character passport}",
  "place": "{place, light, lens: one line shared by all shots of the scene}",
  "action": "{what {character} does: one physical action and an emotion}",
  "speech": "he talks into the phone in {language}, mouth moving clearly with the speech | silent, mouth closed",
  "camera": "locked-off tripod shot, the camera does not move or zoom",
  "duration_s": "{duration}",
  "seed": 42,
  "negative_prompt": "frozen subject, camera zoom only, morphing face, duplicate limbs, extra fingers, text, logo, flicker"
}
```

String for the model: `passport + ", " + place + ", " + action + ", " + speech + ", " + camera`.

Tails matching the mood of the line are appended to `action`: `, menacing on the last word`, `, gives a curt order`,
`, impatient, jabbing the air`.

## Why

The shared `passport` and `place` fields are identical across all shots of a scene, so the hero and the light do not
drift from cut to cut. Only `action` changes, and editing one shot does not break the others. JSON is easy to keep
next to the video and rerun with a different seed.

## Pitfalls

- On a shout, the camera drifted off mid-line. The verbatim phrase `locked-off tripod shot, the camera does not
  move or zoom` fixed it. A short `static camera` is ignored by the model on emotional shots.
- A short B-roll "ducks landing on water" gave seagulls and palm trees on the first try. The details (breed, head
  colour, feet, splashes) had to be spelled out in full.
- Action chain without speech: the last frame of the previous clip becomes the input of the next i2v. Without this
  the hero's pose jumps at the cut.
- In a2v, speech in the clip must end at the edge of the window. If speech stops in the middle, the model fades the
  frame to black: cut the audio right after the end of speech plus 0.08 s.
