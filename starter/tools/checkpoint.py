#!/usr/bin/env python3
"""Private local snapshots. Stop the build before save/restore; no pipeline transaction."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).absolute().parents[1]
STORE = ROOT / '.checkpoints'
DIRECTORIES = {'.agents', 'assets', 'scene', 'tools', 'voice', 'examples', 'data', 'build', 'output', 'qa'}
EXCLUDED = {'node_modules', '.git', '.runtime', '.venv', 'venv', 'env', '__pycache__',
            'cache', '.cache', 'models', 'model', 'weights', 'profile', 'profiles',
            'browser-profile', 'browser-profiles', '.checkpoints', 'secrets', 'credentials'}
EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.mjs', '.json', '.md', '.txt', '.csv', '.tsv',
              '.html', '.css', '.sh', '.yaml', '.yml', '.toml', '.wav', '.m4a', '.mp3', '.aac',
              '.flac', '.ogg', '.mp4', '.mov', '.png', '.jpg', '.jpeg', '.webp', '.svg',
              '.woff', '.woff2', '.ttf', '.otf', '.srt', '.vtt'}
SPECIAL = {'LICENSE', '.gitignore', '.keep'}
MAX_FILES = 100000
MAX_BYTES = 64 * 1024 ** 3
CHUNK = 1024 * 1024
ENTRY = ('make.sh', 'tools/checkpoint.py')   # CLI возврата: заменяются последними и никогда не удаляются


def fail(message):
    raise ValueError(message)


def safe_name(name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', name):
        fail('Имя: 1–80 латинских букв, цифр, _ или -, первый символ буква/цифра')
    return name


def safe_path(name):
    p = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or p.is_absolute() or p.as_posix() != name:
        fail(f'Небезопасный путь: {name!r}')
    if any(part in {'.', '..', ''} for part in p.parts):
        fail(f'Небезопасный путь: {name!r}')
    return p


def allowed(name, directory=False):
    p = safe_path(name)
    if any(part.lower() in EXCLUDED or part.startswith('.env') for part in p.parts):
        return False
    if len(p.parts) > 1 or directory:
        if p.parts[0] not in DIRECTORIES:
            return False
    return directory or p.suffix.lower() in EXTENSIONS or p.name in SPECIAL


def no_links(path):
    """Check every existing component without following directory symlinks."""
    relative = path.relative_to(ROOT)
    current = ROOT
    for component in relative.parts:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            fail(f'Симлинк запрещён во включаемом пути: {current.relative_to(ROOT)}')


def inventory():
    result = []

    def visit(directory):
        for path in sorted(directory.iterdir()):
            name = path.relative_to(ROOT).as_posix()
            # Excluded directories are never traversed, including excluded symlinks.
            if any(p.lower() in EXCLUDED or p.startswith('.env') for p in path.relative_to(ROOT).parts):
                continue
            mode = path.lstat().st_mode
            candidate_dir = len(path.relative_to(ROOT).parts) == 1 and path.name in DIRECTORIES
            if stat.S_ISLNK(mode):
                if candidate_dir or allowed(name) or (directory != ROOT and allowed(name, directory=True)):
                    fail(f'Симлинк запрещён во включаемом пути: {name}')
                continue
            if stat.S_ISDIR(mode):
                if allowed(name, directory=True): visit(path)
            elif allowed(name):
                if not stat.S_ISREG(mode): fail(f'Ожидался обычный файл: {name}')
                result.append(path)

    visit(ROOT)
    return result


@contextmanager
def private_store():
    no_links(STORE)
    STORE.mkdir(mode=0o700, exist_ok=True)
    os.chmod(STORE, 0o700)
    lock = STORE / '.lock'
    no_links(lock)
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def save(name, paths=None):
    safe_name(name)
    target = STORE / (name + '.zip')
    if target.exists() or target.is_symlink(): fail(f'Копия уже существует: {name}')
    paths = inventory() if paths is None else paths
    if len(paths) > MAX_FILES: fail('Слишком много файлов')
    fd, temporary = tempfile.mkstemp(prefix='.save-', dir=STORE)
    os.close(fd)
    try:
        manifest = {'schema': 1, 'kind': 'reel-starter-checkpoint',
                    'created_utc': datetime.now(timezone.utc).isoformat(), 'files': []}
        total = 0
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            for path in paths:
                no_links(path)
                source = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(source, 'rb') as stream:
                    metadata = os.fstat(stream.fileno())
                    if not stat.S_ISREG(metadata.st_mode): fail('Ожидался обычный файл')
                    name_in_root = path.relative_to(ROOT).as_posix()
                    digest = hashlib.sha256(); size = 0
                    with archive.open('files/' + name_in_root, 'w', force_zip64=True) as dest:
                        while data := stream.read(CHUNK):
                            size += len(data); total += len(data)
                            if total > MAX_BYTES: fail('Контрольная копия превышает 64 GiB')
                            digest.update(data); dest.write(data)
                    after = os.fstat(stream.fileno())
                    if (metadata.st_size, metadata.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                        fail('Файл изменился во время копирования; остановите сборку и повторите')
                    manifest['files'].append({'path': name_in_root, 'size': size,
                        'sha256': digest.hexdigest(), 'mode': 0o755 if metadata.st_mode & 0o111 else 0o644})
            archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        # No overwrite of an existing checkpoint, including concurrent writers.
        os.link(temporary, target)
        os.chmod(target, 0o600)
    finally:
        os.unlink(temporary)
    print(f'Сохранено: {name} ({len(paths)} файлов). Приватный архив .checkpoints/{name}.zip')
    return name


def read_manifest(archive):
    infos = archive.infolist()
    if len(infos) > MAX_FILES + 1: fail('Слишком много записей ZIP')
    names = [info.filename for info in infos]
    names_set = set(names)
    if len(names) != len(names_set): fail('Повторяющиеся пути в ZIP')
    if 'manifest.json' not in names_set: fail('Нет manifest.json')
    if archive.getinfo('manifest.json').file_size > 16 * 1024 ** 2: fail('Манифест слишком велик')
    for info in infos:
        safe_path(info.filename)
        mode = info.external_attr >> 16
        if info.is_dir() or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in {0, stat.S_IFREG}):
            fail('ZIP содержит не обычный файл')
    manifest = json.loads(archive.read('manifest.json'))
    if not isinstance(manifest, dict) or set(manifest) != {'schema', 'kind', 'created_utc', 'files'}:
        fail('Неверная схема манифеста')
    if type(manifest['schema']) is not int or manifest['schema'] != 1 or manifest['kind'] != 'reel-starter-checkpoint':
        fail('Неизвестная версия/тип контрольной копии')
    if not isinstance(manifest['created_utc'], str) or not isinstance(manifest['files'], list):
        fail('Неверные поля манифеста')
    expected = {'manifest.json'}; total = 0; paths = set()
    for entry in manifest['files']:
        if not isinstance(entry, dict) or set(entry) != {'path', 'size', 'sha256', 'mode'}:
            fail('Неверная запись манифеста')
        path = entry['path']
        if not isinstance(path, str) or not allowed(path): fail('Запрещённый путь в манифесте')
        if path in paths: fail('Повторяющийся файл в манифесте')
        paths.add(path)
        if type(entry['size']) is not int or entry['size'] < 0 or type(entry['mode']) is not int or entry['mode'] not in {0o644, 0o755}:
            fail('Неверный размер или режим файла')
        if not isinstance(entry['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', entry['sha256']):
            fail('Неверный SHA256')
        member = 'files/' + path; expected.add(member); total += entry['size']
        if member not in names_set or archive.getinfo(member).file_size != entry['size']: fail('Размер/состав ZIP не совпадает')
    if expected != names_set or total > MAX_BYTES: fail('Лишние записи ZIP или превышен лимит 64 GiB')
    if not set(ENTRY).issubset(paths):
        fail('В копии отсутствуют make.sh/tools/checkpoint.py: после возврата нужен рабочий CLI')
    for name in paths:
        if any(parent.as_posix() in paths for parent in PurePosixPath(name).parents if parent.as_posix() != '.'):
            fail('Конфликт файла и каталога в манифесте')
    return manifest, total


def restore(name):
    safe_name(name)
    source = STORE / (name + '.zip'); no_links(source)
    current = inventory()  # Fail closed before staging, backup or any replacement.
    with zipfile.ZipFile(source) as archive, tempfile.TemporaryDirectory(prefix='.restore-', dir=STORE) as temporary:
        manifest, total = read_manifest(archive)
        if shutil.disk_usage(STORE).free < total: fail('Недостаточно места для проверки копии')
        stage = Path(temporary)
        for entry in manifest['files']:
            relative = entry['path']; destination = ROOT / relative; no_links(destination)
            if destination.exists() and destination.is_dir(): fail(f'Вместо файла существует каталог: {relative}')
            for parent in destination.parents:
                if parent == ROOT: break
                if parent.exists() and not parent.is_dir(): fail(f'Вместо каталога существует файл: {relative}')
            staged = stage / relative; staged.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            # The filesystem decides case/Unicode aliases; never overwrite a staged file.
            with archive.open('files/' + relative) as stream, staged.open('xb') as dest:
                while data := stream.read(CHUNK): digest.update(data); dest.write(data)
            if staged.stat().st_size != entry['size'] or digest.hexdigest() != entry['sha256']:
                fail(f'SHA256 не совпадает: {relative}')
            os.chmod(staged, entry['mode'])
        insurance = 'before-restore-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
        save(insurance, current)  # A successful insurance archive is required before mutation.
        print(f'Страховочная копия: {insurance}', flush=True)
        # Порядок на случай прерывания: сначала поверх (os.replace атомарен на файл), CLI возврата последним,
        # лишние файлы удаляются в самом конце. make.sh и tools/checkpoint.py всё время на месте.
        restored, inodes = {entry['path'] for entry in manifest['files']}, set()
        for relative in sorted(restored, key=lambda r: r in ENTRY):
            destination = ROOT / relative; no_links(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage / relative, destination)
            st = destination.stat(); inodes.add((st.st_dev, st.st_ino))
        for path in current:   # inode: на регистронезависимом диске A.ts и a.ts — один и тот же восстановленный файл
            no_links(path); st = path.lstat() if path.exists() else None
            if st and path.relative_to(ROOT).as_posix() not in restored and (st.st_dev, st.st_ino) not in inodes: path.unlink()
    print(f'Восстановлено: {name}. При прерывании верните {insurance}; автоматической транзакции нет.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['save', 'list', 'restore'])
    parser.add_argument('name', nargs='?')
    args = parser.parse_args()
    if (args.action == 'list') != (args.name is None): parser.error('save/restore требуют NAME; list без NAME')
    try:
        with private_store():
            if args.action == 'save': save(args.name)
            elif args.action == 'restore': restore(args.name)
            else:
                for path in sorted(STORE.glob('*.zip')):
                    safe_name(path.stem); no_links(path)
                    with zipfile.ZipFile(path) as archive:
                        manifest, total = read_manifest(archive)
                    print(f'{path.stem}\t{len(manifest["files"])} файлов\t{total} байт\t{manifest["created_utc"]}')
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as error:
        parser.exit(1, f'checkpoint: {error}\n')


if __name__ == '__main__': main()
