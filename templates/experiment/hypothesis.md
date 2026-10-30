# Hypothesis

<!-- Replace everything below with your own advice. Fill this file BEFORE the first run and do not edit it after:
     a hypothesis written after seeing the results is a story, not a test. -->

**Advice being tested:** "Add *this is very important for my career* to your prompt and the model answers more accurately."

**Claim in testable form:** with the phrase (condition B) the model gets more of the five questions in `task/` right
than without it (condition A, control). Everything else is identical: same model, same questions, same flags.

**What counts as success for the advice:** B scores higher than A on average over N runs, and the gap is larger than
the run-to-run spread inside A.

**What would falsify it:** equal scores, or a gap smaller than the spread.

**Chosen before running:**
- models: `haiku`, `sonnet` (aliases of the CLI; the exact model id is logged from the CLI output)
- runs per condition and model: 5
- scoring: exact match per question after normalisation (`run.py: score()`), 0–5 per run
- all runs go into `results.md`, including failures and timeouts

**Known limits written in advance:** a tiny question set, default sampling (no seed), one CLI version.
The result says "on these questions, with this CLI, today", nothing wider.
