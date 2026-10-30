#!/usr/bin/env bash
# Проверка на личное: ищет в репозитории строки, которых в открытом проекте быть не должно
# (личные пути, имена аккаунтов, ID канала, референсы голоса, ключи). Падает при находке.
# Запуск: bash scripts/privacy_check.sh [папка]   (по умолчанию корень репозитория)
# Вызывается в CI на каждый push и pull request.
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
SELF="scripts/privacy_check.sh"

# Шаблоны собраны из кусков, чтобы сам скрипт не находил себя при поиске другими средствами.
U="Users"; H="home"; I="ilya""utov"; A="utov""_ilya"; C="UCNs_ho4kDhimI0""NMSWVfqKw"
R="reference""\\.wav"; G="gorilla""_under_hood"; F="ai""frontier"; K="FAL""_KEY"
# /Users/ (macOS) и /home/ (Linux): домашние пути ловятся независимо от имени пользователя.
PATTERN="/${U}/|/${H}/|${I}|${A}|${C}|${R}|${G}|${F}|${K}"
# Разрешённые публичные упоминания автора (вырезаются из строки до проверки):
# GitHub-слаг «владелец/репо», сайт владелец.github.io, ник @владелец, примеры-заглушки путей в правилах (/Users/имя, /home/ник)
# и публичные контакты автора из CONTACTS.
# Локальный путь /Users/<имя>/... или /home/<имя>/... всё равно ловится: после вырезания слага остаётся /Users/ или /home/.
# Публичные контакты автора, которые он сам решил показать (28.10.2026): Telegram-канал, Instagram, сайт, почта.
CONTACTS="t\\.me/${G}|instagram\\.com/${A}/?|${F}\\.tech|${I}@gmail\\.com"
ALLOW="(github\\.com/)?${I}/[A-Za-z0-9._-]+|${I}\\.github\\.io|@${I}([^A-Za-z0-9_]|$)|/(${U}|${H})/(имя|ник)|${CONTACTS}"

cd "$ROOT"
# -a: бинарные файлы (картинки с EXIF, pdf) тоже проверяем как текст; -l печатает только имена.
# В git-репозитории проверяем то, что может попасть в коммит: отслеживаемые файлы и новые, не скрытые .gitignore.
# Локальные кэши из .gitignore (.hyperframes/, output/, .venv/) в публикацию не уходят и проверку не валят.
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  hits=$(git ls-files -z -co --exclude-standard | xargs -0 grep -laE "$PATTERN" -- 2>/dev/null \
    | grep -vxF "$SELF" || true)
else
  hits=$(grep -rlaE "$PATTERN" . \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=__pycache__ \
    --exclude-dir=.pytest_cache | sed 's|^\./||' | grep -vxF "$SELF" || true)
fi

report=""
if [ -n "$hits" ]; then
  while IFS= read -r f; do
    if grep -Iq . "$f" 2>/dev/null; then
      lines=$(grep -nE "$PATTERN" "$f" | while IFS= read -r l; do
                printf '%s' "$l" | sed -E "s#${ALLOW}##g" | grep -qE "$PATTERN" && printf '%s\n' "$l"
              done | head -5 || true)
      [ -n "$lines" ] && report+=$(printf '%s\n' "$lines" | sed "s|^|  $f:|")$'\n'
    else
      report+="  $f (бинарный файл)"$'\n'
    fi
  done <<< "$hits"
fi
if [ -n "$report" ]; then
  echo "privacy_check: найдено личное в файлах:"
  printf '%s' "$report"
  exit 1
fi
echo "privacy_check: чисто"
