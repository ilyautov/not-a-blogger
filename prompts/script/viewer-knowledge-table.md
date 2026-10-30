# "What the viewer now knows" table

- **Purpose:** a script form filled before the build. Each row records what new knowledge the viewer got, how it is
  shown and which question leads on.
- **Where tested:** Claude Code (filling), a human (review).
- **Status:** hypothesis. The form is used in short-video briefs; its effect on retention was not measured
  separately.

## Prompt

```text
Fill in the script table for a video on the topic "{topic}", {duration} s, hero {character}.
Write the Speech and On-screen text columns in {language}.

| Time | What the viewer now knows | Shot/action | Speech | On-screen text | Source/evidence | Question that leads on |
|---|---|---|---|---|---|---|
| 0–? | What oddity they see | Concrete first shot | One short line | A separate short line | Real material | Why did this happen? |
| ?–? | Why it matters | Consequence or stake | Only the needed context | A number or name, if it helps | Link, file, recording | What will we check? |
| ?–? | What changed the version | Check or action | Causal link | Highlighting the evidence | Primary screen | What did it lead to? |
| end | Answer to the first question | Visible result or limit | Verdict without a lecture | Only the result | Confirmation | Loop closed |

Rules:
- The "What the viewer now knows" column is new in every row. A restatement of the previous row = delete the row.
- Speech and on-screen text do not duplicate each other.
- The "Source" column holds only things that exist. Mark staging with the word "illustration".
- As many rows as the material needs, no more.
After the table, one line: which row can be dropped without losing meaning. If there is one, drop it and rewrite.
```

## Why

The "what the viewer now knows" column forces counting knowledge, not scenes. An empty or repeated cell is visible
at once to a human who reads the table in 30 seconds, and there is no need to argue about taste. The last column
keeps one open loop until the ending.

## Pitfalls

- The agent writes a judgement into "knows" ("the viewer understands this is important") instead of a fact. Require
  a concrete statement that can be checked against the frame.
- Without the "Source" column the table quickly fills with invented numbers. Two such numbers were once found only
  during a dry review of the frames before render.
- The table does not replace watching the final video: it checks the intent, not what ended up in the frame.
