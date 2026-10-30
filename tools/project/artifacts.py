#!/usr/bin/env python3
"""ARTIFACTS.json: паспорт поставки ролика со статусом и sha256 каждого файла.

Что делает: собирает список файлов проекта (по умолчанию — то, что производит starter/:
финальное видео, мастер звука, отчёт QA, story.json, voice-track.json, reel.json, контактный
лист), считает размер и sha256 каждого и пишет ARTIFACTS.json. Статус берётся из
qa/final-result.json (поле status), если файл есть. Публикацию утилита не делает и не
отмечает: поле publication всегда "not published", решение остаётся за человеком.

Шаблоны --include — пути относительно проекта, можно с * и **. Явный путь без * обязан
существовать, иначе понятная ошибка и код 2. Шаблон с * без совпадений тоже ошибка
(если не указан --allow-missing). Пути вне папки проекта (абсолютные, через ..) не принимаются: код 2.

Вход: папка проекта. Выход: <проект>/ARTIFACTS.json (или --out), строка-сводка.
Код возврата: 0; 2, если обязательного файла нет.

Пример:
  python3 tools/project/artifacts.py starter
  python3 tools/project/artifacts.py my-reel --include output/final.mp4 "assets/audio/*.wav" qa/final-result.json
"""
import argparse
import glob
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

DEFAULT_FILES = ['output/final.mp4', 'assets/audio/master.wav', 'qa/final-result.json', 'story.json',
                 'voice-track.json', 'reel.json', 'qa/sheet.jpg']


class MissingFile(Exception):
    pass


class OutsideRoot(Exception):
    pass


def inside(root, p):
    """Файл лежит внутри проекта (после разрешения .. и симлинков)."""
    try:
        return Path(p).resolve().relative_to(root) is not None
    except ValueError:
        return False


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def collect(root, patterns, allow_missing=False):
    root = Path(root).resolve()
    files, missing = [], []
    for pat in patterns:
        if Path(pat).is_absolute() or not inside(root, root / pat.split('*')[0]):
            raise OutsideRoot(f'вне проекта: {pat}' if not Path(pat).is_absolute() else 'вне проекта: абсолютный путь')
        if any(c in pat for c in '*?['):
            hits = sorted(Path(p) for p in glob.glob(str(root / pat), recursive=True) if Path(p).is_file())
            if not hits:
                missing.append(pat)
            files += hits
        else:
            p = root / pat
            (files if p.is_file() else missing).append(p if p.is_file() else pat)
    outside = [p for p in files if not inside(root, p)]
    if outside:
        raise OutsideRoot('вне проекта: ' + ', '.join(str(p.relative_to(root)) if inside(root, p) else '..' for p in outside))
    if missing and not allow_missing:
        raise MissingFile('нет файлов: ' + ', '.join(missing))
    seen, out = set(), []
    for p in files:
        if p not in seen:
            seen.add(p); out.append(p)
    return root, out, missing


def build(root, patterns=None, allow_missing=False):
    root, files, missing = collect(root, patterns or DEFAULT_FILES, allow_missing)
    res = root / 'qa' / 'final-result.json'
    result = json.loads(res.read_text()) if res.is_file() else {}
    return {'date': date.today().isoformat(), 'status': result.get('status', 'unknown'),
            'technical_pass': result.get('technical_pass'), 'publication': 'not published',
            'missing': missing,
            'artifacts': [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in files]}


def main(argv=None):
    ap = argparse.ArgumentParser(description='ARTIFACTS.json со статусом и sha256 поставки.')
    ap.add_argument('project', type=Path)
    ap.add_argument('--include', nargs='+', help='шаблоны путей (по умолчанию набор starter/)')
    ap.add_argument('--allow-missing', action='store_true', help='не падать на отсутствующих файлах')
    ap.add_argument('--out', type=Path, help='куда писать (по умолчанию <проект>/ARTIFACTS.json)')
    a = ap.parse_args(argv)
    try:
        out = build(a.project, a.include, a.allow_missing)
    except (MissingFile, OutsideRoot) as e:
        print(f'ошибка: {e}', file=sys.stderr)
        return 2
    dst = a.out or a.project / 'ARTIFACTS.json'
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(f"{a.project.resolve().name}: статус {out['status']}, файлов {len(out['artifacts'])} → {dst}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
