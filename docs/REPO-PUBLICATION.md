# Repository publication checklist

Release workflow for **v0.2.0**, initially prepared privately. The release notes and handoff record the actual
publication status, exact source commit and CI. Repository visibility and release publication are separate actions
authorized by the author; no announcement or platform upload follows automatically.

## What a reader gets

An agent toolkit with 143 recipes (**73 measured, 70 hypotheses**), prompts, templates, build and QA tools, two
starters and twelve real video breakdowns. The included text mini-course for people has twelve numbered chapters
with exercises, a roadmap and a glossary. [English entry](../README.md), [separate Russian entry](../README.ru.md).
Eighteen [repo-scoped skills](../.agents/skills/README.md) cover fifteen focused tasks and three workflow coordinators
for video creation, QA and a separate publisher.
The [publisher brief](publisher/README.md) is a recipe to implement, not an included upload client.
The eight-style gallery uses the author's existing productions/studies, with [source and rights boundaries](../assets/textbook/style-atlas/CREDITS.md).
The human approves the script, watches and listens to the finished file, and publishes it.

## Verify the candidate source

Use Python 3.11 and the dependencies installed by [.github/workflows/ci.yml](../.github/workflows/ci.yml).
The metadata checks need no paid keys, model weights or voice references:

```bash
python3.11 scripts/lint_recipes.py
python3.11 scripts/build_index.py --check
python3.11 scripts/starter_manifest.py --check
bash scripts/privacy_check.sh
git diff --check
```

The existing automated suite is `python3.11 -m pytest tests/ -q`. The final launch record must link the successful
CI run for the **candidate's exact commit**; a green run for an older revision is not final evidence.
[Baseline CI at cd25fb1](https://github.com/ilyautov/not-a-blogger/actions/runs/41465997589) passed on Ubuntu 24.04:
tests, both demo paths and both PDF builds. [Current workflow runs](https://github.com/ilyautov/not-a-blogger/actions/workflows/ci.yml).

A separate clean-clone check on macOS arm64 at runtime commit `0c1691ec53d9bb43f699659c08267522c6fab35b`
on 2 November also produced the silent 15.000-second MP4 and the full starter's 11.733333-second fake/no-ASR demo.
It used a new Python 3.11 environment and declared requirements. Decode and selected frame contacts were checked;
the full starter reported `preview_partial`, `technical_pass: false`, both ASR checks unset. There was no continuous
audio/video review or real-voice/TTS/ASR validation in that check.

### Reproduce the two CI demos in a clean clone

These commands mirror the `newbie-path` job on Ubuntu 24.04 with Node 22, Python 3.11 and ffmpeg installed.
Before public opening, cloning needs repository access. Substitute the reviewed full commit SHA printed by the
launch handoff for `CANDIDATE_SHA`:

```bash
git clone https://github.com/ilyautov/not-a-blogger.git not-a-blogger-launch
cd not-a-blogger-launch
git checkout CANDIDATE_SHA
git rev-parse HEAD
cd starter-lite
npm run check
npm run render
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 output/first-video.mp4)
python3.11 -c "import sys; d=float('$d'); print(d); sys.exit(0 if 14.5 < d < 15.5 else 1)"
cd ../starter
npm ci
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
export PY="$PWD/.venv/bin/python"
./make.sh fonts
./make.sh fake
./make.sh frames
FINISH_ARGS=--no-asr ./make.sh all
python3.11 -c "import json,sys; r=json.load(open('qa/final-result.json')); print(r['status'], r['checks']); sys.exit(0 if r['status']=='preview_partial' else 1)"
```

The first run needs internet for pinned HyperFrames, packages, fonts and Chromium, and may need permission to
install browser system libraries. It downloads **no TTS/ASR model weights** and uses no paid API.

Inspect `starter-lite/output/first-video.mp4` (15 seconds, silent, no finished-file QA) and
`starter/output/final.mp4`, `starter/qa/sheet.jpg`, `starter/qa/final-result.json`. The full starter's demo has
beeps instead of speech: expected **`preview_partial`, `technical_pass: false`**. Passing it establishes the build
and staging path, not spoken-word accuracy, lip sync, artistic quality or approval to publish.

macOS on Apple Silicon is the local reference environment. Ubuntu CI does not establish the full real-voice,
ASR, TTS or GPU workflow on Linux. Native Windows is unsupported for the full starter (`fcntl` and Bash);
WSL is unverified. Real voice needs the person's own recordings or a separately configured model, permissions
and license checks; see [starter](../starter/README.en.md) and [third-party terms](THIRD-PARTY.md).

## Release artifacts and source identity

Earlier releases [v0.1.0](https://github.com/ilyautov/not-a-blogger/releases/tag/v0.1.0) and
[v0.1.1](https://github.com/ilyautov/not-a-blogger/releases/tag/v0.1.1) predate the v0.2.0 entry/reliability/skills changes.
Keep published releases and their assets intact. A draft does not replace `/releases/latest`; verify that endpoint
after publication. Commands below use v0.2.0 as the example; use the new version for later releases.

Build from the final reviewed source, with the PDF dependencies and system libraries from CI:

```bash
python3.11 scripts/build_textbook_pdf.py --out dist
```

Before publication, prepare a **draft** with `not-a-blogger-textbook-en.pdf`, `not-a-blogger-textbook-ru.pdf` and `SHA256SUMS`.
The release notes must record the exact source commit, the PDF build command, CI link and the actual checks performed.
Inspect affected pages in both languages before calling them reviewed. Do not copy older PDF page counts into the new release.

Verify local files against downloaded draft assets using the author account before publishing:

```bash
git rev-parse HEAD
gh release view v0.2.0 --repo ilyautov/not-a-blogger --json isDraft,targetCommitish,assets
shasum -a 256 dist/not-a-blogger-textbook-en.pdf dist/not-a-blogger-textbook-ru.pdf
mkdir -p release-verify
gh release download v0.2.0 --repo ilyautov/not-a-blogger --dir release-verify
(cd release-verify && shasum -a 256 -c SHA256SUMS)
git ls-remote origin refs/heads/codex/publication-ready refs/tags/v0.2.0 'refs/tags/v0.2.0^{}'
```

Compare uploaded asset digests with local hashes. Resolve the release target to the reviewed commit; if a tag exists,
resolve it too. A private draft may not create the tag until publication, so an absent tag is not proof of a mismatch.
`SHA256SUMS` covers the two PDF filenames, using basenames so verification works after download. Source integrity is
identified by the full Git commit; PDF hashes identify the actual downloadable artifacts.

## GitHub opening and manual preview

[REPO-SETTINGS.md](../.github/REPO-SETTINGS.md) records the applied About text, website, 17 topics and feature settings.
`assets/social-preview.jpg` is ready; a custom preview was **not installed** during preparation. The author
chose manual upload: **Settings → General → Social preview → Edit → Upload an image**, select the JPEG, save and recheck.

After reviewing the exact commit, draft and evidence, the author can change **Settings → General → Danger Zone →
Change repository visibility** to public. Recheck the public English/Russian entry, relative images, licenses,
Actions and release links from a signed-out browser. Publish v0.2.0 separately when intended, then verify both PDF
downloads and `/releases/latest`. Check private vulnerability reporting after opening, per the settings ledger;
[SECURITY.md](../SECURITY.md) keeps the email fallback. No claim that all security risks were eliminated is implied.

## Prepared launch copy — not posted

**English**

> I'm not a blogger, I'm an engineer. I need the videos, not the profession.
>
> I put my video workshop into a toolkit for AI agents: recipes, prompts, templates and tools for building and
> checking short videos. There are 143 recipes (73 backed by measurements, 70 hypotheses), 12 real breakdowns
> including flops, 18 agent skills, two starters, and an eight-style visual atlas. Start with a silent 15-second render.
>
> A text mini-course for people is included: 12 chapters with exercises on scripting, voice, staging, sound and
> checking the result. English first, with a separate Russian version and PDFs in both languages.
> You approve the script and publish the video yourself.
>
> https://github.com/ilyautov/not-a-blogger

**Русский**

> Я не блогер, я технарь. Ролики мне нужны, профессия нет.
>
> Собрал свою видеомастерскую в тулкит для ИИ-агентов: рецепты, промпты, шаблоны и инструменты сборки и проверки
> коротких роликов. Внутри 143 рецепта (73 с замерами, 70 гипотез), 12 настоящих разборов с провалами, 18 скиллов, два стартера
> и атлас восьми визуальных стилей. Начать можно с немого ролика на 15 секунд.
>
> В комплекте текстовый мини-курс для человека: 12 глав с упражнениями про сценарий, голос, постановку, звук и
> проверку результата. Основная версия английская, русская отдельно, PDF на двух языках.
> Сценарий одобряешь ты, ролик публикуешь тоже ты.
>
> https://github.com/ilyautov/not-a-blogger

**Release summary (EN / RU)**

> v0.2.0: an English/Russian entry for the agent toolkit and included text mini-course, an overview of the existing
> eight-style atlas, more reliable worker locks and stillness checks, readable mobile slide decks, and updated
> textbooks. Demo QA remains partial without ASR.
>
> v0.2.0: вход в тулкит для агентов и текстовый мини-курс на английском и русском, обзор существующего атласа восьми
> стилей, исправления блокировки сборки и проверки застоя, читаемые слайды на телефоне и обновлённые учебники.
> Без ASR проверка пробника остаётся частичной.
