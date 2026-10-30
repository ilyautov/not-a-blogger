"""starter: порог ASR на каждый дубль, нормализация любой письменности, паспорт дубля, порядок checkpoint restore."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

from conftest import ROOT

ST = ROOT / 'starter'


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ST / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fin = load('tools/finish.py', 'starter_finish')
trim = load('voice/trim.py', 'starter_trim')
passport = load('voice/passport.py', 'starter_passport')
cp = load('tools/checkpoint.py', 'starter_checkpoint')


def _takes(root, ratios, texts=None):
    texts = texts or [f'Реплика номер {i}' for i in range(len(ratios))]
    (root / 'voice').mkdir(parents=True, exist_ok=True)
    (root / 'voice/chunks.json').write_text(json.dumps([{'text': t, 'pause': .1} for t in texts], ensure_ascii=False))
    for i, (t, r) in enumerate(zip(texts, ratios)):
        wav = root / f'voice/line-{i}.wav'; wav.write_bytes(f'take {i}'.encode())
        (root / f'voice/asr-{i}.json').write_text(json.dumps({'text': t, 'ratio': r, 'line_sha256': hashlib.sha256(wav.read_bytes()).hexdigest()},
                                                             ensure_ascii=False))
    return texts


def test_one_take_below_threshold_fails_whole_video(tmp_path):
    _takes(tmp_path, [.97, .62, 1.0])
    ok, detail = fin.takes_asr(tmp_path)
    assert ok is False and detail['below_0_9'] == [{'line': 1, 'ratio': .62}]
    assert fin.verdict({'loudness': True, 'asr_ge_0_9': True, 'takes_asr_ge_0_9': ok}, False) == 'technical_failed'


def test_all_takes_pass(tmp_path):
    _takes(tmp_path, [.95, .91])
    assert fin.takes_asr(tmp_path) == (True, {'below_0_9': [], 'missing_or_stale': []})
    assert fin.verdict({'asr_ge_0_9': True, 'takes_asr_ge_0_9': True}, False) == 'ready_for_user_preview'


def test_missing_take_result_is_partial(tmp_path):
    _takes(tmp_path, [.95, .95])
    (tmp_path / 'voice/asr-1.json').unlink()
    ok, detail = fin.takes_asr(tmp_path)
    assert ok is None and detail['missing_or_stale'] == [1]
    assert fin.verdict({'asr_ge_0_9': True, 'takes_asr_ge_0_9': ok}, False) == 'preview_partial'


def test_stale_take_result_cannot_pass(tmp_path):
    texts = _takes(tmp_path, [.99, .99])
    chunks = json.loads((tmp_path / 'voice/chunks.json').read_text())
    chunks[0]['text'] = texts[0] + ' и ещё слово'                     # текст переписан, trim не перезапущен
    (tmp_path / 'voice/chunks.json').write_text(json.dumps(chunks, ensure_ascii=False))
    (tmp_path / 'voice/line-1.wav').write_bytes(b'other audio')       # дубль заменён после trim
    ok, detail = fin.takes_asr(tmp_path)
    assert ok is None and detail['missing_or_stale'] == [0, 1]


def test_fake_track_is_partial_even_if_checks_green():
    assert fin.verdict({'asr_ge_0_9': True, 'takes_asr_ge_0_9': True}, True) == 'preview_partial'


def test_empty_normalisation_never_passes():
    assert fin.ratio('— … !!!', '— … !!!') == 0.0
    assert fin.ratio('Раз два', '') == 0.0 and fin.ratio('', 'раз два') == 0.0
    assert trim.match_ratio('—', ['—']) == 0.0
    assert trim.match_ratio('Раз два', []) == 0.0


def test_non_latin_scripts_normalise_non_empty():
    for s in ('Ελληνικά', 'नमस्ते', 'עברית', 'مرحبا', 'Привет'):
        assert trim.norm(s), s
        assert fin.words(s), s
    assert fin.words('नमस्ते दुनिया!') == ['नमस्ते', 'दुनिया']
    assert fin.ratio('Καλημέρα κόσμε', 'καλημέρα, κόσμε.') == 1.0
    assert trim.match_ratio('Привет, мир!', ['привет', 'мир']) == 1.0
    assert trim.norm('Ёж') == trim.norm('е́ж') == 'еж'
    assert fin.words('Mi-Box за 200') == ['mi', 'box', 'за', 'двести']


def test_passport_catches_changed_text_and_audio(tmp_path):
    wav = tmp_path / 'raw-0.wav'; wav.write_bytes(b'RIFF take')
    assert 'нет паспорта' in passport.check(wav, 'Раз два')
    passport.write(wav, 'Раз два', 'live', {'source': 'my-0.m4a'})
    meta = json.loads(wav.with_suffix('.json').read_text())
    assert meta['engine'] == 'live' and meta['sha256'] == hashlib.sha256(b'RIFF take').hexdigest()
    assert passport.check(wav, 'Раз два') is None
    assert 'текст реплики' in passport.check(wav, 'Раз три')
    wav.write_bytes(b'RIFF other')
    assert 'sha256' in passport.check(wav, 'Раз два')


def test_checkpoint_restore_keeps_cli_until_last(tmp_path, monkeypatch):
    root = tmp_path / 'starter'
    for rel, body in {'make.sh': 'old make', 'tools/checkpoint.py': 'old cp', 'scene/a.ts': 'v1', 'voice/chunks.json': '[]'}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True); (root / rel).write_text(body)
    monkeypatch.setattr(cp, 'ROOT', root); monkeypatch.setattr(cp, 'STORE', root / '.checkpoints')
    cp.STORE.mkdir()
    cp.save('snap')
    (root / 'scene/a.ts').write_text('v2'); (root / 'scene/extra.ts').write_text('new'); (root / 'make.sh').write_text('new make')
    log, real_replace, real_unlink = [], os.replace, Path.unlink
    monkeypatch.setattr(cp.os, 'replace', lambda a, b: (log.append(('replace', Path(b).relative_to(root).as_posix())), real_replace(a, b))[1])
    monkeypatch.setattr(Path, 'unlink', lambda self, *a, **k: (log.append(('unlink', self.name)), real_unlink(self, *a, **k))[1])
    cp.restore('snap')
    assert (root / 'scene/a.ts').read_text() == 'v1' and (root / 'make.sh').read_text() == 'old make'
    assert not (root / 'scene/extra.ts').exists()
    replaced = [p for op, p in log if op == 'replace']
    assert set(replaced[-2:]) == {'make.sh', 'tools/checkpoint.py'}
    assert log.index(('unlink', 'extra.ts')) > max(i for i, (op, _) in enumerate(log) if op == 'replace')
    assert ('unlink', 'make.sh') not in log and ('unlink', 'checkpoint.py') not in log
    assert any(p.name.startswith('before-restore-') for p in cp.STORE.glob('*.zip'))
