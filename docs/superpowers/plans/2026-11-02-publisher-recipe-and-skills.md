# Publisher recipe and agent skills implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a recipe for building a personal publisher and three reusable, repo-scoped agent skills.

**Architecture:** Skills route to existing recipes/tools. The publisher addition is an implementation recipe and
bilingual build brief, not an upload client. Existing human-publication rules remain in force.

**Tech Stack:** Markdown, Agent Skills frontmatter, existing Python index/PDF tooling. No new runtime dependencies.

## Global constraints

- English first; separate Russian onboarding and publisher explanation.
- Keep the production workshop and publisher read-only; export no sessions, credentials, profiles or private code.
- A new publisher blueprint is `hypothesis`, not a tested public uploader. No live publication in this task.
- Preserve partial-QA reporting, script approval and the person's control of publication.
- Keep existing releases intact; update only the private v0.2.0 draft after exact-commit CI.

### Task 1: Publisher build recipe

- [x] Write the recipe and bilingual build brief: queue/account/file identity, uncertain outcomes, adapter contract,
  manual login, offline acceptance checks and a copyable task for the agent.
- [x] Add navigation from chapter 08 and the publishing index; regenerate recipe indexes and current counts.

### Task 2: Agent skills

- [x] Record baseline responses to explicit skill requests before adding skills.
- [x] Add `nab-video`, `nab-video-qa`, `nab-publisher-builder` and bilingual setup/invocation instructions.
- [x] Validate frontmatter/references and run independent behavioral scenarios with the skills present.

### Task 3: Review and private release preparation

- [x] Run metadata/privacy checks and independent content review; fix demonstrated issues.
- [x] Build/review affected PDF pages in both languages; inspect README at desktop/mobile sizes.
After committing, push and verify exact-commit CI, then update About and draft PDFs/checksums/notes and re-read remote state.
Record those external results in the draft release notes, avoiding a second source commit merely to update CI status.
Report what is supplied and the untested real-account boundary. Do not open repository visibility or publish.

Local results: 48 recipe/index/PDF tests passed; three skill validators passed; independent baseline/forward
read-only scenarios and source/rendered-artifact reviews completed. Baseline already respected partial QA and
uncertain-submit recovery; the new skills add explicit entry points, not a demonstrated safety improvement.
The final RU publisher block was shortened after visual review to fit one column.
