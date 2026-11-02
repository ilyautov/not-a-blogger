# Publication-ready repository Implementation Plan

> For agentic workers: use subagent-driven-development for Tasks 1 and 2 with a scoped spec/quality review after each, then a whole-branch review. Parent owns Task 3 delivery and verification. Continue without intermediate permission questions.

**Goal:** Finish the public-facing course/repository, remove confirmed starter/QA defects and prepare a concrete launch package, leaving the visibility change for the author.

**Architecture:** Keep the existing Markdown course, agent recipes, two starters and PDF builder. English README is primary; Russian is a separate version. Preserve the established illustrations and add an overview of the approved eight-style atlas. No new website, LMS, account system or video publication.

**Tech stack:** Markdown, existing Python/TypeScript/HTML tools, JPEG/SVG assets, GitHub metadata/CI, existing WeasyPrint PDF build.

## Global constraints

- Start at cd25fb13cf02106ab5ea85a2e3e18b94dd6e6e7f on codex/publication-ready in the isolated not-a-blogger clone. The source workshop is read only.
- User confirmed English first, separate Russian version; audiences include beginners, technical authors and experienced practitioners. Course for humans, exact recipes/checks for agents.
- Use real examples and the approved eight-style selection. No fabricated reach, timings, full TTS support or artistic acceptance. Preserve historical metrics/dates and their boundaries.
- No paid APIs, model downloads, voice cloning, platform uploads, outreach or visibility change. New CI/clean-clone videos use the existing fake/no-ASR path and remain preview_partial.
- Keep MIT/vendor exceptions, CC BY 4.0 text, Commons CC BY-SA photo/adaptation credits and independent author-brand exclusions explicit. Do not invent ownership or an endorsement.
- Workers own named files only, are not alone in the checkout and must not revert parent/other changes. Stage/commit only owned files. Parent owns the ledger, release artifacts and GitHub settings.
- Tests target actual defects and public entry paths. No tests mirroring prose/CSS or arbitrary full test repeats. Visual review: one batched inspection at desktop/mobile, one bounded correction/confirmation.
- GitHub remains private. Prepare source/release material before the final visibility decision. Preserve prior release assets and published video records.

## Task 1: fix confirmed reliability and readability defects

Ownership: starter/locked.py; tools/lint/still_lint.py; starter/scene/scene.ts; starter/examples/subscription/scene.ts; starter/README.md and README.en.md; tools/slides/deck.html and README.md; relevant existing/new tests; generated starter manifest (find with scripts/starter_manifest.py). No root README, course prose, release files or settings.

- [x] Reproduce prior findings before fixes, distinguishing environment failure, wrapper lifetime, sampling parameters and camera-only motion. Record red/green evidence.
- [x] Keep the lock held for the actual worker lifetime, including when the command receives SIGTERM. Prefer replacing the wrapper after flock via `os.set_inheritable(f.fileno(), True); os.execvp(cmd[0], cmd)` or an equally justified lifetime-preserving implementation. Preserve safe lock-file checks and command exit status; test real process contention and signal termination without leaking processes.
- [x] Reject non-finite or non-positive sample step at the public sampling/run boundaries before loops/browser launch. Reject non-finite/negative threshold and max_still as well; CLI should explain invalid input and exit nonzero. Tests cover zero/negative/NaN/Inf and valid ordinary sampling, not just helper implementation.
- [x] Add an explicit optional scene contract `window.setQAMode(enabled: boolean)` in both bundled Canvas scenes. In QA mode disable camera/postprocessing that can masquerade as object movement; normal rendering remains unchanged. still_lint calls the hook before sampling when camera removal is requested, retains #world fallback, and reports the applied camera-control method honestly. Unsupported custom camera removal is disclosed rather than declared successful. --keep-camera and --pre-js remain usable.
- [x] Regression: a Canvas scene whose only movement is camera/effects fails stillness with QA mode, while genuine object movement passes. Keep readable documentation for the command and hook; update bundled source manifest after changes.
- [x] Fix the slide deck's viewport-only font sizes on narrow screens. At 390x844 body text >=16px and controls >=44px, long content scrolls without covering navigation. Desktop and 1280x720 print retain their design and content. Inspect template plus generated list/table/code slide on mobile/desktop and print; no extra CSS-mirroring tests.
- [x] Run relevant tests, recipe/index and manifest checks. Commit only Task 1 files and report tests/screenshots/limitations to parent. Scoped independent review before Task 2.

## Task 2: course entry, visual examples and publication copy

Ownership: README.md, README.ru.md, learn/en/README.md, learn/ru/README.md, starter-lite/README.md and README.ru.md, starter/README.md and README.en.md (compatibility wording only) plus regenerated starter/SOURCE-MANIFEST.json, assets/README.md, an atlas-overview asset if needed; docs/REPO-PUBLICATION.md, .github/REPO-SETTINGS.md, root CHANGELOG.md; SECURITY.md and contributor-entry wording if required for truthful reporting/issue routes; license-summary documentation if necessary. No code/runtime/CI/AGENTS or prior metrics changes.

- [x] Read current entry routes, course index, BRAND/THIRD-PARTY/atlas credits and Task 1 outcomes before editing. Preserve approved identity and existing examples, rewrite hierarchy around learning with a human and agent.
- [x] Primary entry in English, clear Russian switch near the top; both versions equivalent. Lead with concrete output and roles, then direct links for learning, first silent render, agent task, advanced recipes and current PDF. Distinguish no-install reading, Node/ffmpeg silent path and full Python/TTS path.
- [x] Surface the eight-style atlas with an approved existing overview or a technical contact sheet of bundled images, not new synthetic artwork. Preserve source/credit rights for the overview. Keep a readable link to full chapter and the historical/static-study distinctions.
- [x] Remove stale claims that Linux has never been checked: Ubuntu24.04 CI covers two demo paths and PDF/tests; full local voice/model/GPU workflow remains unverified there. Do not imply native Windows support. Avoid fixed beginner-time guarantees or 'all proven' recipe claims.
- [x] Preserve real dated performance examples and existing author voice. Separate general licenses from brand/photo/vendor exceptions near the public entry. Do not alter standard license legal text.
- [x] Add an actual release/publication guide: exact verification and clean-clone commands; what was measured vs unverified; current source/release paths; concrete About/topics/social preview settings; final owner visibility action and checks after opening. Include concise EN/RU launch/release copy for review, no posting.
- [x] Add human-readable version history in root CHANGELOG.md without modifying generated docs/CHANGELOG.md. Ensure settings document is a truthful prepared/applied ledger and does not claim private reporting or social upload are enabled without evidence.
- [x] Check local Markdown/image links, consistency, privacy and repository counts. Commit owned files only; report. Scoped independent content/visual review.

## Task 3: concrete private launch candidate

Parent ownership: metadata/settings, review evidence, clean checkout, artifacts, optional security-fix integration and final launch status. These are external acceptance gates; exact source/PDF/CI results are recorded in the draft release and verification artifacts rather than rewriting the verified source commit.

- Inspect history with gitleaks, tracked media/files and private paths; verify third-party boundaries. Resolve material findings, preserve intentional public author contacts.
- Apply non-visibility About description/homepage/topics and existing feature preferences through available GitHub capabilities. Upload/verify existing social preview via UI only if connector/CLI lacks support; disclose an actual account/tool blocker if present.
- Run the full existing test suite once after changes and exact clean-clone starter-lite + full starter fake/no-ASR commands, locally or in CI. Do not download TTS/ASR weights. Inspect generated frames/report and disclose preview_partial.
- Build both PDFs from final sources with existing builder, check gates and new affected pages visually; marker before PDF authoring as required by PDF skill. Prepare checksums and a draft v0.2.0 launch release with both PDFs and source references. Leave prior releases intact.
- Whole-branch independent code/security/content/render review on the final state; address material findings, then push source and verify GitHub CI. Recheck exact remote commit, metadata and draft asset hashes.
- Deliver a concise ready/not-ready statement with reviewable GitHub links, artifacts and any real remaining owner action. Ask only for final public-visibility decision; do not change visibility without that instruction.

## Evidence ledger

02.11: user requested final formatting/publication preparation, confirmed English first with separate Russian version. Baseline main cd25fb1, clean local checkout; v0.1.1 PDFs exist and match reviewed files; last CI passed both demo paths and checks. GitHub About is empty and topics are absent; repository remains private. Runtime/readability findings were previously reproduced and will be rechecked before changes.

02.11 preparation evidence: About description/homepage and 17 topics applied and re-read through API; visibility stays private. Custom social preview is not installed (GraphQL usesCustomOpenGraphImage=false). User explicitly chose a ready image and manual instructions instead of browser login, so no further browser-auth work is required. Existing assets/social-preview.jpg is 1280×640, 218558 bytes, visually inspected and suitable for the handoff. Private vulnerability reporting GET returns404 while private; GitHub official docs place enabling it on public repositories, so it remains a post-opening owner action with existing email fallback. No issue seeding or announcements were sent.

02.11 Task 1: e60b4fe plus focused 0c1691e follow-up. Spec PASS and code-quality APPROVE, no open findings. 78 selected runtime tests passed; focused slide suite10 passed. Native output hashes match baseline at10 sampled times. A single concurrent browsercapture returned a broken-image placeholder; saved and bounded-diagnosed, causal link to code not established; no thresholds weakened. Mobile body16px/buttons44px, scrollable long content, table/code focus consumes horizontal arrows. Parent inspected mobile/desktop/print contact sheets. SOURCE-MANIFEST fresh. Both scoped reviews are complete before Task 2 starts.

02.11 Task 2: 906a6f8 plus bounded intro correction4908176; both scoped source reviews PASS/APPROVE. 249 local targets checked,15images, counts142=73+69,12examples/12chapters; manifest/index/privacy clean. Parent rendered actual GitHub Markdown API output in a local inspection stylesheet, not an authenticated GitHub-page render. EN/RU at1280px and390px inspected, all local images load and page width matches viewport. Mobile quicklinks moved fromY749 to484EN/509RU and hero fromY887 to622EN/648RU. Four gallery surfaces inspected with image visibly in viewport; no extra visual correction loop. Public-only badges do not resolve in the signed-out private-repo preview and remain a post-opening check.

02.11 clean checkout: runtime0c1691e onmacOSarm64, fresh Python3.11venv plus declared starter dependencies. Lite check/render:15.000s,H264,1080x1920,30fps,450frames,strictdecode and3frames inspected. Full fonts/fake/frames/no-ASR all:11.733333s,expectedpreview_partial,technical_passfalse, file gates pass and ASRnull; contact inspected, no continuousAV/realvoice/TTS/ASR validation. All runtime inputs remain identical through4908176; intervening starter changes are README/SOURCE-MANIFEST only. Scoped security/public-exposure review PASS, no concrete blockers. Final exact-SHA CI, PDF/draft asset verification and owner decision remain external acceptance gates below.
