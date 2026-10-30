# Когда сборка остановилась

Вход: команда, её код возврата и последние строки ошибки. Сохраните их в отчёт. Не лечите окружение удалением всего проекта.
Ниже команды выполняются из корня starter. `$PY` — Python из README; TTS использует отдельный `$OMNI_PY`.

| Ошибка / этап | Что проверить | Что сделать и повторить | Ожидаемый выход |
|---|---|---|---|
| `python3.11: command not found`, импорт numpy/PIL/Playwright | `./make.sh doctor`; версия Python и значение PY | Установка README; `export PY="$PWD/.venv/bin/python"`; `./make.sh doctor` | Все обязательные пункты OK |
| `tsc` отсутствует / scene | Наличие `node_modules/.bin/tsc`, версия Node | `npm ci`; `./make.sh scene` | `build/scene.js`, код 0 |
| Chromium executable missing / frames/render | Doctor, версия Playwright, его кэш | `"$PY" -m playwright install chromium` (Linux: `install --with-deps chromium`); `./make.sh doctor`; `./make.sh frames` | Контактные листы `qa/frames/` |
| Шрифт не загрузился / render | Файлы `assets/fonts/`, сеть и сообщение fonts | `./make.sh fonts`; `./make.sh frames` | Onest/PT Serif и лицензии; текст без подмены/обрезки |
| Получено неверное число WAV/M4A / live | Число реплик в chunks и аргументов live | Один файл на каждую реплику; `./make.sh live voice/my-0.m4a voice/my-1.m4a voice/my-2.m4a` | raw-N.wav и новый voice-track.json |
| Загрузка Whisper не удалась / trim/finish | Сеть, кэш модели и свободный диск; `ASR_MODEL` | Восстановить доступ; повторить прежнюю live/voice или `./make.sh finish` | ASR-результат, без умолчания о пропуске |
| ASR расходится с текстом / trim/finish | raw-N.wav на слух, ratio, endings, chunks/lines и NUM | Исправить свою запись; live → frames → all | Совпадающая речь; QA ≥ заданного порога |
| `дубли не сходятся с паспортом` / trim | voice/raw-N.json: текст реплики в chunks.json правили после синтеза или raw-N.wav подменён | Пересинтезировать реплику (`python3 locked.py voice -- "$OMNI_PY" voice/gen_omni.py N`) или заново `./make.sh live …`; паспорт руками не правьте | trim.py проходит, asr-N.json от текущего текста |
| `ASR не нашёл ни одного слова` / trim | voice/raw-N.wav (или line-N.wav) на слух: тишина, обрыв, другой язык; ASR_LANG/--lang | Перезаписать реплику N (`./make.sh live …` или `python3 locked.py voice -- "$OMNI_PY" voice/gen_omni.py N`); язык — `--lang=<код>` | trim.py проходит, в asr-N.json есть слова |
| `lines.json съедает K произнесённых слов, chunks.json произносит M` / trim | Реплика N: слова экрана против слов речи, метки `{N}` («Mi_Box{2}» = два слова речи) | Поправить voice/lines.json (или текст в chunks.json и пересобрать голос); `voice/trim.py track` | Числа совпадают, voice-track.json собран |
| Финал упал до отчёта (ffmpeg, ASR) / finish | Текст ошибки в терминале и `error` в qa/final-result.json (status technical_failed, video null) | Исправить причину; `./make.sh finish`. Прежний output/final.mp4 этим запуском не проверен | Новый final.mp4 и отчёт той же сборки |
| `takes_asr_ge_0_9` false или null / finish | qa/final-result.json → asr_takes: below_0_9 (дубль < 0,9) или missing_or_stale (нет asr-N.json, текст или line-N.wav поменялись после trim) | Ниже порога — переписать текст или запись реплики; устарело — `voice/trim.py N`, потом `./make.sh all` | Все дубли ≥ 0,9; дальше слушать ушами |
| `OMNI_PY`/`OMNI_REF` не задан, нет TXT / voice | `./make.sh doctor --voice`; личная WAV и точная TXT | Настройка OmniVoice из README; `./make.sh voice` | raw-N.wav, тайминг; проверить ударения на слух |
| Событие E не найдено / frames | Слова cues в voice-track.json против E и lines | Исправить слово события; `./make.sh frames`, затем `./make.sh all` | Предмет меняется на нужном слове |
| Ожидание lock / voice/render | Другой процесс этой очереди ещё работает? | Дождаться/остановить свой процесс; повторить исходную команду | Очередь отпускает шаг сама; чужую блокировку не удалять |
| После пробного `--from/--to` ролик короткий / finish | picture.mp4 — только отрезок? | `./make.sh render`; `./make.sh finish` | Полная длительность и свежий QA |
| `technical_failed` / finish | `qa/final-result.json`: конкретные checks | Исправить причину; сцена: frames → all; музыка: sound → finish | Обязательные проверки прошли, exit code 0 |
| `preview_partial` / finish | fake, FINISH_ARGS=--no-asr или asr_takes.missing_or_stale? | Для речи live/voice → frames → `./make.sh all` без FINISH_ARGS | Полный QA; частичный статус сам по себе не авария |
| Недостаточно диска / render/checkpoint | `df -h .`; размер frames/output/cache | Освободить ненужные данные по выбору владельца; повторить шаг | Выход записан целиком; модели бездумно не удалять |
| checkpoint отклонил имя | Только A–Z/a–z/0–9/_/-, первый символ буква/цифра | `./make.sh checkpoint save before-edit-2` | Новый приватный ZIP; существующий не затирается |
| checkpoint отклонил symlink/hash/schema | Ссылки в исходниках; целостность архива | Не восстанавливать повреждённое; выбрать сохранённую копию через list | До замены исходников проверены все SHA256 |

Если первая гипотеза не подтвердилась, проверьте ещё причины: неверный Python, устаревший тайминг, незавершённый рендер.
Зафиксируйте доказательство перед правкой. Три безрезультатных круга — повод вернуться к сохранённому состоянию и пересмотреть подход.

## Контрольная копия и возврат

Сначала дождитесь завершения сборки или остановите её. Между командами `all` нет общей транзакции;
checkpoint не блокирует редактирование другим приложением. Во время save/restore не меняйте файлы.

```sh
./make.sh checkpoint save before-edit
./make.sh checkpoint list
./make.sh checkpoint restore before-edit
```

Выход save: `.checkpoints/before-edit.zip`, приватный каталог 0700, архив 0600.
В него входят исходники и JSON/CSV, `.agents`, `scene`, `tools`, `examples`, `data`, `voice` (включая собственные
WAV/M4A/TXT), `assets`, `build`, `output`, `qa`. Разрешённые расширения явно перечислены в tools/checkpoint.py.
Неизвестные каталоги/расширения не подбираются. Храните данные ролика в этих папках.
Исключены `.env*`, `.git`, `.checkpoints`, node_modules, `.runtime`, venv, cache, models/weights, profiles и secrets.
Файл модели `.safetensors/.pt/.bin/.gguf` не входит по расширению. Это рабочий снимок, а не полная резервная копия компьютера.

Restore проверяет схему/пути/размеры/SHA256 каждого файла в отдельном временном каталоге.
В снимке обязательны make.sh и tools/checkpoint.py, чтобы сохранить возможность следующего возврата.
Симлинки во включаемых путях и в ZIP отклоняются; ZIP не распаковывается через extractall.
Перед заменой создаётся `before-restore-ДАТА-ID.zip`. Если страховочная копия не создана, замены не начинаются.
Файлы снимка встают поверх текущих по одному (замена каждого файла атомарна), make.sh и tools/checkpoint.py — последними,
добавленные после снимка включаемые файлы удаляются в самом конце; исключённые модели/окружения остаются.
CLI возврата поэтому не пропадает. При аварии посреди замены исходники могут оказаться смешаны: верните напечатанную
страховку, `./make.sh checkpoint restore before-restore-ДАТА-ID` (имя есть и в `./make.sh checkpoint list`).

Если CLI всё-таки не запускается (make.sh или tools/checkpoint.py испорчены не restore'ом), страховка — обычный ZIP,
файлы лежат в нём под `files/`. Ручной возврат из папки starter:

```sh
unzip -l .checkpoints/before-restore-ДАТА-ID.zip            # что внутри
unzip -p .checkpoints/before-restore-ДАТА-ID.zip files/tools/checkpoint.py > tools/checkpoint.py
unzip -p .checkpoints/before-restore-ДАТА-ID.zip files/make.sh > make.sh && chmod +x make.sh
./make.sh checkpoint restore before-restore-ДАТА-ID         # остальное с проверкой SHA256
```

Без CLI вовсе: `unzip -o .checkpoints/before-restore-ДАТА-ID.zip 'files/*' -d .checkpoints/возврат`, затем скопируйте
содержимое `.checkpoints/возврат/files/` в папку starter. Так хэши не проверяются; сверить их можно по `manifest.json` в том же ZIP.
Лимиты защиты архиватора: 100 000 файлов и 64 GiB несжатых данных; это не требования к машине.

Архив содержит личные записи и готовые видео. `.gitignore` исключает `.checkpoints/`; в публичный ZIP его не добавляйте.
Права доступа ограничивают локальное чтение, шифрования нет. После проверки возврата скопируйте нужные приватные архивы
на собственный резервный носитель: копия на том же диске не защищает от потери диска.
