"""Своя начитка: один файл на реплику, в порядке chunks.json. Затем запустить trim.py.
Рядом с каждым raw-N.wav пишется паспорт raw-N.json (voice/passport.py): текст, движок live, имя исходника, sha256."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import passport  # noqa: E402

P = Path(__file__).resolve().parents[1]


def import_recordings(root, recordings):
    root = Path(root)
    chunks_path = root / 'voice/chunks.json'
    chunks = json.loads(chunks_path.read_text())
    sources = [Path(p).resolve() for p in recordings]
    if len(sources) != len(chunks):
        raise ValueError(f'Нужно файлов: {len(chunks)}, получено: {len(sources)}. Один файл на реплику.')
    for src in sources:
        if not src.is_file(): raise ValueError(f'Нет записи: {src}')
        if src in [(root / f'voice/raw-{i}.wav').resolve() for i in range(len(chunks))]:
            raise ValueError('Исходник не должен называться raw-N.wav: сохраните запись как my-N.wav')
    # Сначала декодировать все записи. Не оставлять половину новых raw-файлов при битом входе.
    with tempfile.TemporaryDirectory(prefix='live-', dir=root / 'voice') as d:
        for i, src in enumerate(sources):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vn', '-ar', '24000', '-ac', '1',
                            str(Path(d) / f'raw-{i}.wav')], check=True)
        for i, ch in enumerate(chunks):
            (Path(d) / f'raw-{i}.wav').replace(root / f'voice/raw-{i}.wav')
            ch['engine'] = 'live'; ch['tail'] = False
            passport.write(root / f'voice/raw-{i}.wav', ch['text'], 'live', {'source': sources[i].name, 'sr': 24000, 'tail': False})
            ch.pop('omni_speed', None)
    chunks_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=1) + '\n')
    print(f'Импортировано реплик: {len(chunks)}. Далее: voice/trim.py → make.sh all')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('recordings', nargs='+', help='WAV/M4A, по одному на реплику')
    a = ap.parse_args()
    try: import_recordings(P, a.recordings)
    except (ValueError, subprocess.CalledProcessError) as e: ap.exit(1, f'Начитка: {e}\n')


if __name__ == '__main__': main()
