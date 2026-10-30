# Text and humanizer

Script text for videos and posts: remakes without plagiarism and checking text (the first line lives in [hooks/](../hooks/README.md), reel length and script approval in [idea/](../idea/README.md)) with the [humanizer-ru](https://github.com/ilyautov/humanizer-ru) scanner (MIT) before voice synthesis. Format: [recipe template](../../templates/recipe.md). `proven` only where there is a number.

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [text-fact-lock-before-after](text-fact-lock-before-after.md) | hypothesis | ru | Diff edited text against the source on numbers, dates, names; read logic by eye. |
| [text-humanize-script-before-tts](text-humanize-script-before-tts.md) | proven | ru | Scan and edit the script before the first TTS take. |
| [text-local-edit-not-rewrite](text-local-edit-not-rewrite.md) | proven | any | Mark spots and fix them; never rewrite paragraphs "for liveliness". |
| [text-modern-chatgpt-tells](text-modern-chatgpt-tells.md) | proven | ru | Grep for dashes, triplets, "new stage", not old clichés. |
| [text-scanner-genre-flag](text-scanner-genre-flag.md) | proven | ru | Pass `--genre` so reference/legal text isn't penalized. |
| [text-scanner-misses-form-slop](text-scanner-misses-form-slop.md) | proven | any | Scanner "clean" ≠ living script; check form with five questions. |
| [text-claude-md-plain-russian](text-claude-md-plain-russian.md) | hypothesis | ru | Countable rule in CLAUDE.md: words −47 %, markers 24 → 9 (8 questions × 1 run). |
