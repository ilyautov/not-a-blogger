#!/usr/bin/env bash
# One command from lines.json to output/skit.mp4 + contact sheet + loudness:
#   bash rebuild.sh            # placeholder babble or the takes listed in lines.json
#   bash rebuild.sh --asr      # word timings from faster-whisper for real takes
# PY=/path/to/python bash rebuild.sh   if your python with numpy/soundfile/playwright is not "python3".
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
"$PY" build_audio.py "$@"
"$PY" render.py
mkdir -p qa
ffmpeg -v error -y -i output/skit.mp4 -vf "fps=1.5,scale=216:384,tile=9x6" -frames:v 1 qa/sheet.jpg
ffmpeg -i output/skit.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
echo "done: output/skit.mp4, qa/sheet.jpg (look at the sheet yourself before calling it ready)"
