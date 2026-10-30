# Vertical relayout and frame review before render

- **Purpose:** the agent makes a vertical short from a horizontal long video by relaying out the scenes, not by
  cropping, and checks the frames by eye on a contact sheet before render.
- **Where tested:** Claude Code; long videos and vertical shorts cut from them, published on three platforms.
- **Status:** proven on 2 long videos and 8 vertical shorts from them. A dry review of frames before render on one
  long video caught overlapping scenes, overflowing banners, a cropped sticker and two invented numbers.

## Prompt

```text
Make a vertical short 1080×1920, {duration} s, from a fragment of the long video "{topic}" ({timecodes}).
On-screen text and subtitles stay in {language}.

Relayout, not crop:
- The content of the horizontal frame spans ~1620 px of 1920 in width. A 9:16 crop gives 0.56–0.67× scale and
  unreadable text. Rebuild each scene for vertical: elements stacked, font size no smaller than in the long video.
- Recompute positions and camera for a 1080 width from the frame centre, not by shifting the original coordinates.
- Put the chapter number and title on the cut between scenes, not on top of the content.
- Keep the bottom ~15 % and the platform's right-hand button column free of important text.

Review before render:
1. Check the scene sources for errors (scene lint, if available).
2. Grab a frame from the middle of each scene by timecode, build a contact sheet.
3. Go through the sheet by eye and list for each scene: overlap with neighbouring scenes, text spilling out of a
   banner, a cropped element, a number without a source in the fact-check, text too small for a phone.
4. Fix and repeat steps 2–3. Launch the final render only after a clean sheet.
In the reply: the contact sheet, the list of what was found and fixed.
```

## Why

A crop keeps a layout made for a wide screen, and on a phone the text becomes one and a half to two times smaller.
Relayout costs more, but the short is readable. A frame from the middle of each scene by timecode is tens of times
cheaper than a render and catches layout errors that automated QA misses.

## Pitfalls

- The first shorts from a long video were made by cropping: 0.56–0.67× scale, text unreadable on a phone.
- Frames at a fixed interval miss short scenes. You need the middle of each scene, not "a frame every 5 seconds".
- Automated QA missed every error that the dry review found. The sheet is reviewed by an agent or a human, not a
  script.
- Invented numbers appeared in the layout, not in the script. Check on-screen text against the fact-check, not just
  the voice lines.
