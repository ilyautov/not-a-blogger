---
id: hooks-result-in-first-second
title: Start with a result, scandal, or intrigue at 0.0 s
section: hooks
lang: any
status: proven
evidence: measurement
tools: [ffmpeg, faster-whisper]
learn: ../../learn/en/01-idea-hook-script.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
The draft opens with an intro or explanation: "soon…", "people on TikTok advise…", "I asked the AI to…". That is a lecture; viewers swipe before the point.

## Do
1. First sentence at 0.0 s, no intro. Pick one type:
   - result spoiler: "Passed an AI recruiter thanks to one invisible line";
   - scandal or secret: "While you sleep, we discuss you";
   - intrigue with an object: "Nothing is open. Yet the laptop is screaming. Who's in there?"
2. Give context ("how it happened") at 3–5 s, not earlier.
3. Rewrite an opening conditional clause ("if you…", "when the agent…") into a statement.
4. Design the first second on three tracks: the frame shows an oddity or action, the voice adds conflict, a short caption makes it clear without sound. Don't make all three repeat one phrase.
5. Fit the hook to the real result; never bend the numbers.

```text
Before: Soon a robot will interview you.
After:  The mascot beat an AI recruiter with one invisible line.
```

## Verify
- First frame muted: would a stranger know what to look at?
- First sentence without picture: does it contain an event or stakes, not a status line? Hide everything except the first line: it tells how the video ends or why to keep watching.
- Transcript: first word starts at 0.0–0.1 s.

```bash
ffmpeg -i final.mp4 -vn -ar 16000 -ac 1 a.wav
python -c "from faster_whisper import WhisperModel as M; s,_=M('small').transcribe('a.wav',word_timestamps=True); w=next(s).words[0]; print(w.word, w.start)"
```

## Don't
- Don't promise more than the video shows: the ending must answer the question of the first frame.
- Don't write a loud hook without a real result: it reads as a lie and costs trust. Result first, hook second.

## Evidence
- Seven hits (178k – 3M views): in every video with speech the first word lands at 0.0 s; none has an intro.
- The week's reference hits (up to 710k views) open with a disaster ("I deleted the database…") or a result.
- Two lead-in openings in a row were rejected by the approver ("weak opening"). No own retention A/B.

## Related
- [Voice by 0.45 s](hooks-voice-by-045.md)
- [Open loop](hooks-open-loop-payoff.md)
- [Smash cut into the hook](../transitions/transitions-smash-cut.md)
- [Reel under 40 s: punchline first](../idea/idea-one-example-short-reel.md)
- [Ending: question and codeword](../cta/cta-codeword-in-comments.md)
- Example: [The TV showed an ad. The agent turned it off](../../examples/tv-no-ads/README.md)
- Example: [The agent said the tests passed](../../examples/agent-cheats-long/README.md)
- Example: [AI text gives itself away, but not by the old clichés](../../examples/ai-text-tells/README.md)
