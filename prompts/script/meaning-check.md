# Meaning check: draft and final video

- **Purpose:** the agent checks whether the video has one idea and an event worth watching. Two passes: over the
  draft before render and over frames of the final mp4.
- **Where tested:** Claude Code (can read png frames), Codex CLI.
- **Status:** proven on 5 batch videos as a mandatory step. Some of the draft questions remain a hypothesis: they
  come from research into a screenwriting method.

## Prompt

```text
Create qa/meaning.md for a video on the topic "{topic}" ({duration} s, hero {character}).
The video is in {language}; quote lines and on-screen text in {language}, write your assessment in English.

Pass 1, over the script (before render):
- The one idea of the video in one sentence.
- First frame without sound: would a stranger understand what to look at?
- First line without the picture: is there a concrete event or stake, not a status update?
- By second five, has the viewer received new information, or are we still repeating the hook?
- If you swap two neighbouring shots, is causality lost? If not, there is no plot.
- Does the ending answer the question from the hook and show the source?
- Could a viewer mistake a staged scene, mockup or generation for a recording of a real event?
- Is there a twist or absurdity? Are there formulaic narrator phrases? Would a non-IT person understand it?

Pass 2, over the final mp4:
- Grab 6–8 frames with ffmpeg (one from each scene plus the first frame) and open them as images.
- Answer honestly for each: is it a slide; is the on-screen text readable on a phone; is the main subject covered
  by subtitles or the platform's interface.
Fix what you found and rebuild. In the report: what you found, what you fixed, what remains doubtful.
```

## Why

Technical QA checks frames, speech, loudness and format, but does not tell you whether there is anything to watch.
The questions are phrased so the answer is "yes" or "no" with an example, without judgements like "fairly
interesting". The second pass over real frames catches what is not in the script: overlaps, small text, slide-like
layout.

## Pitfalls

- Green QA does not mean "done". A video that passed every automated check was called "static" and "a
  presentation" by the author.
- The agent tends to praise its own video. "Assess honestly" plus a requirement to name at least one problem works
  better than "check it".
- Frames grabbed at a fixed interval miss short scenes. Grab the middle of each scene by timecode.
