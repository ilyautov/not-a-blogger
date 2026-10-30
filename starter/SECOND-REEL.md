# Второй ролик: счёт за подписку

Общий маршрут от идеи до публикации: ../learn/ru/00-first-video.md.
Сюжет, интерфейс и 200 рублей учебные; возврат денег не обещается. Исходники: examples/subscription/.

1. Сделайте вторую копию набора рядом с первой: из корня репозитория `cp -R starter my-subscription`
   (копируйте чистую папку, без node_modules, .venv, output и qa).
2. Из my-subscription выполните:

```sh
cp examples/subscription/voice/chunks.json voice/chunks.json
cp examples/subscription/voice/lines.json voice/lines.json
cp examples/subscription/scene.ts scene/scene.ts
cp examples/subscription/reel.json reel.json
npm ci
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock-macos-arm64.txt
export PY="$PWD/.venv/bin/python"
./make.sh fonts
./make.sh doctor
./make.sh fake
./make.sh frames
FINISH_ARGS=--no-asr ./make.sh all
open output/final.mp4
```

Chromium устанавливается один раз для этой версии Playwright; при необходимости повторите команду из README.
Можно использовать готовый Python из первой копии, задав его абсолютный путь в PY, вместо создания нового .venv.

3. Прочитайте examples/subscription/BRIEF.md и объект E в scene/scene.ts. Места, где слово управляет картинкой,
помечены в scene.ts комментарием «ГОЛОС → ДВИЖЕНИЕ». cost на «двести»: пуш бьёт в стопку, камера вздрагивает.
cancel на «продление»: переключатель щёлкает, строка «Автопродление» гаснет. zero на «ноль»: разряды «200»
встают в «0» ровно в начале слова, камера делает панч. receipt на «чек»: чек выползает, камера отъезжает.
Переброска в настройки стоит за 0,12 с до начала второй реплики. В конце экран возвращается к первому кадру,
ролик зациклен. sound_events в reel.json использует cost/cancel/zero/receipt.
4. Проверьте синхронность счётчика: в консоли страницы window.counterAt(t) возвращает показанное число.
«0» должен встать не позже чем через 2 кадра (0,067 с) от window.events.zero.
5. Речь без записи своего голоса: OmniVoice в режиме voice design, без референса и клона (условия весов — THIRD-PARTY.md).
Установка venv и весов — README, шаг 4; OMNI_REF не нужен.

```sh
cp examples/subscription/voice/gen_design.py examples/subscription/voice/snap_onsets.py voice/
python3 locked.py voice -- "$OMNI_PY" voice/gen_design.py
python3 locked.py voice -- "$PY" voice/trim.py
python3 locked.py voice -- "$PY" voice/snap_onsets.py
./make.sh frames
./make.sh all
```

snap_onsets.py уточняет начала слов после пауз по энергии: Whisper ошибается там до 0,1 с, а это 3 кадра.
Своя начитка — make.sh live с четырьмя файлами по README, затем тот же snap_onsets.py. Новая речь меняет тайминг, сцена переезжает сама.
6. Если хотите изменить сумму, обновите chunks.json, lines.json, E, рисуемые числа, COLS счётчика и NUM в trim.py/finish.py.

При смене одной реплики сначала сделайте новый сухой просмотр. Не обрезайте окончание ради старого тайминга.
Сравните начало и конец: пуш «Списано 200 ₽» в начале, «0 ₽» и чек в конце, последний кадр равен первому.
Прочтите суммы на телефоне, затем прослушайте окончания слов и клик переключателя. Итоговый статус QA не означает одобрения человеком.
