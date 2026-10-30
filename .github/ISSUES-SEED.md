# Заготовки good first issue

Десять задач, готовых к заведению после открытия репозитория: каждая заводится отдельным issue с меткой
`good first issue` и меткой раздела. Текст issue — блок под заголовком, на английском (рецепты пишутся
по-английски, см. CONTRIBUTING.md). Каждая задача выполняет правило из [TRIAGE.md](../docs/TRIAGE.md): файл и образец
названы, есть команда проверки, назван отвечающий (мейнтейнер @ilyautov, ответ в течение недели).

Перед заведением сверить, что рецепт с таким приёмом не появился: `grep -ril "<ключевое слово>" recipes/`.

В разборах `examples/*/README.md` такие приёмы уже стоят строкой с пометкой «(рецепта пока нет)»: задача закрывается,
когда эта пометка заменена ссылкой на новый рецепт.

Общая проверка для задач-рецептов (№ 1–8), в issue её вставить целиком:

```bash
python3 scripts/lint_recipes.py          # 0 errors
python3 scripts/build_index.py           # rewrites recipes/README.md, index.json, BY-SYMPTOM.md, docs/CHANGELOG.md
python3 scripts/build_index.py --check   # "index is fresh"
bash scripts/privacy_check.sh            # "privacy_check: чисто" [clean]
```

---

## 1. Recipe: loop the ending into the first frame

Labels: `good first issue`, `recipe`
- **File:** `recipes/transitions/transitions-loop-ending.md`, from `templates/recipe.md`.
  Sample next to it: `recipes/transitions/transitions-smash-cut.md`.
- **Source:** `examples/free-friday` and `examples/mascot-cancels-call`, both looped shorts (section "Format and length" in `README.en.md`).
- **Scope:** how the last frame hands over to the first (same background, same object position, no fade to black),
  how to check the seam. No metric → `status: hypothesis`.
- **Done when:** the common check passes, and both example READMEs link the recipe under "Techniques used" (`README.en.md`) and its Russian twin in `README.md`:
  `grep -l transitions-loop-ending examples/*/README.md` prints two files.
- **Who answers:** @ilyautov.

## 2. Recipe: one counter as the hero of the whole video

Labels: `good first issue`, `recipe`
- **File:** `recipes/assembly/assembly-counter-as-hero.md`. Sample: `recipes/assembly/assembly-terminal-typing.md`.
- **Source:** `examples/free-friday` (meetings counter melts), `examples/mascot-cancels-call`, `examples/tv-no-ads`.
- **Scope:** one number lives through all scenes and changes on the spoken word; tween parameters from the example
  code; how to avoid two counters at once.
- **Done when:** the common check passes; `grep -l assembly-counter-as-hero examples/*/README.md` prints ≥ 2 files.
- **Who answers:** @ilyautov.

## 3. Recipe: count the catches with the same opener

Labels: `good first issue`, `recipe`
- **File:** `recipes/idea/idea-same-opener-tally.md`. Sample: `recipes/idea/idea-one-example-short-reel.md`.
- **Source:** `examples/deepseek-headlines` (headline after headline), `examples/three-keys-repeat`.
- **Scope:** each item starts with the same words, the count is visible; when it tires the viewer (more than 4 items
  is a hypothesis to state). Differs from `hooks-foreign-thesis-refrain` (that one closes with a refrain): say how.
- **Done when:** the common check passes; both example READMEs link the recipe.
- **Who answers:** @ilyautov.

## 4. Recipe: a silent beat under on-screen action

Labels: `good first issue`, `recipe`
- **File:** `recipes/sound/sound-silent-beat-under-action.md`. Sample: `recipes/sound/sound-sfx-by-meaning.md`.
- **Source:** `examples/free-friday`, section "Second-by-second structure" in `README.en.md`: 6.8–10.6 s without speech while the days fall.
- **Scope:** length of the pause (measure it in the example: `ffmpeg -i <video> -af silencedetect=n=-35dB:d=0.3 -f null -`),
  what plays instead (SFX, music), where it must not go (the first 3 seconds).
- **Done when:** the common check passes; the recipe's "Evidence" quotes the measured pause; free-friday links it.
- **Who answers:** @ilyautov.

## 5. Recipe: the last line is an action, not a conclusion

Labels: `good first issue`, `recipe`
- **File:** `recipes/cta/cta-last-line-action.md`. Sample: `recipes/cta/cta-deliver-before-asking.md`.
- **Source:** last lines of `examples/free-friday` and `examples/photo-geo-blind-test`.
- **Scope:** rewrite rule ("try X tonight" instead of "so, AI is powerful"), two before/after pairs from the examples.
- **Done when:** the common check passes; both example READMEs link the recipe.
- **Who answers:** @ilyautov.

## 6. Recipe: credit photos, maps and music in the video description

Labels: `good first issue`, `recipe`
- **File:** `recipes/publishing/publishing-credits-in-description.md`.
  Sample: `recipes/publishing/publishing-instagram-ai-label.md`.
- **Source:** `examples/photo-geo-blind-test` (Wikimedia CC BY-SA 4.0 photo with attribution at the end of README),
  `recipes/sound/sound-music-rotation.md` (CC BY music).
- **Scope:** a ready credit line format (author, title, license, link) for CC BY / CC BY-SA, where it goes on each
  platform, what is not a credit (a bare "from the internet").
- **Done when:** the common check passes; the recipe has a credit line copied from photo-geo-blind-test as its example.
- **Who answers:** @ilyautov.

## 7. Recipe: captions on top, small line plus one big word

Labels: `good first issue`, `recipe`
- **File:** `recipes/captions/captions-small-line-big-word.md`. Sample: `recipes/captions/captions-grow-upward.md`.
- **Source:** `examples/tv-no-ads` (captions at the top, numbers in color).
- **Scope:** sizes in px for 1080×1920, which word gets big, color only for numbers (see `captions-colors-contrast`).
- **Done when:** the common check passes; tv-no-ads links the recipe; the sizes in "Do" match the example's code or poster.
- **Who answers:** @ilyautov.

## 8. Recipe: hook as a loss ("you are losing hours")

Labels: `good first issue`, `recipe`
- **File:** `recipes/hooks/hooks-loss-promise.md`. Sample: `recipes/hooks/hooks-result-in-first-second.md`.
- **Source:** `examples/three-keys-repeat` (hook «Короче. Три кнопки в Клоде, без которых ты теряешь часы.» [Long story short. Three keys in Claude without which you lose hours], metrics in README).
- **Scope:** loss phrasing vs gain phrasing, three rewrites; `status: hypothesis` unless you have an A/B.
- **Done when:** the common check passes; three-keys-repeat links the recipe.
- **Who answers:** @ilyautov.

## 9. Pitfall: first line of `gotchas/lang/de.md` or `es.md`

Labels: `good first issue`, `gotcha`, `lang:de` or `lang:es`
- **File:** `gotchas/lang/de.md` or `gotchas/lang/es.md` (both are empty stubs with a template).
  Sample: `gotchas/lang/ru.md`.
- **Scope:** one or more lines "what breaks: model and version, input line in quotes, how often, workaround".
  Ideas to check are listed in the stub.
- **Done when:** the line has a count ("in 5 of 20 takes"); `bash scripts/privacy_check.sh` prints `privacy_check: чисто` [clean];
  the line «Nothing here yet» is removed.
- **Who answers:** @ilyautov.

## 10. Tool: YouTube chapters from the voice track

Labels: `good first issue`, `tool`
- **File:** `tools/project/chapters.py` + `tests/test_chapters.py`. Sample: `tools/project/artifacts.py` and
  `tests/test_tools_help.py` (every tool must answer `--help`).
- **Input:** `voice-track.json` from `starter/` (keys `cues[].start`, `cues[].text`) plus a short list of chapter
  titles with the cue id they start at. **Output:** text for the description, `0:00 Title` per line, first line
  `0:00`, at least 3 chapters, each ≥ 10 s (YouTube's rules). No upload, no network.
- **Done when:** `python3 -m pytest tests/test_chapters.py tests/test_tools_help.py -q` is green; the test builds
  a voice track in `tmp_path` and checks the 0:00 / ≥ 10 s rules; `tools/README.md` has one row for the tool.
- **Who answers:** @ilyautov.

---

## Резерв (без заготовки issue)

Приёмы из `examples/`, которые можно оформить позже тем же способом: шутка-сравнение на каждый пункт
(ai-text-tells), заезд камеры в мелкий шрифт (deepseek-headlines), двойной вывод «обещание преувеличено, угроза
реальна» (photo-geo-blind-test), два голоса: герой и «исполнительная» нейросеть (mascot-cancels-call), персонаж-реакция
в кружке (mascot-cancels-call), мат в панчлайне с цензурой в субтитрах (mascot-cancels-call), выбор дубля клона по
темпу живой записи (guess-my-voice), твист в финале (guess-my-voice), стоп-кадр перед выкриком
(instagram-to-claude-skit), поворот-обида в хуке (tv-no-ads); превью рецепта в CI (рендер примера в GIF).
