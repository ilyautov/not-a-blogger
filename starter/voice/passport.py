"""Паспорт исходного дубля: voice/raw-N.json рядом с raw-N.wav — точный текст, движок, настройки, sha256.
Пишут gen_omni.py, examples/.../gen_design.py и import_live.py. trim.py не берёт дубль, который разошёлся
с паспортом (файл подменён) или с текстом реплики в chunks.json (текст переписан, а звук старый)."""
import hashlib, json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(wav, text, engine, settings):
    wav = Path(wav)
    wav.with_suffix('.json').write_text(json.dumps({'text': text, 'engine': engine, 'settings': settings, 'sha256': sha256(wav)},
                                                   ensure_ascii=False, indent=1) + '\n')


def check(wav, text):
    """Строка с причиной, если дубль нельзя брать; None, если дубль, паспорт и текст сходятся."""
    wav = Path(wav); pas = wav.with_suffix('.json')
    if not wav.exists(): return f'нет {wav.name}'
    if not pas.exists(): return f'нет паспорта {pas.name}: дубль сделан не через make.sh voice/live, пересинтезируйте или импортируйте заново'
    try: d = json.loads(pas.read_text())
    except ValueError: return f'паспорт {pas.name} не читается'
    if d.get('sha256') != sha256(wav): return f'{wav.name} изменён после синтеза/импорта: sha256 не совпадает с {pas.name}'
    if d.get('text') != text: return f'текст реплики в chunks.json изменился после {wav.name}: пересинтезируйте или перезапишите эту реплику'
    return None
