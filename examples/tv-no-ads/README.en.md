[Русская версия](README.md)

# "The TV showed an ad. Claude turned it off"

![Frame from the video](poster.jpg)

YouTube Shorts: https://youtube.com/shorts/Ma8Wsotaj2Q (version 2, released 21.10.2026).
The first version, with a different voice synthesizer: https://youtube.com/shorts/vpOuoB43J3Q.

## Format and length

Vertical reel, 1080×1920, 54.7 s (version 2; the first was 47 s). No face: everything is drawn
in code on canvas, synthesized voice. Genre: retelling someone else's open-source project as an
everyday story ("a guy removed the ads from his parents' TV").

## Hook (first line)

«Короче. Чувак включил родителям Нетфликс, а телевизор сначала показал ему рекламу.
На своём же телевизоре.» [Long story short. A guy put on Netflix for his parents, and the TV
showed him an ad first. On his own TV.]

From second zero the frame shows a TV with an ad banner and a "skip" timer over Netflix.

## Second-by-second structure

| Time | What you hear | On screen |
|---|---|---|
| 0.3–6.8 | Hook: an ad on your own TV | TV with a banner, the "skip" timer starts over |
| 7.2–11.4 | «Он не полез в прошивку. Просто написал Клоду, какой у него телевизор» [He didn't mess with the firmware. He just told Claude what TV he has] | A chat window with the TV model |
| 11.9–16.5 | The agent found the TV on the home Wi-Fi and pulled the list of apps | Terminal, a scrolling list of packages |
| 17.0–22.6 | 25 manufacturer apps: ads, tracking, recommendations | Packages light up with labels, counter "25" |
| 23.2–27.7 | Everything disabled, nothing deleted, rollback with one command | Toggles switch off, big "deleted: 0" |
| 28.2–34.5 | The agent wrote its own home screen: black, four apps | Launcher code typing out, then a clean screen |
| 35.2–43.2 | The project is free, 147 TVs from 49 brands, «ваш телик тоже» [your TV too] | A wall of brands, a "Your TV" badge with a checkmark |
| 43.7–49.8 | What to do: enable debugging, hand over the prompt, 15 minutes | Checklist and a 15-minute timer |
| 50.5–52.0 | «Не за что. Удачи.» [You're welcome. Good luck.] | Clean TV screen, channel emblem |

## Techniques used

- [Start with a result, scandal or intrigue at 0.0 s](../../recipes/hooks/hooks-result-in-first-second.md): the first line opens with «Короче» [long story short] and names an everyday pain right away,
  no intro.
- A turn inside the hook: «на своём же телевизоре» [on his own TV] sounds like a grievance, not tech (no recipe yet).
- [Cut hard, save flashy transitions for 2–3 spots](../../recipes/transitions/transitions-hard-cut-default.md): one large object in frame per line, hard cuts, in the first
  version (47 s) the shot changes 17 times, every 1.5–4 s.
- Numbers as heroes of the frame: "25", "deleted: 0", "147", a "15 minutes" timer (no recipe yet).
- [Build a handheld camera from a sum of sines on a separate layer](../../recipes/camera/camera-handheld-sines.md): handheld camera over every shot, not a single still stretch longer than
  0.5 s (measured by the difference between neighboring frames).
- [Put noise whooshes on cuts, even if people hear them as "sniffling"](../../recipes/sound/sound-keep-noise-whooshes.md): noise "whooshes" on the cuts. Viewers heard them as someone sniffling, and that
  became a topic in the comments.
- Subtitles at the top: a small line plus a big word, emphasis in italics, numbers in color (no recipe yet).
- [Review the middle of every scene before rendering](../../recipes/qa/qa-dry-frame-review.md): a "clear without sound" check before rendering, a dry review of 64 frames.
- [Do a second-by-second remake of a hit in your own words](../../recipes/idea/idea-remake-rhythm-not-words.md): the rhythm was taken from someone else's hit in the niche, the wording rewritten in our own words.
  How to find such models: [Take ideas from niche hits selected by the creator's median](../../recipes/idea/idea-find-hits-by-median.md).

## Metrics (platform, number, measurement date)

| Platform | Number | Measurement date |
|---|---|---|
| Instagram Reels | 5,611 views, 162 likes, 9 comments about 2 hours after release | 21.10.2026 |
| Instagram Reels | 212K views, 7,515 likes | 21.10.2026, 23:48 MSK |
| Instagram Reels | 792K views | 24.10.2026 |
| YouTube Shorts | 1,500 views | 24.10.2026 |
| Instagram Reels | 21,496 likes, 257 comments (views aren't visible without logging in) | 22.10.2026 |
| YouTube Shorts and TikTok | from 1 to 328 views across different uploads | 21.10.2026 |

For comparison: the account's neighboring reels got 58–400 views on the same days. Followers
went from 61 to 70 in the first two hours. One of the two versions was uploaded to Instagram;
which one wasn't recorded.

## What worked

- The topic makes sense to someone outside IT: an ad on your TV, an AI removed it, for free.
- A grievance in the hook ("on his own") and a result you can repeat at home in 15 minutes.
- "Deleted: 0" removes the main fear ("won't I break my TV?").
- The video generated comments on its own: «а без Клода как?» [how about without Claude?], «не
  превратит ли в кирпич» [won't it brick it?], «кто там шмыгает» [who's sniffling there?]. Each
  such question later became the topic of a reply video.

## What didn't work

- The channel's author rated the first version's voiceover as «ужасную» [awful]: the synthesizer
  can't handle short, fast text. The second version was re-synthesized with a different model.
- On YouTube and TikTok the uploads of both versions got 1 to 328 views (21.10.2026),
  version 2 on YouTube got 1,500 (24.10.2026).
- The first draft repeated four phrases from the model video the rhythm was taken from. They were
  rewritten in our own words.
- The terminal at 9–19 s is too dense, and package names are clipped on the left. It's texture,
  no one needs to read them, but it looks sloppy.

## How to repeat it

1. Find an open-source project that solves an everyday pain (ads, tracking, unwanted
   subscriptions) and check its license.
2. First line: who, what happened, why it's annoying. No "today I'll tell you".
3. Show the path in 5–7 steps, each step as one object in frame and one number.
4. Remove the fear: "nothing gets deleted", "rollback with one command".
5. Ending: what the viewer should do and how long it takes.
6. Upload to all platforms and record which version went where.
