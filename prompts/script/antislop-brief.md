# Anti-slop section of a brief

- **Purpose:** a block pasted into an agent's brief before a batch of videos. It lists why past videos were called
  slop and forbids repeating it.
- **Where tested:** Claude Code, a batch of 5 short videos on different visual worlds.
- **Status:** proven on 5 videos: the author accepted 3, one was published. Before this block, two back-to-back
  copies of a successful video were both rated "slop".

## Prompt

```text
## Why past videos were called slop (do not repeat)
- The same skeleton in every video: dark background, text card, {character} in a circle in the corner, subtitles,
  a banner. The assembly line is recognizable by the second video.
- Formulaic narrator lines: "Remember this phrase", "First / Second / Third", "Plus... three things in a row".
- A wall of small on-screen text. {character} has no personality, just a talking head.
- What works: a live situation, absurdity, {character} with a role in the scene, one clear idea, proof on screen.

## Every video gets its own visual world
- A new scene in its own file. Do not copy the layout of neighbouring scenes; borrow techniques only.
- A visual metaphor taken from the story itself (a form, a chat, a report, a detector). Constant motion in frame,
  large elements, little text.
- Large subtitles, readable on a phone, never covering the main subject.
- Visual worlds already used (do NOT repeat): {list of worlds from past batches}.
- Do not take topics from past batches: {list of topics}.

## Video recipe
Metaphor from the story itself + genre stylization + an on-screen joke + {character} with a role + one clear
punchline at the end.
Topic: {topic}. Duration: {duration} s.
Write the script, on-screen text and subtitles in {language}.
```

## Why

A model reproduces the most successful past example if you show it one. An explicit list of "what has already been
done" and "what was called slop" breaks that inertia better than a generic "be original". The lists of used worlds
and topics grow after every batch: feedback becomes a rule instead of a verbal remark.

## Pitfalls

- A copy of a successful video on the same skeleton with a new topic was rated "slop". Viewers recognize the layout
  before the content.
- A video built on a template of top formulas from other people's hits was called "neuro-slop" by the author:
  formulas, forced comparisons, a faceless character.
- Without updating the lists of used worlds, the second batch converges again to two or three layouts.
