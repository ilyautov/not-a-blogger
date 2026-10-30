# Definition of a "non-template long video" for an agent

- **Purpose:** a brief block that explains to the agent how a long video (a horizontal video several minutes long)
  differs from a slicing of theses into slides.
- **Where tested:** Claude Code, briefs for horizontal long videos.
- **Status:** hypothesis. The block was written after two rejected long videos; long videos built with it have not
  yet been rated by the author.

## Prompt

```text
## What "non-template" means
- There is a PLOT with an arc (setup → twist → resolution), not a slicing of theses. {character} is a hero with a
  goal and reactions, not a narrator.
- Every chapter is its own visual world within the video's overall style. Not a single "card with a title", not a
  single slide.
- A gag or a physical event in frame at least every 3–5 s. Not a single second of empty background.
- Do not copy the layout of existing scenes; borrow techniques. Do not repeat formulaic narrator phrases.
- Subtitles short (2–5 words per screen), large, never covering the main subject.
- Mark staged material (invented scenes, dialogue) explicitly as illustration in the fact-check.

Topic: {topic}. Duration: {duration}.
Write the script, voice lines and on-screen text in {language}.

## Handoff
output/final.mp4, qa/factcheck.md, qa/meaning.md, README.md, SCRIPT.md (script by chapter with timecodes).
In the reply: path, duration, the plot in 5 lines, chapters, what was checked, what is doubtful.
```

## Why

The agent reads the word "interesting" as "more cards and animations". Here, instead of a judgement, there are
verifiable conditions: an event every 3–5 seconds, zero empty background, zero slides. "The plot in 5 lines" in the
handoff shows at once whether there is an arc, without watching 10 minutes of video.

## Pitfalls

- A long course recap made of cards, lists and screenshots with a slow zoom was called static by the author. A 6 %
  zoom does not count as motion.
- A long video with a title, a diagram and a footer in every frame looked like a presentation, even with animation.
  Layout gives a slide away, not lack of motion.
- Green QA does not catch empty background: one long video spent 22 % of its runtime empty while passing all checks.
  Measure frame fill on the final mp4.
- Before a long video, build a 20-second probe and get an "ok". A whole long video on an untested frame grammar goes
  to the bin entirely.
