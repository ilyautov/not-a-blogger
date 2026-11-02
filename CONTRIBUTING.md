# Contributing

Thanks for stopping by. This is a technical kit: it doesn't say what to make videos about, it makes the build
measurable. The author used it one way (Russian shorts about AI tools); contributions that show another way are the
most welcome. You don't have to write code: the most valuable contributions are a TTS pitfall in your language, a
recipe with a number, and a breakdown of something you made with the kit, metrics included.

Merged contributions go to [CONTRIBUTORS.md](docs/CONTRIBUTORS.md); a recipe's author is listed in its front matter.

[Русская версия](docs/CONTRIBUTING.ru.md)

## What you can add in one evening

| Contribution | Where | Effort | Issue form |
|---|---|---|---|
| TTS pitfall in your language | `gotchas/lang/<code>.md`, one line | 15 min | "Pitfall" |
| General pitfall (ASR, render, platform) | `gotchas/README.md`, one line | 15 min | "Pitfall" |
| New recipe for agents | `recipes/<section>/<id>.md` from the [template](templates/recipe.md), English | 1 hour | "Recipe" |
| Language-specific sibling recipe | next to a `lang: ru` recipe, same section, `lang: <code>` | 1 hour | "Recipe" |
| Breakdown of your video | `examples/<slug>/README.md` | 1 hour | "My video" |
| Video made with the kit | one row in [MADE-WITH.md](docs/MADE-WITH.md) | 5 min | none, open a PR |
| Textbook chapter translation | `learn/<code>/` mirroring `learn/en/` | an evening | "Translation" |
| Fix a number or an outdated recipe | edit the file, bump `updated:` | 15 min | "Outdated recipe" |
| Tool | `tools/<group>/<name>.py` + test in `tests/` | an evening | "Recipe", marked "tool" |
| Template | `templates/<name>/` with README | an evening | "Recipe", marked "template" |

Not sure where to start? Look for an open issue labelled `good first issue`, or propose a small change using the
forms above. A label is not a promise that an issue is available. Labels are described in [TRIAGE.md](docs/TRIAGE.md).

## Recipes vs textbook

- **Recipes** (`recipes/`) are for agents: terse, imperative, exact parameters, a verification step. English only.
- **Textbook** (`learn/`) is for humans: why it works, real examples, mistakes. Each language has its own folder.

A new technique usually starts as a recipe. If it needs explaining, add a subsection to the matching chapter in
`learn/en/` and, if you can, `learn/ru/`.

## Recipe rules

1. **One technique, one file.** Two techniques mean two files linked under "Related".
2. **Search first.** If a close recipe exists, extend it. In the issue, say how yours differs.
3. **A number or an honest hypothesis.** `status: proven` needs a measurement, an A/B test or a published video's
   metric. Without numbers use `status: hypothesis`; we accept those too. `scripts/lint_recipes.py` enforces it:
   `proven` passes only with `evidence: measurement`, `ab-test` or `video-metric`; `experience` and
   `viewer-feedback` go with `hypothesis`. Thresholds a check fails on live in `docs/QA-THRESHOLDS.md`, not in recipes.
4. **Reproducible.** Commands run without paid API keys. If a paid model is required, say so under "Don't".
5. **Licenses for borrowed things.** Code, music, fonts and images from other projects come with a link and a license.
   No copying from AGPL, GPL or unlicensed repos: describe the idea in your own words.
6. **Nothing personal.** No absolute home-folder paths, keys, tokens, other people's voice references or faces without
   consent. CI checks this: `scripts/privacy_check.sh`.
7. **Language-specific recipes** set `lang:` and invite a sibling for other languages. The lint enforces the
   invitation: a recipe with `lang:` other than `any` must contain the word "contribute"; the ready line is at the
   end of the [template](templates/recipe.md).
8. **Two words for two people.** In instructions, *the person* is whoever the agent is helping: they approve the
   script, hear the voice, publish. In evidence, *the author* is whoever made the measured videos. Don't use "the user"
   or "the owner" for either.

### What `lang` means

`lang` is the language of the speech or text the technique depends on: a TTS quirk, an ASR habit, a scanner of
AI-written text. Use an ISO 639-1 code (`ru`, `en`, `de`); `any` when the technique does not depend on language
(camera, editing, render). The recipe body is English either way.

A sibling for another language is a separate file in the same section with its own `lang:` and its own evidence,
linked from both files under "Related". The id follows the usual `<section>-<short-name>` form; there is no sibling
in the kit yet, so when the technique is the same and only the language differs, we suggest the language code as the
suffix (`voice-f5-sacrificial-first-word-de`).
Don't turn a `lang: ru` recipe into `any` by adding a paragraph about another language: that hides which claims were
measured where.

## Breakdown rules

- Metrics come from the platform's analytics, with the date. No rounding up.
- Failures are welcome. "Why 3 views" teaches more than another "how I got a million".
- Media by link; no mp4 in git. A poster frame under 100 KB is fine.
- No faces of people who did not consent.

## Checks before a PR

```bash
python3.11 -m pip install -r requirements.txt pytest
python3.11 -m pytest tests/            # CI runs Python 3.11
python3 scripts/lint_recipes.py     # recipes, learn links, ru/en chapter parity
python3 scripts/build_index.py      # regenerates recipes/README.md, recipes/index.json, recipes/BY-SYMPTOM.md, docs/CHANGELOG.md
bash scripts/privacy_check.sh       # personal paths, keys, voice references
```

CI runs the same on every PR.

## Working with an agent

Writing a recipe with Claude Code or Codex? Give it [AGENTS.md](AGENTS.md). A recipe written entirely by an agent
without your check on a real video goes in as `hypothesis`.

## Code of conduct

Argue about techniques and numbers, not people. A reviewer may ask for a measurement: that's the rule of the kit, not
distrust. The full rules and where to report a problem: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
