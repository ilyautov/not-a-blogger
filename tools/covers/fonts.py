# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Поиск свободного шрифта по имени среди установленных в системе.

Файлы шрифтов в репозиторий не кладём. Pillow нужен путь к файлу, поэтому ищем по имени
в стандартных папках: сначала Inter, потом Noto Sans (оба под SIL Open Font License).
Свой файл можно передать явно (--font). Если их нет, берётся системный sans (fc-match),
в последнюю очередь встроенный шрифт Pillow, в нём нет кириллицы: будут квадраты, и об этом печатается предупреждение.

Где скачать: Inter https://rsms.me/inter/ или https://fonts.google.com/specimen/Inter,
Noto Sans https://fonts.google.com/noto/specimen/Noto+Sans.
"""
import argparse
import os
import sys
from pathlib import Path

FAMILIES = ('Inter', 'Noto Sans')
DIRS = [
    '~/Library/Fonts', '/Library/Fonts', '/System/Library/Fonts', '/System/Library/Fonts/Supplemental',
    '~/.local/share/fonts', '~/.fonts', '/usr/share/fonts', '/usr/local/share/fonts',
    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
]
EXT = ('.ttf', '.otf', '.ttc')
_cache = {}


def _candidates():
    if 'files' not in _cache:
        files = []
        for d in DIRS:
            p = Path(os.path.expanduser(d))
            if p.is_dir():
                try:
                    files += [f for f in p.rglob('*') if f.suffix.lower() in EXT]
                except OSError:
                    pass
        _cache['files'] = files
    return _cache['files']


WEIGHTS = ('thin', 'light', 'regular', 'medium', 'semibold', 'bold', 'extrabold', 'black', 'variable')


def _is_family(stem, key):
    """Точное семейство: «Inter-Bold», «Inter[opsz,wght]», «NotoSans-Regular», но не «NotoSansOriya»."""
    s = stem.lower().replace(' ', '')
    if 'italic' in s or not s.startswith(key):
        return False
    rest = s[len(key):]
    return rest == '' or rest[0] in '-_[' or rest.startswith(WEIGHTS)


def system_fallback(bold=True):
    """Системный sans через fontconfig (fc-match), если OFL-шрифты не установлены."""
    import shutil
    import subprocess
    if shutil.which('fc-match'):
        r = subprocess.run(['fc-match', '-f', '%{file}', 'sans-serif:bold' if bold else 'sans-serif'],
                           capture_output=True, text=True)
        if r.returncode == 0 and Path(r.stdout).is_file():
            return r.stdout
    for p in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(p).is_file():
            return p
    return None


def find_font(families=FAMILIES, bold=True):
    """Путь к файлу первого найденного семейства или None."""
    files = _candidates()
    for fam in families:
        key = fam.lower().replace(' ', '')
        hits = [f for f in files if _is_family(f.stem, key)]
        if not hits:
            continue

        def score(f):
            s = f.stem.lower()
            if bold:
                return (0 if 'bold' in s and 'extra' not in s and 'semi' not in s else 1 if 'bold' in s else 2, len(s))
            return (0 if 'regular' in s else 1 if not any(w in s for w in ('bold', 'light', 'thin', 'black', 'medium')) else 2, len(s))
        return str(sorted(hits, key=score)[0])
    return None


def load(size, bold=True, path=None):
    """ImageFont нужного кегля: явный путь, Inter/Noto Sans, системный sans, встроенный."""
    from PIL import ImageFont
    path = path or find_font(bold=bold)
    if not path:
        path = system_fallback(bold)
        if path and not _cache.get('fb'):
            print(f'Inter / Noto Sans не установлены, беру системный {path}; см. README', file=sys.stderr)
            _cache['fb'] = True
    if path:
        f = ImageFont.truetype(path, size)
        try:  # вариативный шрифт: выставляем начертание
            f.set_variation_by_name('Bold' if bold else 'Regular')
        except Exception:
            pass
        return f
    if not _cache.get('warned'):
        print('шрифт Inter / Noto Sans не найден, кириллица может стать квадратами; см. README', file=sys.stderr)
        _cache['warned'] = True
    try:
        return ImageFont.load_default(size)
    except TypeError:  # старый Pillow
        return ImageFont.load_default()


def main(argv=None):
    ap = argparse.ArgumentParser(description='Найти установленный Inter / Noto Sans (библиотечный модуль для overlay.py и cover.py).')
    ap.add_argument('--regular', action='store_true', help='искать обычное начертание вместо жирного')
    a = ap.parse_args(argv)
    path = find_font(bold=not a.regular) or system_fallback(not a.regular)
    print(path or 'шрифт не найден; см. README')
    return 0 if path else 1


if __name__ == '__main__':
    sys.exit(main())
