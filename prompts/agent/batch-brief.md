# Batch brief skeleton

- **Purpose:** a single brief from which an agent builds a batch of several short videos: topics, rules, mandatory QA
  files and handoff format.
- **Where tested:** Claude Code, batches of 5 short videos.
- **Status:** proven on a batch of 5 videos: the author accepted 3, 1 was published. Before this skeleton, copies of
  one successful video were rated "slop".

## Prompt

```text
# Batch of {N} short videos, {duration} s each, vertical 9:16
Language of voice, captions and on-screen text: {language}.

## Topics
{list of topics: one line per video, with the source of the news or material}
Do not take topics from past batches: {list}.

## Anti-slop
{paste the block from prompts/script/antislop-brief.md}

## Order for each video
1. Script per prompts/script/scenario-from-material.md and the "what the viewer now knows" table.
2. Show me the script, the first frame and one storyboard BEFORE the build. Do not start building without an "ok".
3. Its own scene in a separate file. Do not copy the layout of neighbouring videos.
4. Voice per the rules in prompts/voice/ and gotchas/README.md. ASR on every take before the build.
5. qa/factcheck.md and qa/meaning.md are mandatory (prompts/script/).

## Constraints
- Synthesis and render strictly sequential, one video at a time: running in parallel eats memory.
- Do not call paid APIs without my "yes".
- Publish and upload nothing. Ready for review is not approval.
- Commit nothing unless asked.

## Handoff for each video
output/final.mp4, qa/factcheck.md, qa/meaning.md, SCRIPT.md (lines with timecodes), README.md.
In the reply: path, duration, the video's idea in one line, what was checked, what is doubtful.
```

## Why

Without a handoff format, the agent reports "done" on green tests. Mandatory `factcheck.md` and `meaning.md` turn
the checks into artefacts you can open. The "script before build" gate is the cheapest one: editing text costs
minutes, rebuilding a video costs an hour.

## Pitfalls

- Without a separate scene file per video, the agent replicates one layout across the whole batch.
- Topics in the brief without a source get padded by the agent with invented details. Attach a link to the material
  for every topic.
- A copy of a successful video on the same skeleton was rated "slop". A successful video is a sample of a technique,
  not a layout template.
- The "script before build" rule appeared after a video that was built in full and called "slop" on first viewing.
  The whole build went to the bin.
