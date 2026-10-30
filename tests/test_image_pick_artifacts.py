"""depth_layers на синтетической карте глубины, depth (skip без весов), pick_take, artifacts."""
import hashlib
import json
import shutil
import subprocess

import numpy as np
import pytest

from conftest import load

lay = load('image', 'depth_layers')
pick = load('voice', 'pick_take')
art = load('project', 'artifacts')


# ---------- depth_layers ----------
def _bands(h=240, w=320):
    depth = np.zeros((h, w), np.uint8)
    depth[:, :w // 3] = 30
    depth[:, w // 3:2 * w // 3] = 128
    depth[:, 2 * w // 3:] = 220
    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, (h, w, 3), dtype=np.uint8)
    return img, depth


def test_three_bands_three_layers():
    img, depth = _bands()
    layers = lay.make_layers(img, depth, cuts=[85, 170])
    assert len(layers) == 3
    far = layers[0][0]
    assert far.shape == (240, 320, 4)
    assert (far[..., 3] == 255).all()                     # у дальнего слоя дыр нет
    covers = [c for _, c in layers]
    assert all(25 <= c <= 40 for c in covers), covers
    near = layers[2][0]
    assert near[120, 300, 3] > 200 and near[120, 10, 3] == 0


def test_layers_cli(tmp_path):
    import cv2
    img, depth = _bands()
    cv2.imwrite(str(tmp_path / 'a.png'), img)
    cv2.imwrite(str(tmp_path / 'a.depth.png'), depth)
    assert lay.main([str(tmp_path / 'a.png'), '--cuts', '85', '170', '--out-dir', str(tmp_path / 'L')]) == 0
    assert sorted(p.name for p in (tmp_path / 'L').iterdir()) == ['a.L0.png', 'a.L1.png', 'a.L2.png']


def test_layers_reject_depth_map_with_other_aspect(tmp_path):
    import cv2
    img, depth = _bands()
    with pytest.raises(ValueError, match='пропорци'):
        lay.make_layers(img, depth[:, :160], cuts=[85, 170])
    # та же пропорция, меньший размер — это просто даунскейл карты, его масштабируем
    small = cv2.resize(depth, (160, 120), interpolation=cv2.INTER_NEAREST)
    assert len(lay.make_layers(img, small, cuts=[85, 170])) == 3
    cv2.imwrite(str(tmp_path / 'a.png'), img)
    cv2.imwrite(str(tmp_path / 'a.depth.png'), depth[:, :160])
    with pytest.raises(SystemExit) as e:
        lay.main([str(tmp_path / 'a.png')])
    assert 'пропорци' in str(e.value)


def test_depth_load_image_applies_exif_orientation(tmp_path):
    from PIL import Image
    depth = load('image', 'depth')
    im = Image.fromarray(np.zeros((40, 100, 3), np.uint8))
    exif = Image.Exif()
    exif[0x0112] = 6                              # телефонный JPEG: повернуть на 90°
    p = tmp_path / 'phone.jpg'
    im.save(p, exif=exif)
    assert Image.open(p).size == (100, 40)
    assert depth.load_image(p).size == (40, 100)   # как видит cv2.imread в depth_layers


def test_depth_normalize():
    depth = load('image', 'depth')
    d = depth.normalize(np.array([[1.0, 2.0], [3.0, 5.0]]))
    assert d.min() == 0 and d.max() == 255 and d.dtype == np.uint8
    assert (depth.normalize(np.ones((2, 2))) == 0).all()


@pytest.mark.slow
def test_depth_model_smoke(tmp_path):
    depth = load('image', 'depth')
    try:
        proc, net = depth.load_model(depth.DEFAULT_MODEL, download=False)
    except Exception as e:  # весов нет локально
        pytest.skip(f'нет локальных весов Depth-Anything-V2-Small: {e.__class__.__name__}')
    from PIL import Image
    a = np.zeros((256, 256, 3), np.uint8)
    a[:, :, :] = np.linspace(0, 255, 256, dtype=np.uint8)[:, None, None]
    d = depth.estimate(Image.fromarray(a), proc, net)
    assert d.shape == (256, 256) and d.dtype == np.uint8


# ---------- pick_take (логика выбора без ASR) ----------
def _row(name, ratio, words, bad=0, ok=0, clipped=False, gaps=(), dur=2.0):
    return {'take': name, 'asr': '', 'ratio': ratio, 'words': words, 'bad': bad, 'ok': ok, 'clipped_end': clipped,
            'gaps_gt_025': list(gaps), 'dur': dur, 'stress': {}}


def test_ratio_detects_dropped_word():
    t = 'Проверка заняла ровно одну минуту'
    assert pick.text_ratio(t, 'проверка заняла ровно одну минуту') > 0.97
    # одно выброшенное короткое слово в длинной фразе даёт ≈0,91: порог 0,9 его не ловит,
    # поэтому ratio ещё участвует в сортировке среди прошедших
    assert pick.text_ratio(t, 'проверка заняла одну минуту') < 0.95
    assert pick.text_ratio(t, 'проверка заняла минуту') < 0.9
    assert pick.text_ratio('Вернул 200 рублей', 'вернул двести рублей') > 0.97


def test_measure_too_short_take_returns_row(tmp_path):
    import soundfile as sf
    p = tmp_path / 'tiny.wav'
    sf.write(p, np.zeros(120), 24000)             # 5 мс: раньше ValueError в np.convolve
    r = pick.measure(p, 'Проверка', asr=None)
    assert r['take'] == 'tiny.wav' and r['ratio'] == 0.0 and r['words'] == []
    assert r['clipped_end'] is True and 'короче' in r['error']
    assert pick.choose(pick.add_stretch([r]))['take'] == 'tiny.wav'


def test_measure_english_words_get_stretch_keys(tmp_path):
    """Английский дубль: ключи слов не пустые, растянутое «hello» ловится (раньше norm() давал '')."""
    import soundfile as sf
    from types import SimpleNamespace as NS
    p = tmp_path / 'en.wav'
    sf.write(p, 0.3 * np.sin(2 * np.pi * 220 * np.arange(24000) / 24000), 24000)

    def asr_for(d_hello):
        ws = [NS(word=' Hello,', start=0.0, end=d_hello), NS(word=' world', start=d_hello, end=d_hello + .3)]
        return NS(transcribe=lambda *a, **k: ([NS(words=ws)], None))

    rows = [pick.measure(p, 'Hello, world', asr_for(d), lang='en') for d in (.2, .2, 2.0)]
    assert rows[0]['words'][0][0] == 'hello' and rows[0]['words'][1][0] == 'world'
    pick.add_stretch(rows)
    assert [r['stretch'] for r in rows] == [False, False, True]
    assert rows[2]['stretch_ratio'] == (10.0, 'hello')
    ru = pick.measure(p, 'Ёлка', NS(transcribe=lambda *a, **k: ([NS(words=[NS(word='Ёлка!', start=0, end=.4)])], None)))
    assert ru['words'][0][0] == 'елка'                                     # русский ключ как раньше

def test_pick_report_has_basenames_and_copies_best(tmp_path, monkeypatch):
    import sys as _sys
    import types
    fake = types.ModuleType('faster_whisper')
    fake.WhisperModel = lambda *a, **k: object()
    monkeypatch.setitem(_sys.modules, 'faster_whisper', fake)
    takes = []
    for i in range(2):
        q = tmp_path / 'cand' / f'{i}.wav'
        q.parent.mkdir(exist_ok=True)
        q.write_bytes(b'RIFF' + bytes(i))
        takes.append(q)
    w = [('проверка', .5), ('заняла', .4)]
    rows = iter([_row('0.wav', 0.80, w), _row('1.wav', 0.99, w)])
    monkeypatch.setattr(pick, 'measure', lambda p, text, asr, expected=None: next(rows))
    rep, dst = tmp_path / 'qa' / 'pick.json', tmp_path / 'voice' / 'raw.wav'
    assert pick.main([*map(str, takes), '--text', 'Проверка заняла', '--report', str(rep), '--copy-to', str(dst)]) == 0
    assert dst.read_bytes() == takes[1].read_bytes()
    txt = rep.read_text()
    assert str(tmp_path) not in txt
    assert json.loads(txt)['best'] == '1.wav'


def test_choose_skips_dropped_word_and_stretch():
    w = [('проверка', .5), ('заняла', .4), ('минуту', .45)]
    rows = [
        _row('a.wav', 0.80, w[:2], dur=1.5),                                   # выброшено слово
        _row('b.wav', 0.98, [('проверка', .5), ('заняла', .9), ('минуту', .45)]),  # тянет «заняла»
        _row('c.wav', 0.97, w),
    ]
    pick.add_stretch(rows)
    assert rows[1]['stretch'] is True and rows[2]['stretch'] is False
    best = pick.choose(rows)
    assert best['take'] == 'c.wav'
    assert all('stretch_ratio' in r for r in rows)


def test_choose_tiebreak_is_median_duration_not_shortest():
    # три равных по качеству дубля: раньше выигрывал самый короткий (1,6 с), теперь ближайший к медиане (2,0 с)
    w = [('проверка', .5), ('заняла', .4), ('минуту', .45)]
    rows = pick.add_stretch([_row('short.wav', 0.97, w, dur=1.6), _row('mid.wav', 0.97, w, dur=2.0),
                             _row('long.wav', 0.97, w, dur=2.5)])
    assert pick.choose(rows)['take'] == 'mid.wav'


def test_choose_drops_too_fast_and_falsetto_takes():
    w = [('проверка', .5), ('заняла', .4)]
    fast, ok_ = _row('fast.wav', 0.98, w, dur=2.0), _row('ok.wav', 0.97, w, dur=2.0)
    fast['rate'], ok_['rate'] = 7.4, 5.1
    assert pick.choose(pick.add_stretch([fast, ok_]))['take'] == 'ok.wav'
    hi, lo = _row('hi.wav', 0.98, w), _row('lo.wav', 0.97, w)
    hi['f0'], lo['f0'] = 290, 110
    assert pick.choose([hi, lo], max_f0=250)['take'] == 'lo.wav'
    assert pick.choose([hi, lo])['take'] == 'hi.wav'          # без --max-f0 высота не участвует
    # если быстрые все, выбор не пустой
    fast2 = dict(ok_, take='fast2.wav', rate=6.9)
    assert pick.choose([fast, fast2])['take'] in {'fast.wav', 'fast2.wav'}


def test_speech_rate_uses_asr_span():
    words = [('проверка', 0.3, 0.8), ('заняла', 0.85, 1.2), ('минуту', 1.25, 1.8)]
    # «Проверка заняла минуту» = 9 гласных на 1,5 с речи, тишина по краям не считается
    assert pick.speech_rate('Проверка заняла минуту.', words, dur=2.4) == 6.0
    assert pick.speech_rate('Проверка', [], dur=2.0) == 1.5


def _say_ok():
    if not shutil.which('say'):
        return False
    r = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
    return 'ru_RU' in r.stdout


@pytest.mark.slow
@pytest.mark.skipif(not _say_ok(), reason='нет русского голоса macOS say')
def test_pick_with_real_asr(tmp_path):
    pytest.importorskip('faster_whisper')
    from faster_whisper import WhisperModel
    try:
        asr = WhisperModel('small', device='cpu', compute_type='int8', local_files_only=True)
    except Exception:
        pytest.skip('нет локальной модели faster-whisper small')
    text = 'Проверка заняла ровно одну минуту.'
    takes = []
    for name, phrase in (('full1', text), ('cut', 'Проверка заняла минуту.'), ('full2', text)):
        aiff, wav = tmp_path / f'{name}.aiff', tmp_path / f'{name}.wav'
        subprocess.run(['say', '-v', 'Milena', '-o', str(aiff), phrase], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-ar', '24000', '-ac', '1', str(wav)], check=True)
        takes.append(wav)
    rows = pick.add_stretch([pick.measure(p, text, asr) for p in takes])
    best = pick.choose(rows)
    assert not best['take'].endswith('cut.wav')
    assert all('ratio' in r for r in rows)


# ---------- artifacts ----------
def test_artifacts_hashes(tmp_path):
    (tmp_path / 'output').mkdir(); (tmp_path / 'qa').mkdir()
    (tmp_path / 'output' / 'final.mp4').write_bytes(b'video' * 1000)
    (tmp_path / 'qa' / 'final-result.json').write_text(json.dumps({'status': 'preview_partial', 'technical_pass': False}))
    (tmp_path / 'story.json').write_text('{}')
    code = art.main([str(tmp_path), '--include', 'output/final.mp4', 'qa/*.json', 'story.json'])
    assert code == 0
    out = json.loads((tmp_path / 'ARTIFACTS.json').read_text())
    assert out['status'] == 'preview_partial' and out['publication'] == 'not published'
    for a in out['artifacts']:
        assert a['sha256'] == hashlib.sha256((tmp_path / a['path']).read_bytes()).hexdigest()
    assert len(out['artifacts']) == 3


def test_artifacts_missing_file(tmp_path, capsys):
    assert art.main([str(tmp_path), '--include', 'output/final.mp4']) == 2
    assert 'output/final.mp4' in capsys.readouterr().err
    assert art.main([str(tmp_path), '--include', 'output/final.mp4', '--allow-missing']) == 0


def test_artifacts_rejects_paths_outside_project(tmp_path, capsys):
    proj = tmp_path / 'proj'
    proj.mkdir()
    (tmp_path / 'secret.txt').write_text('x')
    assert art.main([str(proj), '--include', '../secret.txt']) == 2
    err = capsys.readouterr().err
    assert 'вне проекта' in err and str(tmp_path) not in err
    assert art.main([str(proj), '--include', str(tmp_path / 'secret.txt')]) == 2
    assert art.main([str(proj), '--include', str(tmp_path / '*.txt')]) == 2
    assert not (proj / 'ARTIFACTS.json').exists()
