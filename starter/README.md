[English version](README.en.md)

# Рил из кода: стартовый набор

Результат: вертикальный MP4 1080×1920, 30 fps, H.264 + AAC. Сцена рисуется на TypeScript + Canvas,
звук собирается Python, кадры снимаются локальным Chromium. Публикации и платных API в этом наборе нет.

Два примера: демо про сборку (три реплики) и отдельная история про подписку в examples/subscription/.
Начните с [FIRST-TASK.md](FIRST-TASK.md): точное поручение агенту для учебной подписки, затем полная задача на свою тему.
Для ручного первого прогона повторите демо ниже; второй пример описан в [SECOND-REEL.md](SECOND-REEL.md).
Среда/сеть/место — [RESOURCES.md](RESOURCES.md), отказы и возврат — [DIAGNOSTICS.md](DIAGNOSTICS.md),
выдача — [DELIVERY.md](DELIVERY.md). 

## 1. Установка

Проверенный профиль — macOS 26.2, Apple Silicon, Python 3.11, Node 24.21. Нужны Node 18+ и ffmpeg/ffprobe.
CI на Ubuntu 24.04 с Python 3.11 и Node 22 прошёл пробник fake/no-ASR, тесты и сборку PDF
([прогон](https://github.com/ilyautov/not-a-blogger/actions/runs/41465997589)). Полный путь с настоящей речью,
ASR, TTS и GPU на Linux не проверен. Нативная Windows не поддерживается (`fcntl` и Bash); WSL не проверялся.
Модели LTX и NVIDIA для 2D-сцены не нужны.

Если Homebrew уже установлен, недостающие инструменты можно поставить так:

```sh
brew install python@3.11 node ffmpeg
```

В терминале перейдите в папку starter этого репозитория (или в её копию, см. SECOND-REEL.md):

```sh
npm ci
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock-macos-arm64.txt
.venv/bin/python -m playwright install chromium
export PY="$PWD/.venv/bin/python"
./make.sh fonts
./make.sh doctor
```

`doctor` проверяет импорты, системные программы, компилятор и запуск браузера. При FAIL исправьте указанную причину;
WARN (пустая assets/fonts, нет faster-whisper) не мешает fake-прогону. Если make.sh пишет «нет python3.11», задайте PY.
В новом окне терминала снова задайте PY. Шрифты Onest и PT Serif скачиваются вместе с OFL-лицензиями.
requirements.txt фиксирует прямые зависимости; requirements-lock-macos-arm64.txt — полное проверенное окружение.
Для другой ОС используйте requirements.txt и отдельно проверяйте совместимость.

На Ubuntu 24.04 CI использует requirements.txt вместо macOS lock-файла и ставит системные библиотеки Chromium:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install --with-deps chromium
```

## 2. Первый результат без TTS и ASR

```sh
./make.sh fake
./make.sh frames
FINISH_ARGS=--no-asr ./make.sh all
open output/final.mp4
cat qa/final-result.json
```

Получится видео с гудками вместо речи. Нормальный статус — `preview_partial`, `technical_pass: false`.
Вы проверили сборку и постановку, но ещё не речь. Контактный лист — qa/sheet.jpg.

Время установки, скачивания моделей и работы человека не входит во время рендера. На подготовленном Mac
демо с голосом раньше собиралось примерно за две минуты, на другой машине время будет другим.

## 3. Своя начитка: путь без клонирования

Прочитайте voice/chunks.json. Запишите каждую реплику отдельным WAV/M4A, назовите my-0.m4a, my-1.m4a, my-2.m4a.
Текст должен совпадать, начало и окончание слова целиком остаются в записи. Не называйте исходники raw-N.wav.

```sh
./make.sh live voice/my-0.m4a voice/my-1.m4a voice/my-2.m4a
./make.sh frames
./make.sh all
open output/final.mp4
```

Импортер приводит записи к 24 кГц/mono, затем trim.py подрезает паузы, распознаёт слова и строит тайминг.
Whisper large-v3 при первом обращении скачивает веса в кэш Hugging Face. Это отдельный сетевой шаг.
`ASR_MODEL=small` годится для пробы, но совпадение текста нужно проверить на выбранной модели и на слух.

Язык распознавания по умолчанию русский. Для другого языка задайте код Whisper один раз на окно терминала:
`export ASR_LANG=en` (действует и на trim.py, и на finish.py) или флагом: `voice/trim.py --lang=en`,
`FINISH_ARGS="--lang en" ./make.sh all`. Сверка текста с распознаванием берёт буквы и цифры любой письменности
(кириллица, латиница, греческий, деванагари…; ё = е, знак ударения не считается); пустой текст или пустое
распознавание дают ratio 0, а не успех. Сквозной прогон с Whisper проверен только на русском, нормализация других
письменностей — только тестами. Для языков без пробелов между словами (китайский, японский, тайский) фраза
сравнивается как одно слово, и ratio там грубый: проверяйте на слух. Демо-реплики в voice/chunks.json русские, а в trim.py русские жертвенный
хвост TAIL и словарь чисел NUM (и NUM в tools/finish.py): для своего языка замените и их.

## 4. Опционально: OmniVoice на Apple Silicon

В этом наборе код и веса TTS имеют разные условия. Прочитайте THIRD-PARTY.md и карточку конкретных весов.
Свой голос для клона — 10–20 секунд чистой записи без музыки и эха. Рядом нужен TXT с точной расшифровкой.
Личный референс в публичный архив не кладите.

```sh
python3.11 -m venv .runtime/tts-omnivoice/venv
.runtime/tts-omnivoice/venv/bin/python -m pip install -r requirements-omni-lock-macos-arm64.txt
export OMNI_PY="$PWD/.runtime/tts-omnivoice/venv/bin/python"
export OMNI_MODEL="$PWD/.runtime/tts-omnivoice/model"
"$OMNI_PY" -c 'from huggingface_hub import snapshot_download; import os; snapshot_download("k2-fsa/OmniVoice", revision="c5fdb5ccb189668d56333f77ba2629f4cd7535f4", local_dir=os.environ["OMNI_MODEL"])'
export OMNI_REF="$PWD/voice/my-ref.wav"
export OMNI_DEVICE=mps
./make.sh doctor --voice
./make.sh voice
./make.sh frames
./make.sh all
```

Точную команду установки сверили с https://huggingface.co/k2-fsa/OmniVoice и зафиксировали версии.
Новый venv проверяется отдельно от загрузки весов: в протоколе явно отмечено повторное использование локальной модели.
Синтез на MPS и CPU проверен на этом Mac; CUDA не проверен. На Mac последовательная загрузка весов включена в gen_omni.py:
асинхронная первая загрузка в тестовом окружении зависала на GIL.

Темп задаётся OMNI_SPEED, например 1.1. Неверное ударение исправляйте в тексте или заменой слова,
а затем проверяйте на слух. Сид 42 уменьшает случайность, но не гарантирует побайтовое равенство на другом устройстве.
Переозвучить одну реплику: python3 locked.py voice -- "$OMNI_PY" voice/gen_omni.py 1, затем trim.py 1.

## 5. Устройство

- voice/chunks.json — что произносится, числа словами; pause — тишина после реплики.
- voice/lines.json — что видно: цифры и латиница. Mi_Box{2} связывает одно показанное слово с двумя произнесёнными.
- voice/trim.py — ASR, подрезка, склейка; выход voice-track.json содержит cues и пословные start/end.
- voice/raw-N.json — паспорт исходного дубля (текст, движок, настройки, sha256); пишут gen_omni.py и import_live.py.
  trim.py останавливается, если дубль или текст реплики с паспортом разошлись.
- scene/scene.ts — исходник картинки; build/scene.js генерируется tsc.
- reel.json — лимит длительности, музыка и необязательный sound_events для новой сцены.
- tools/render.py — служебный HTTP-сервер, setTime(t), кадры и picture.mp4.
- tools/sound.py — голос, даккинг, SFX, стемы speech.wav/music.wav/sfx.wav и master.wav.
- tools/finish.py — финальный AAC/MP4, технический QA и SHA256.
- AGENTS.md, CLAUDE.md, BRIEF.md, .agents/skills/reel-starter/SKILL.md — переносимое задание агенту.
- .agents/skills/reels-direction/SKILL.md — самодостаточная карта приёмов R1–R18 и границы проверки; ссылок на чужие ролики в ней нет.
- .agents/skills/camera-moves/SKILL.md и camera-kit.js — 30 приёмов, формулы и готовый ES-модуль. Он не подключается к учебной сцене автоматически.
- analytics.csv — пустая таблица измерений; опубликованные посты и рассылку набор не создаёт.

Голос → voice-track.json → story.json → сцена/события → звук/рендер → final.mp4 → проверка человеком.
Время события берётся из слов. Если слово исчезло, исправьте E, а не подставляйте произвольную секунду.
Для чисел дополняйте NUM в trim.py и finish.py. Несопоставленные ASR-слова интерполируются; это не доказательство,
что все слова были произнесены. Проверяйте ratio каждой реплики и финальный ASR, затем слушайте.

Случайность в сцене задаётся фиксированным PRNG, setTime(t) зависит только от времени.
Субтитры рисуются отдельным слоем; камера двигает главный предмет. Стили и планы учебной сцены можно менять.

Музыка: при music.file=null синтезируется встроенный пэд. Для внешнего трека задайте путь, offset, gain и credit.
Проверяйте условия конкретного трека. Стемы пишутся до финального мастеринга и отличаются по громкости от MP4.

## 6. Команды и правки

```sh
./make.sh doctor
./make.sh scene
./make.sh frames
./make.sh sound
./make.sh render
./make.sh finish
```

Текст/голос: live или voice → frames → all. Сцена/события: frames → all. Только музыка: sound → finish.
Только экранный текст: voice/trim.py track → frames → all, с проверкой соответствия слов.
Кусок рендера для пробы: python3 locked.py render -- "$PY" tools/render.py --from 0 --to 4.
Он перезаписывает picture.mp4, поэтому после пробы перед finish соберите полный render.

`all` пересобирает сцену, звук, картинку и финал. Оно не синтезирует голос. Это простой последовательный набор,
а не инкрементальный runner. Голос и рендер идут через общую очередь /tmp/not-a-blogger-*.lock
(`python3 locked.py <имя> -- <команда>`; без `--` команда печатает подсказку и выходит).
Не меняйте LOCK_DIR между параллельными сборками, иначе получите разные очереди.

Перед существенной правкой остановите сборку и сохраните рабочее состояние:

```sh
./make.sh checkpoint save before-edit
./make.sh checkpoint list
./make.sh checkpoint restore before-edit
```

Контрольная копия приватная: в `.checkpoints/` входят и локальные voice/*.wav/m4a/txt, и MP4/QA.
Модели, окружения и профили исключены; состав публичных исходников перечислен в SOURCE-MANIFEST.json.
Restore сначала проверяет схему/пути/SHA256 и сохраняет страховочную копию. Добавленные после снимка
включаемые файлы будут удалены. При прерывании замены используйте имя страховочной копии из вывода.
Общей транзакции для all нет. Подробный состав, ограничения и отказы — в DIAGNOSTICS.md.

## 7. QA и ограничения

- ready_for_user_preview + technical_pass=true: все обязательные проверки прошли, использовалась речь и финальный ASR.
- preview_partial + technical_pass=false: гудки или пропущенный ASR; команда завершилась штатно для технической пробы.
- technical_failed + ненулевой exit code: нарушен обязательный порог. Исправьте причину из checks.
- artistic_approval и publication_approved всегда false: их автоматика не выдаёт.

Проверки: декодирование, faststart, 1080×1920/30 fps, длительность из max_duration, размер ≤100 МБ,
−15±1 LUFS, TP≤−1.5 dBTP по финальному AAC, статика ≤3 с, совпадение ASR≥0.9 у финала и у каждого дубля
(`takes_asr_ge_0_9` по voice/asr-N.json; нижняя граница, не пропуск). Результат дубля, устаревший после правки
текста или line-N.wav, не засчитывается: статус preview_partial, пока не переподрежете `voice/trim.py N`.
Откуда взят каждый порог и что из них мерилось: [QA-THRESHOLDS.md](../docs/QA-THRESHOLDS.md).
Порог статики — средняя разница серых кадров 135×240 при включённой камере: движение камеры может скрыть скучную
сцену. Для отдельной проверки из корня репозитория запустите:

```bash
python3 tools/lint/still_lint.py starter --step 0.5 --max-still 3
```

Обе Canvas-сцены набора предоставляют необязательный контракт `window.setQAMode(enabled: boolean)`.
При `true` он убирает камеру, переброски и зерно, сохраняя предметную анимацию и субтитры;
обычный рендер и `false` оставляют авторский вид. Линт включает этот режим перед пробами.
Без хука он сбрасывает CSS-transform у DOM-камеры `#world`; свою камеру можно отключить через
`--pre-js "window.cam.reset()"` (JS после каждого `setTime`). `--keep-camera` сохраняет камеру.
Смотрите `camera_control` в `qa/still-lint.json`: `setQAMode`, `dom-world`, `kept` или `unsupported`.
Последнее означает, что отключение не подтверждено; эффект собственного `--pre-js` нужно проверить отдельно.
Шаг должен быть конечным числом > 0, порог и допустимый застой — конечными числами >= 0.
ASR не проверяет ударения, интонацию и художественную ценность. Смотрите и слушайте готовый файл целиком.
Кадры и звуковые дорожки помощник может проверить отдельно; это ещё не непрерывный просмотр и прослушивание.

Код starter — MIT. Модели, личные записи и чужая музыка в эту лицензию не входят. THIRD-PARTY.md содержит ссылки.

## 8. Если застряли

Сохраните команду, код возврата и последние строки ошибки, затем идите по таблице в [DIAGNOSTICS.md](DIAGNOSTICS.md).
Ниже самые частые остановки первого прогона.

**`make.sh` пишет «нет python3.11» или npm не видит package.json.** Терминал открыт не в папке starter: `ls` должен
показать make.sh и package.json, перейдите туда через `cd`. Если venv уже создан, задайте `export PY="$PWD/.venv/bin/python"`;
в каждом новом окне терминала переменную задают заново.

**`doctor` пишет FAIL.** TypeScript: выполните `npm ci` или задайте `TSC=/путь/к/tsc`. Chromium: `.venv/bin/python -m playwright install chromium` (на Linux `install --with-deps chromium`).
node, ffmpeg, ffprobe: установите их (`brew install node ffmpeg`) и заново откройте терминал. При первом запуске
установки Playwright и Whisper нужен интернет; ошибку сети или сертификата не лечат отключением защиты.

**Кадры в qa/frames есть, а `all` остановился или MP4 нет.** Контактные листы и предпросмотр не считаются экспортом; итог только
в output/final.mp4. Прочитайте `qa/final-result.json`: при `technical_failed` в `checks` назван конкретный порог, его и
исправляйте. Для гудков без ASR запускайте `FINISH_ARGS=--no-asr ./make.sh all`; статус `preview_partial` в этом случае
штатный. Перед правкой сцены сохраните состояние: `./make.sh checkpoint save before-edit`.

**Своего компьютера мало для модели.** Для 2D-демо видеокарта не нужна: путь `fake` → `frames` → `all` собирает ролик
на любом Mac с Python 3.11 и Node 18+. OmniVoice (раздел 4) необязательна, своя начитка (раздел 3) её заменяет.
Whisper large-v3 тяжёлый: для пробы `ASR_MODEL=small`, но совпадение текста проверьте на выбранной модели и на слух.
Усложняйте один шаг, а не ставьте все модели сразу.

**Голос и распознавание ведут себя странно.** Неверное ударение у OmniVoice правится текстом или заменой слова,
а не параметрами. Расхождение ASR с текстом сначала проверьте на слух по raw-N.wav: распознавание ошибается само.
Грабли конкретных моделей собраны в [../gotchas/](../gotchas/) и в рецептах [../recipes/voice/](../recipes/voice/).
