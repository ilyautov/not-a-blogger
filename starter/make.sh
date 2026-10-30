#!/usr/bin/env bash
# Связка шагов. Запуск из любой папки: ./make.sh <шаг> (без шага печатает эту справку)
#   doctor  проверить окружение без загрузки моделей
#   live    импортировать свою запись: ./make.sh live voice/my-0.wav voice/my-1.wav voice/my-2.wav
#   fonts   скачать шрифты (один раз)
#   voice   OmniVoice -> voice/raw-N.wav, затем trim.py -> voice-track.json   (нужны OMNI_PY, OMNI_MODEL, OMNI_REF)
#   fake    заглушка голоса без синтеза (гудки) -> voice-track.json
#   scene   tsc: scene/scene.ts -> build/scene.js
#   frames  сухой просмотр: кадр каждые 0,75 с -> qa/frames/sheet-N.jpg
#   sound   метки из сцены + звук -> assets/audio/master.wav
#   render  покадровый рендер -> output/picture.mp4
#   finish  сведение + QA -> output/final.mp4, qa/sheet.jpg, qa/final-result.json
#   all     scene + sound + render + finish (голос должен быть готов)
#   checkpoint save NAME | checkpoint list | checkpoint restore NAME (сначала остановите сборку)
# Переменные: PY (python с numpy/scipy/soundfile/pillow/playwright/faster-whisper), OMNI_PY (python из venv OmniVoice),
#             TSC (по умолчанию node_modules/.bin/tsc), FINISH_ARGS (например --no-asr для заглушки).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3.11}
TSC=${TSC:-node_modules/.bin/tsc}
export TSC
L=("$PY" locked.py)   # тот же интерпретатор, что и для шагов: отдельный python3 не нужен
step=${1:-help}
if [[ "$step" != help && "$step" != fonts ]] && ! command -v "$PY" >/dev/null 2>&1; then
  echo "нет $PY: задайте PY=/путь/к/python3.11 (например PY=\$PWD/.venv/bin/python)" >&2; exit 127; fi
case "$step" in
  checkpoint) "$PY" tools/checkpoint.py "${@:2}" ;;
  doctor) "$PY" tools/doctor.py "${@:2}" ;;
  live)   "${L[@]}" voice -- "$PY" voice/import_live.py "${@:2}"
          "${L[@]}" voice -- "$PY" voice/trim.py ;;
  fonts)  ./tools/fonts.sh ;;
  voice)  "${L[@]}" voice -- "${OMNI_PY:?задай OMNI_PY}" voice/gen_omni.py
          "${L[@]}" voice -- "$PY" voice/trim.py ;;
  fake)   "$PY" voice/fake_track.py ;;
  scene)  "$TSC" -p scene ;;
  frames) "$TSC" -p scene; "${L[@]}" render -- "$PY" tools/render.py --frames 0.75 ;;
  sound)  "${L[@]}" render -- "$PY" tools/render.py --probe; "${L[@]}" render -- "$PY" tools/sound.py ;;
  render) "${L[@]}" render -- "$PY" tools/render.py ;;
  finish) "${L[@]}" render -- "$PY" tools/finish.py ${FINISH_ARGS:-} ;;
  all)    "$TSC" -p scene
          "${L[@]}" render -- "$PY" tools/render.py --probe
          "${L[@]}" render -- "$PY" tools/sound.py
          "${L[@]}" render -- "$PY" tools/render.py
          "${L[@]}" render -- "$PY" tools/finish.py ${FINISH_ARGS:-} ;;
  help) sed -n '2,16p' "$0" ;;
  *) sed -n '2,16p' "$0"; exit 1 ;;
esac
