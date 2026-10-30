# Script fact-check

- **Purpose:** the agent checks every claim and every on-screen number against a source before the video is built.
- **Where tested:** Claude Code, a mandatory step in briefs for short videos and long videos.
- **Status:** proven on 5+ batch videos and on long videos: unconfirmed claims were removed from the script before
  voice synthesis.

## Prompt

```text
Create qa/factcheck.md for a video on the topic "{topic}".
Write the claim column and the script edits in {language}, the language of the video.

For every claim in the script and every number on screen, one table row:
| # | Claim (verbatim from the script) | Source (URL or file) | Source type | Status |

Rules:
- Prefer the primary source: company report, press release, court documents, scientific paper. Media retellings
  are worse.
- The key fact of the video needs at least two independent sources.
- Status: ✅ confirmed, ⚠️ partially confirmed or single source, ❌ not confirmed.
- ❌ remove from the script. ⚠️ rephrase so it claims no more than the source does:
  "according to the company", "the survey was commissioned by the manufacturer", "in one study".
- Mark staged scenes and invented dialogue as separate rows with the status "illustration".
- If a neural network's answer is shown on screen, it must match the saved answer file verbatim. Give the file,
  the model and the run date.
At the end: a list of script edits you made as a result of the check.
```

## Why

An agent writes plausible numbers as easily as real ones. A table with a mandatory source column makes a gap
visible. Phrasings like "according to the company" keep the fact in the video without turning a manufacturer's
claim into truth.

## Pitfalls

- Two invented numbers once made it into the frames and were caught only during a dry review of the scenes before
  render. A script fact-check does not cover what the agent added to the layout: check the on-screen text too.
- The agent marks ✅ for a link it never opened. Ask for a quote from the source next to the link.
- In the video, call the model "a neural network" unless you are sure the public app would give the same answer.
