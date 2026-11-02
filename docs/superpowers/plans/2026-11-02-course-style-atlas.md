# Course style atlas Implementation Plan

> **For agentic workers:** Use subagent-driven-development for the scoped content-and-assets task, followed by independent review. Preserve the approved eight-style selection and the existing book layout.

**Goal:** Add eight examples from the author's own archive to the image/frame lesson, connect them to learning tasks, and deliver updated Russian and English PDFs for local review.

**Architecture:** Existing learn/ru and learn/en chapter 04 contain the atlas; chapter 05 links to it. Source images and a provenance/credits manifest live in assets/textbook/style-atlas/. The existing PDF builder is reused unchanged; no new platform or course engine.

**Tech Stack:** Markdown, JPEG, JSON, existing Python/WeasyPrint PDF builder and Poppler verification.

## Global Constraints

- Work in the isolated local not-a-blogger clone, branch codex/course-style-atlas, starting from 008ae7786549b0cebb20d869e41ca575a0f835e5. The initial delivery was local only; the repository-sync follow-up below supersedes that delivery limit.
- The source video-pipeline-agent workshop is read only. Do not modify or re-render source videos, voice references, models or profiles.
- User approved these eight styles: retro 1930s, instructional-film 1950s, voxel, PS2-era cutscene, film look, typography/photo, paper collage, halftone comic.
- Preserve the existing book's typography, layout, chapter count, examples, exercises and factual copy outside this addition. Add material about visual choice, not claims of better reach.
- Six video/style-board examples and two static research frames must be clearly distinguished. A still cannot prove motion, voice, retention or artistic acceptance.
- Preserve current publication/status boundaries. An approved visual test is not a published video.
- Do not copy private paths into shipped metadata. Attribution and license exceptions for the collage/comic photos must accompany the images.
- No new image generation, heavy model download, unrelated pipeline fixes or global package installation.
- Verify only checks appropriate to this content change: source/provenance, links, privacy, existing textbook tests, rendered PDFs. Do not repeat unrelated full video tests.

## Task 1: bilingual atlas and source assets

**Ownership:** worker owns assets/textbook/style-atlas/, assets/README.md, learn/ru/04-image-and-frame.md, learn/en/04-image-and-frame.md, learn/ru/05-camera-editing.md, learn/en/05-camera-editing.md. No Python, CSS, templates, recipes or AGENTS changes.

- [x] Read AGENTS.md, docs/BRAND.md, docs/THIRD-PARTY.md and the two chapters in both languages before editing.
- [x] Copy R30/R50/VOX/SA3/FILM/REEL still.jpg from the workshop styles catalog, naming them retro-30s.jpg, instructional-50s.jpg, voxel.jpg, ps2-cutscene.jpg, film-look.jpg, typography-photo.jpg. Retain exact source bytes.
- [x] Convert research-2026-10-19-styles/frames/2-collage.png and 4-comic.png to paper-collage.jpg and halftone-comic.jpg with high quality, without cropping or creative alteration.
- [x] Add source-manifest.json with source-relative paths, original and published SHA256, dimensions, media kind, historical status date and image rights. Catalog stills are frame boards; do not invent exact source-video timestamps.
- [x] Add CREDITS.md with all Wikimedia author/source/license details from research-2026-10-19-styles/frames/credits.md and distinguish generated 1950s/film stylization from documentary archive.
- [x] Insert a compact atlas section in chapter 04 before its existing exercise. Each of the eight entries has an image, what visual mechanism it demonstrates, a concrete learner task and an observable completion check. Keep original exercise and warnings.
- [x] Add one exercise where the learner proposes the same event in two styles and explains what changes beyond palette. Agent instructions specify the chosen material, intended action and check, without claiming the pictured static study was animated.
- [x] Add a short contextual link in chapter 05 in both languages. Add assets README provenance/rights note. Do not present additional engines as bundled.
- [x] Run python3.11 scripts/lint_recipes.py and python3.11 scripts/build_index.py --check. Report exact files, commands and any unresolved concerns; do not commit.

## Task 2: render and review

**Ownership:** parent owns environment setup, PDF outputs, validation and plan ledger. Reviewer reads all changed files and rendered evidence.

- [x] Use a dedicated Python environment only if required by the existing builder. Reuse the repository's declared PDF dependencies; no system package changes.
- [x] Before PDF authoring, invoke the PDF artifact-operation marker once. Build with python scripts/build_textbook_pdf.py --out output/pdf.
- [x] Run existing tests/test_textbook_pdf.py and tests/test_credits.py, asset SHA/dimension/link checks, and scripts/privacy_check.sh.
- [x] Render all-page contact sheets and inspect the cover/contents plus every page containing the new atlas in both PDFs. Fix clipping, illegible captions and orphaned headings in one bounded batch if needed.
- [x] Independent content/provenance/code review with full diff and PDF-page screenshots. Address material findings and confirm once.
- [x] Record final paths and checks. Deliver local PDFs and a visual preview; keep GitHub unchanged.

## Evidence ledger

02.11: user approved the eight-style board. Main is 008ae7786549b0cebb20d869e41ca575a0f835e5; isolated clone created on codex/course-style-atlas. Context inspection confirmed a scoped extension of existing reading material, not a redesign. Source videos remain untouched.

02.11 final: Task 1 spec/provenance review PASS; final independent content/code/rendered-artifact review APPROVE, no actionable findings. Six catalog JPEGs match source bytes; both static-study conversions retain 1080×1920. Both language chapters preserve all prior copy and exercises. Direct Commons author/source/license/change credits are in both chapters.

The first PDF gate found em dashes in new copy; those additions were corrected. Rendered review caught the Russian film example's status caption on the next page. Image/status pairs now stay together with local Markdown HTML wrappers; the builder and global CSS remain unchanged. Final cover, contents and all atlas pages 42–45 were inspected in both languages; all-page contact sheets are available in output/pdf/review/.

Final validation: 28 existing textbook/credits tests passed; recipe lint 142 with 0 errors; index fresh; privacy clean; diff whitespace check clean. PDFs: output/pdf/not-a-blogger-textbook-ru.pdf (82 pages, SHA256 9b269f7a935fd39a4e96e66ced8ca195422519bfbb4129c8d128510bddf36dd9) and output/pdf/not-a-blogger-textbook-en.pdf (83 pages, SHA256 46c2e0fdd25e5bd1bff0723fc0836dab1bd555cc0f8b3ccc306a0aef72925369). Preview: output/pdf/style-atlas-preview.jpg. Verification details: output/pdf/review/verification.json.

Completion is scoped to this local textbook addition and its rendered pages. No new video, motion/audio validation or publication was performed; no external repository writes were made.

## Repository-sync follow-up

02.11: after local delivery, the user asked whether everything had been uploaded to the repository. Proceeding with the reviewed textbook sources on main and a new v0.1.1 release containing the two verified PDFs, following the existing release convention. Prior v0.1.0 is preserved. This authorization concerns textbook/repository delivery; video publication remains outside the task.

Fresh pre-upload checks: 28 textbook/credits tests passed; recipe lint 142 with 0 errors; index fresh; privacy clean; diff whitespace check clean. Remote main still matches the reviewed base. No source workshop files, videos, audio, models, environments or private paths are included.
