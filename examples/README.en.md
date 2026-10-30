[Русская версия](README.md)

# Examples: breakdowns of published videos

Each folder breaks down one of our published videos: format, hook, second-by-second storyboard,
techniques, metrics with the measurement date, what worked, what didn't, and how to repeat it.
Both hits and flops are here: flops are just as useful to learn from.

The numbers come from our own measurements, and each one has a date. Where nothing was measured,
it says so: "not measured". Each number is true as of the date in brackets and is not updated later;
videos released after the last measurement have none.

| Video | Format | Length | Best metric | Main lesson |
|---|---|---|---|---|
| [The TV showed an ad. Claude turned it off](tv-no-ads/README.en.md) | Vertical, everyday story about an open-source project | 54.7 s | Instagram: 792K views (24.10.2026); YouTube: 1,500 (24.10.2026) | Real-life pain in the first line, and the fear defused on screen ("deleted: 0"). Instagram and YouTube diverged by hundreds of times on the same date; which version went to Instagram isn't recorded |
| [Asked an AI to free up my Friday](free-friday/README.en.md) | Vertical, "asked the AI → absurdity", infographic | 20 s | YouTube: 1,307 (12.10.2026) | The absurdity is shown through action, and the video loops. The channel's best YouTube short on 12.10.2026 |
| [They said the same about DeepSeek](deepseek-headlines/README.en.md) | Vertical, explainer that takes apart a headline | 59 s | YouTube: 1,196 (12.10.2026) | One hero object in frame and camera push-ins. Replace a word with the wrong stress instead of marking it up |
| [AI gives itself away, and not with "it's worth noting"](ai-text-tells/README.en.md) | Vertical, "I can spot AI text" | 28.9 s | YouTube: 989, TikTok: 530 in the first day (14.10.2026) | A guessing game instead of a tutorial. A copy of the winning template a day later turned into slop |
| [3 Claude Code keys (repeat)](three-keys-repeat/README.en.md) | Vertical, "three points", flop | 21.5 s | YouTube: 3, TikTok: 0 (14.10.2026) | Second version uploaded the same day as the first; cause of the flop not established |
| [The whole course in 20 minutes](course-retelling/README.en.md) | Horizontal long-form course retelling, flop | 19:56 | YouTube: retelling long-forms got 32–79 (12.10.2026) | Cards with a slow zoom look like slides. Retelling a free source gives no reason to watch |
| [The agent said the tests passed](agent-cheats-long/README.en.md) | Horizontal long-form on motion-reel grammar | 2:07 | Not measured (all the channel's long-forms 12–625 as of 12.10.2026) | A number as the hook, a background per chapter, our own experiment. Frame occupancy 78% vs 24% |
| [A hook that blocks a dangerous command](hook-vertical-from-long/README.en.md) | Vertical cut from a long-form | 35 s | Not measured | A vertical from a long-form is made by re-laying out the scenes: fitting into the 1080 width shrinks text to 0.56–0.67, a center crop cuts off the edges |
| [I gave my Instagram to Claude](instagram-to-claude-skit/README.en.md) | 3D skit, the hero's live voice | 25 s | Instagram: 398 in 3 hours (21.10.2026) | Live voice for the hero, synthesis for the side characters. A meme shout at the end |
| [Guess which one is my voice](guess-my-voice/README.en.md) | A/B guessing game with a twist | 39.5 s | Not measured | Format chosen from a sample of neighboring hits (median 3.7K for guessing games versus 787 for how-tos). The final twist makes people rewatch |
| [Claude finds a place from a photo. I tested it blind](photo-geo-blind-test/README.en.md) | Blind test of someone else's claim | 41.8 s | Not measured | Test a loud claim yourself and give a two-sided verdict: where it's exaggerated, where the real risk is |
| [Goro cancelled the call](mascot-cancels-call/README.en.md) | Meme loop with the mascot | 14.4 s | Not measured | Absurdity escalating in three steps in 14 seconds, looped |

## What the hits have in common

- The first line is about pain, fear or absurdity from the viewer's life, not about technology.
- One large object in frame per line, and something is always happening inside the frame.
- Numbers are big, treated as the heroes of the frame.
- An ending with an action: a question, a code word or a tip.

## What the flops have in common

- A second version uploaded the same day as the first (link to the flop not established).
- Retelling someone else's free material without a story of our own.
- A static frame with a slow zoom.
- A definition as the hook instead of a result.

## How to submit your own example

1. Copy any folder here as a template and name it in Latin letters, hyphenated, after what the
   video is about: `examples/<slug>/`.
2. Fill in `README.md` with the same sections in the same order: "Format and length", "Hook
   (first line)", "Second-by-second structure", "Techniques used", "Metrics (platform, number,
   measurement date)", "What worked", "What didn't work", "How to repeat it".
3. Only list metrics you actually measured, with platform and date. No measurement: "not
   measured". Don't round up and don't merge platforms into one number.
4. Send flops too. A flop is valuable if "What didn't work" names a concrete lesson.
5. Poster: one frame from the video.

   ```bash
   # vertical
   ffmpeg -ss 2 -i final.mp4 -frames:v 1 -vf scale=360:-2 -q:v 4 poster.jpg
   # horizontal
   ffmpeg -ss 2 -i final.mp4 -frames:v 1 -vf scale=640:-2 -q:v 4 poster.jpg
   ```

   Pick a frame that makes the video clear (the hook or the main object), not a blurry transition.
   If the frame shows a real person's face and there's no consent to publish, don't include a
   poster and say so in the README.
6. Only link to your own videos. Don't name other creators, commenters or personal accounts.
   If the frame contains someone else's photo, music or map, state the license and attribution.
7. Write "Techniques used" in plain words. If there's already a recipe for a technique in
   [`recipes/`](../recipes/), link to it.
8. Open a pull request with one folder per video.
