# Granular agent skills

**Goal:** Make individual video/publisher tasks directly selectable without invoking the whole workflow.

**Design:** Keep the three existing names as coordinators. Add fifteen focused skills: script, shot plan,
assets, motion, voice, sound, captions, render, file QA, picture QA, speech QA, publication preparation,
publisher queue, publisher adapter and publisher recovery. Each identifies its input, output and boundary,
then loads only the relevant existing recipes/tools. No new runtime code or recipe claims.

## Constraints

- English skill instructions; separate English/Russian directory and setup guides.
- Preserve approved text/assets, existing authorization and unrelated stages of a narrow request.
- Existing publication policy remains in force. Publisher skills build/specify components, not operate accounts.
- Keep 143 recipes (73 measured, 70 hypotheses). Do not modify PDF inputs or published releases.
- No global installation, account actions, new media generation or rendering as part of this packaging task.

## Checks

1. Record the missing dedicated entry points before edits; do not call that a demonstrated safety failure.
2. Validate every frontmatter, relative reference, and copy into a local Claude project layout.
3. Independently check description-based selection and narrow-scope handoffs.
4. Review the complete diff, update current navigation/counts and commit/push after local checks.
5. Verify exact-commit CI and refresh the private draft target/notes. Retain the reviewed PDFs built from 4bc57e9
   if source inputs remain unchanged; verify their digests. Record external results in release notes rather than
   adding another source commit merely to record CI status.

Native client-menu discovery, artistic quality and live publication are not established by these checks.

Local results: 18 skills pass frontmatter validation, 254 canonical references resolve, and the documented
Claude setup copies all 18 with 96 resolving body references while preserving existing copies. Independent
description-based selection matched all 18 requests; an SRT/VTT fixture export passed without MP4 generation.
Speech-only partial QA, queue-only planning and uncertain-submit incident handoffs remained scoped. Independent
review approved after fixing one relocated directory link. English/Russian catalog previews fit 390/1440px.
