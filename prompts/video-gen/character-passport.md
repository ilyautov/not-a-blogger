# Archetype character passport

- **Purpose:** a single descriptive phrase for a character, inserted at the start of every video-model prompt so the
  hero looks the same in all shots.
- **Where tested:** LTX-2 locally (`ltx-2-mlx`), t2v, i2v and a2v.
- **Status:** proven on 1 sketch probe: the accepted passport gave a recognizable look in every shot. The video was
  shelved because of the voice, not the video.

## Prompt

Passport template (keep it in English; video models understand it better):

```text
A {build} {archetype} in his/her {age}, {hair}, {eyebrows and eyes}, {stubble/skin}, {one striking detail},
{clothing top to bottom}, {characteristic facial expression}
```

Example of a depersonalized archetype:

```text
A tall wiry office accountant in his late thirties with neatly combed thinning hair, thin eyebrows, tired grey
eyes, pale skin, a pencil behind his ear, a wrinkled light-blue shirt with a loose dark tie, a nervous sideways
glance
```

How to insert: `{passport}, {place}, {action}, {camera}`, with the identical passport string in every shot of the
video.

## Why

A video model does not remember the hero between calls. Repeating the same full phrase holds the look better than a
short name. The passport describes an archetype, not a specific person: "a type, not a face". That is legally
cleaner, and the model does not pull in a celebrity's features. The facial expression in the passport sets the
personality; otherwise the hero is blandly neutral in every shot.

## Pitfalls

- The first passport, with glasses and a thick moustache, got "doesn't look like him": the model draws small
  accessories differently in each shot and they steal attention. The accepted version has no glasses or moustache
  and leans on eyebrows, stubble and expression.
- Do not put the character's name, an actor's name or "in the style of so-and-so" into the passport. This set does
  not support generating real people from a name or photo.
- An accepted passport does not save the video on its own: the probe was shelved because of the character's voice.
  Choose the voice before generating video.
