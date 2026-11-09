# AI jury: up to three edits before the person sees the video

- **Purpose:** after technical QA and before the video goes to the person, a fresh agent looks at the contact
  sheet and a few frames and returns at most three edits that change the impression most. It is an edit
  generator, not a gate: it never decides whether the video is shown and its score never goes into the QA
  report as approval.
- **Model or agent:** a multimodal agent that did not build the video (a background agent without the
  session history). The author may run it only if it answers strictly from frames, not from memory of the plan.
- **Where tested:** written for the author's pipeline after two neighbouring kits; not yet counted on
  finished videos.
- **Status:** hypothesis.

## Prompt

```text
You are a jury for a short video on "{topic}" ({duration} s). You did not make it. You see only:
- the contact sheet {contact_sheet} (frames with time stamps),
- up to three full-size frames: {frames},
- the brief with its "never do" list and its "reference and 4 of 6" field: {brief}.
Do not render anything and do not measure anything new. On-screen text is in {language}; quote it as is,
write your answers in English.

Answer seven questions, each with a timestamp and one sentence:
1. Hook. In the first 2 s, is the subject already acting and is the topic clear without sound? If not, what to show.
2. Hero moment. Where is it (timestamp) and does it hit harder than everything around it? If there is none, say the video is flat.
3. Template. Is there a frame that would fit any video: stock, an AI default look, a "title + bullets" slide, a faceless
   character? Which. Include any violation of the brief's "never do" list.
4. Weakest 5 seconds. Where and why: it stands still, repeats, is unclear, drags, or shows two beats at once.
5. Sound on picture. For the three main cuts or hits: does each have its own sound or a stop?
6. Words. Which line or caption sounds generated (bureaucratic, "powerful", a moral after the punchline)?
7. Copy. How does the video differ from its reference and from the previous episode: how many of the six parameters
   (structure, opening, signature frame, camera path, music shape, ending) actually differ on the sheet?

Then give at most three edits, the biggest first. Each: timestamp -> what changes -> how, in numbers (frames,
seconds, px, easing, which object). At least one edit must raise the "wow", not only fix something.
Finish with one score for the whole video on this honest scale: 5 student work, 6 template, 7 solid professional,
8 strong agency, 9 festival shortlist. First builds are usually 5-7; do not inflate.
```

## Why

- Timestamps on every answer turn opinions into places to look; an answer without a timestamp is not usable.
- "At most three edits, biggest first" keeps the round to one pass; a long list gets half-done and re-judged.
- "One edit must raise the wow" stops the jury from only polishing: a video with no defects can still be flat.
- The fixed scale with "first builds are 5-7" counters the default of models to praise.

## Pitfalls

- Running a second jury round on the same video produces new edits forever. After the person has seen it,
  only the person's feedback drives changes.
- Writing the score into the QA report as "accepted" turns an edit generator into a gate. It is not one.
- Edits that touch elements the person already approved (voice, character, palette) are shown to the person
  as suggestions, not applied.

Sources: questions with timestamps and "no more than three edits" retold from sarpstar/cinecode (MIT),
`references/jury.md`; the scale and "one edit must raise the wow" from Vincentwei1021/mg-styles-15 (MIT),
`rubric.md`. Wording is our own.
