# Pitfalls

Every line here cost someone a video or an evening. Only things confirmed by a measurement or a publication.
Fixes live in the recipes. Found your own? Add a line via PR with a number, see [CONTRIBUTING](../CONTRIBUTING.md).

Language-specific TTS and ASR pitfalls live in [lang/](lang/README.md): Russian is filled in, other languages are
waiting for you.

Line format: **what breaks**, the number, the workaround.

## ASR and text checks

- **ASR substitutes a familiar word.** A domain term was transcribed as a common word in all 12 takes while the audio
  was correct. Re-check with a larger model and a topic vocabulary prompt, never with the line's own text.
- **A 0.90 similarity threshold misses real defects.** Actual errors came at 0.975 and 0.988, and one dropped short
  word in a long line still scores about 0.91. Look for missing words, not a percentage.

- **Final WhisperX pass drops a whole 30 s window.** One phrase came out instead of four lines, reproducibly on the
  same file. Re-transcribe such segments in a second pass and log which windows were redone.

## Frame and QA

- **Green QA does not mean a filled frame.** 22% of a long video (6 of 27 min) was empty background with all checks
  green. Measure fill on the final mp4.
- **DOM "ink" measurement lies.** A 1300×90 block counted as filled on an empty frame; DOM said 20.5%, the mp4 grid
  said 25%. Count a 16×8 grid on pixels.
- **A slow camera push hides dead time.** The still lint found 3 static scenes with the push on and 41 with it off.
- **Karaoke cache keyed on audio hash.** After a text edit 8 lines kept old words on screen and the video shipped with
  the defect. Key = take hash + text.

## Vertical

- **Cropping a 16:9 long video to 9:16.** Text shrinks to 0.56–0.67× and becomes unreadable. Re-layout, don't crop.

## Rendering carousels

- **`pdftoppm -r 72` on WeasyPrint output.** PNGs come out 810×1013 instead of 1080×1350 because WeasyPrint maps 1 px
  to 0.75 pt. Use `-r 96`.

## Publishing

- **YouTube drops the "not made for kids" flag.** It happened to all 5 videos of one series and comments got disabled.
  Check after every upload.
- **Re-uploading the same reel.** The second version got 3 views on YouTube and 0 on TikTok.
- **Hard-coded music.** One track played in 7 videos in a row. Pick from a library and forbid repeats.
- **YouTube daily upload cap on a small channel.** The 11th upload of the day was refused with "try again in 24 hours,
  pass verification" and no draft was created. That is the technical ceiling, not a plan: see the next line.
- **On one small channel, uploads after the 3rd of the day got almost no views (cause unknown).** YouTube slots 1–3
  (Pacific day): median ~970 views, n=17; slot 4 and later: median 9, n=15. TikTok: the first 6 of 22 uploads got
  229–754, the rest 0–60, and the ten uploads of the next day got 1–75. Public view counts over two weeks, not
  impressions; a per-account slot limit or throttling is a hypothesis. Precaution: ≤3 a day to YouTube, ≤5 to TikTok,
  strongest first.

- **Login in one browser, publishing in another.** Logging in through the automation library's bundled Chromium saved
  cookies the real Chrome (which the publisher drives) can't decrypt; preflight showed the login page right after a
  "session saved". Log in with the same browser channel that publishes.
- **A killed browser leaves its profile locked.** `SingletonLock` points at a dead PID and every run reports "profile
  busy". Remove it only after `ps -p <pid>` shows the process is gone.
- **Burst of identical links in DMs.** About 15 DM threads with the same link in 11 minutes, sent by hand from a
  browser profile that automation also drives, preceded an Instagram suspension the next morning. One case, cause not
  confirmed. Reply via the official API, with a per-hour cap and varied text.

## Agent tooling

- **`claude -p` and `codex exec` inside `while read` eat stdin.** The loop handles 1 line of 5 and exits. Add
  `</dev/null`.
- **The agent "fixes" tests to make them pass.** A deny rule `Edit(./tests/**)` holds even under
  `--dangerously-skip-permissions`; `Write(...)` rules do not apply to paths.
- **Sub-agents with web search hit the request limit.** Split research into sequential passes.
