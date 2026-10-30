"""Проверка окружения без загрузки TTS/ASR-моделей и без изменения файлов."""
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

P = Path(__file__).resolve().parents[1]


def inspect(voice=False):
    checks = []
    def add(name, ok, detail, fix='', warn=False):
        checks.append({'name': name, 'ok': bool(ok), 'detail': str(detail), 'fix': fix, 'warn': bool(warn)})
    add('Python', sys.version_info[:2] == (3, 11), sys.version.split()[0], 'Используйте Python 3.11 и новый .venv.')
    for name in ['node', 'ffmpeg', 'ffprobe']:
        binary = shutil.which(name)
        add(name, binary is not None, binary or 'не найден', 'Установите системные зависимости из README.')
    if shutil.which('node'):
        ver = subprocess.check_output(['node', '--version'], text=True).strip()
        add('Node >=18', int(ver.lstrip('v').split('.')[0]) >= 18, ver)
    tsc = os.environ.get('TSC') or str(P / 'node_modules/.bin/tsc')   # make.sh берёт тот же $TSC
    add('TypeScript', Path(tsc).is_file(), tsc, 'Выполните npm ci или задайте TSC=/путь/к/tsc.')
    fonts = [f for f in (P / 'assets/fonts').glob('*.woff2')]
    add('Шрифты', bool(fonts), f'{len(fonts)} woff2 в assets/fonts' if fonts else 'assets/fonts пуста, сцена рисует запасными',
        './make.sh fonts', warn=True)
    for name, mod, optional in [('numpy', 'numpy', False), ('scipy', 'scipy', False), ('soundfile', 'soundfile', False),
                                ('pillow', 'PIL', False), ('playwright', 'playwright', False), ('faster-whisper', 'faster_whisper', True)]:
        try:
            importlib.import_module(mod)
            add(name, True, importlib.metadata.version(name))
        except (ImportError, OSError, importlib.metadata.PackageNotFoundError) as e:
            add(name, False, f'{e}; не нужен для fake и --no-asr' if optional else e,
                'Выполните .venv/bin/python -m pip install -r requirements.txt.', warn=optional)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True); b.close()
        add('Chromium', True, 'headless запуск выполнен')
    except Exception as e:
        deps = ' --with-deps' if sys.platform.startswith('linux') else ''   # на чистом Linux без системных библиотек Chromium не стартует
        add('Chromium', False, e, f'Выполните .venv/bin/python -m playwright install{deps} chromium.')
    if voice:
        for name in ['OMNI_PY', 'OMNI_MODEL', 'OMNI_REF']:
            v = os.environ.get(name, '')
            add(name, bool(v) and Path(v).exists(), 'задан и существует' if v and Path(v).exists() else 'не задан или путь отсутствует',
                'См. README, раздел OmniVoice.')
        ref = os.environ.get('OMNI_REF')
        if ref:
            add('Расшифровка референса', Path(ref).with_suffix('.txt').is_file(), 'TXT рядом с WAV', 'Запишите точную расшифровку в .txt.')
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--voice', action='store_true'); ap.add_argument('--json', action='store_true'); a = ap.parse_args()
    checks = inspect(a.voice); ok = all(c['ok'] or c['warn'] for c in checks)   # WARN не валит doctor
    if a.json: print(json.dumps({'ok': ok, 'checks': checks}, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(('OK  ' if c['ok'] else 'WARN' if c['warn'] else 'FAIL') + f" {c['name']}: {c['detail']}")
            if not c['ok'] and c['fix']: print('     ' + c['fix'])
        print('WARN не мешает fake-прогону. Модели ASR/TTS эта команда не скачивает.')
    return 0 if ok else 1


if __name__ == '__main__': sys.exit(main())
