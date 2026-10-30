[Русская версия](findings.md)

# 20 findings from our research

Generalized conclusions without creator names and without tables of other people's videos. Every point can be challenged:
bring your own snapshot with a method via the «Приём» [Technique] issue, labeled "research".

How to read this: the numbers come from public view, like and comment counters in our snapshots. They are observations,
not causes: we did not measure subscriber growth, retention or impressions, and there were no control groups. Where the
way creators or videos were selected is not described (for example "936 channels"), treat the sample as unspecified and
the point as an observation within it.

1. **A hit = a multiple of the creator's median, not absolute views.** Working thresholds from our snapshots: ≥5 medians and ≥100K for mature videos, ≥3 medians and ≥50K for young ones; when views are hidden, use the multiple on likes. Compare a video only with videos by the same creator.
2. **Comments, not likes, set hits apart in our snapshots.** Hits get ×1.4 comments per view at equal likes. Videos with a code word had 1.96% comments per view against 0.26% without one: a correlation, not proof that the word "lifts" comments.
3. **An object with an event.** Across 100+ technical reels, what works is a video where something happens to a specific object; facts become stages of the event, and removing a stage breaks the chain.
4. **The first word at 0.0 s.** None of the eight hits we broke down has an intro; loudness −14…−15 LUFS, no silence longer than 0.25 s, a compressed bed with no dips (LRA 2–3 LU).
5. **Tool tutorials got few views in our snapshots.** On the Russian internet 43–4,000 views; in the West not a single AI tutorial at ≥5× the creator's median across 936 channels (how the channels were selected is not described here). The hits in the same snapshots were about a situation, fear, comedy, a result.
6. **A topic wider than the niche.** The biggest hits of niche AI creators in our snapshots were often not about AI: a timeless story, everyday absurdity, a confession. The same creators' niche videos sat near their median.
7. **Shorts and long-forms on growing expert channels.** The Shorts median for expert creators with growing channels is 1.4–2.4K views; the same creators publish 8–30-minute long-forms every 4–7 days and have their own open artifact. We did not measure subscriber growth from Shorts or from long-forms, so "what grows a channel" does not follow from this; the selection of creators is not described.
8. **Own open artifact among fast-growing creators.** The fastest growth in the snapshot belonged to those who released their own repository/skill and make videos about it; causation was not tested. Their lead magnet is one specific feature of a free tool, not "a lesson".
9. **A format's life cycle in the observed cases: one week.** A formula got ×200+ in the first 3 days, then copies arrived and the multiple dropped 10–40×; a specific storyline was taken after the second copycat; sequels of a hit on the same storyline did not repeat its success.
10. **First "what to shoot" from data, then "how".** Select formats from niche hits (parsing profile grids, the multiple, ease of repeating) and go for volume. We don't quote other people's odds of a video taking off: their source isn't recorded.
11. **Faceless: three models among the snapshot's hits:** a mascot character with personality, a mechanism in motion, a live expert voice. 62 of 106 Russian hits are faceless; nobody in the snapshot used a synthetic voice as the carrier of expertise.
12. **The "human and AI agent" skit: 60-second dramaturgy**: pain → deadpan reply → escalation in 3–4 steps → a useful nugget → punchline → in-character CTA; cuts every 2–3 s, a wide shot only at the turn.
13. **A business function as a topic vs a frame.** CRM, sales, contracts: zero hits in the month of the snapshot; the hits used frames such as "an AI employee with a price/arithmetic", "fear of being exposed", "a prompt for a niche → result".
14. **Generative video: an insert, not a foundation.** 2–3 s between anchor stills, "bad picture" genres; character consistency is held by process (character passport, references, anchor frames, take selection); ~$4–8 per 30-s short in the cloud, locally 40–70 s of compute per second of video.
15. **What platforms actually say about retention.** Their documents confirm view share, "watch/swipe away", retention graphs and testing on non-subscribers; they don't confirm "3 seconds", cuts every N seconds, the weight of shares, or penalties for synthetic voices.
16. **AI labels and platform rules as of late 2026.** Auto-labels on Shorts, mandatory labeling of realistic "a real person did something that never happened", sanctions for templated mass production, likeness detection; don't realistically generate real people, and don't name private individuals from the news.
17. **An agent QC stack without the cloud.** Structural preflight → render → scoring; blackdetect/freezedetect, a scene detector checked against cut points, ebur128, OCR, two ASRs as a defect detector, a contact sheet ≤2576×1456 for a single VLM call, a VLM judge only against a checklist; plus an "empty frame" metric on the finished mp4.
18. **Why AI motion looks angular and how to lint it.** One ease, one axis, identical durations, no camera and no depth; thresholds: ≥3 ease characters, stagger 0.05–0.1 s and ≤0.5 s per group, hero 0.8–1.2 s, a spring with dampingFraction 0.8–0.85; no ready-made motion lint exists: a gap.
19. **A short-video script as a chain of the viewer's knowledge.** Event → apparent explanation → new evidence → shift in understanding → verifiable outcome; the first second has three tracks (frame, voice, caption) about one conflict; the voice carries the thought, the screen shows the evidence; if the scenes can be reordered, it's a list.
20. **Collecting public metrics without logging in, and its limits.** Public pages and embeds, calibrating different counters (play ≈ 2× view), the date from the video ID, repeated snapshots of one panel of creators; what you can't see without logging in (search, sounds, comments, new creators) and the ethics: read-only, no other people's sessions, no publishing other people's data by name.
