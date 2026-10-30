"""voice_qa: логика гейта на синтетике, ebur128 на сгенерированном wav (нужен ffmpeg)."""
import json

import numpy as np
import pytest

from conftest import load, needs_ffmpeg, silence, tone

vq = load('qa', 'voice_qa')


def _lines(gaps, dur=1.5, text='Проверка заняла'):
    out, t = [], 0.3
    for i, g in enumerate([0.0] + list(gaps)):
        t += g
        out.append({'id': f'l{i + 1}', 'text': text, 'start': round(t, 3), 'end': round(t + dur, 3)})
        t += dur
    return out


def test_metronome_gaps_fail_varied_pass():
    metronome = vq.evaluate(-1.8, 4.0, _lines([0.38] * 6))
    assert metronome['checks']['gap_sd'] == [0.0, False] and metronome['pass'] is False
    varied = vq.evaluate(-1.8, 4.0, _lines([0.25, 0.6, 0.3, 0.85, 0.4, 0.55]))
    assert varied['checks']['gap_sd'][1] is True and varied['pass'] is True


def test_squashed_peaks_and_flat_lra_fail():
    r = vq.evaluate(-4.4, 1.8, _lines([0.25, 0.6, 0.3, 0.85]))
    assert r['checks']['true_peak'] == [-4.4, False]
    assert r['checks']['lra'] == [1.8, False]
    assert r['pass'] is False


def test_fast_line_and_falsetto_listed():
    lines = _lines([0.3, 0.7, 0.4])
    lines[1]['end'] = lines[1]['start'] + 0.6           # 6 гласных за 0,6 с = 10 слог/с
    r = vq.evaluate(-1.8, 4.0, lines, f0={'l1': 110, 'l2': 120, 'l3': 290, 'l4': 0})
    assert r['checks']['rate_over'] == [['l2'], False]
    assert r['checks']['f0_over'] == [['l3'], False]


def test_f0_not_measured_is_not_a_fail():
    r = vq.evaluate(-1.8, 4.0, _lines([0.25, 0.6, 0.3]), f0={'l1': None, 'l2': None})
    assert r['checks']['f0_over'][1] is None and r['pass'] is True


def test_load_lines_accepts_dict_and_requires_fields(tmp_path):
    p = tmp_path / 't.json'
    p.write_text(json.dumps({'lines': [{'text': 'а', 'start': 0, 'end': 1}]}))
    assert vq.load_lines(p)[0]['id'] == 'l1'
    p.write_text(json.dumps([{'text': 'а', 'start': 0}]))
    with pytest.raises(ValueError):
        vq.load_lines(p)


@needs_ffmpeg
def test_main_soft_clip_lowers_true_peak(tmp_path):
    """Одинаковая громкость (RMS): линейная дорожка держит пик у −1,5 dBTP, после tanh пики придавлены."""
    import soundfile as sf
    sr = 48000
    lines = _lines([0.25, 0.6, 0.3, 0.85], text='Ок')
    rng = np.random.default_rng(0)
    x = silence(lines[-1]['end'] + 0.3, sr)
    for ln in lines:
        a, b = int(ln['start'] * sr), int(ln['end'] * sr)
        env = np.abs(np.sin(np.linspace(0, 9 * np.pi, b - a)))     # «слоги»: огибающая с пиками
        x[a:b] = rng.standard_normal(b - a) * env * 0.2
    lin = x / np.abs(x).max() * 0.84                               # ≈ −1,5 dBFS
    sq = np.tanh(lin * 6)
    sq *= np.sqrt(np.mean(lin ** 2) / np.mean(sq ** 2))            # та же громкость
    (tmp_path / 'lines.json').write_text(json.dumps(lines))
    out = {}
    for name, y in [('lin.wav', lin), ('tanh.wav', sq)]:
        sf.write(tmp_path / name, y, sr)
        vq.main([str(tmp_path / name), '--lines', str(tmp_path / 'lines.json'), '--json', str(tmp_path / f'{name}.json')])
        out[name] = json.loads((tmp_path / f'{name}.json').read_text())
    assert out['lin.wav']['checks']['true_peak'][1] is True
    assert out['tanh.wav']['checks']['true_peak'][1] is False
    assert out['tanh.wav']['true_peak'] < out['lin.wav']['true_peak'] - 3
    assert out['lin.wav']['checks']['f0_over'][1] is None           # голоса без музыки не дали: F0 не мерился
    assert str(tmp_path) not in json.dumps(out['lin.wav'])


def test_line_f0_from_voice_track(tmp_path):
    pytest.importorskip('librosa')
    import soundfile as sf
    sr = 24000
    lines = _lines([0.3, 0.6], dur=1.0)
    x = silence(lines[-1]['end'] + 0.2, sr)
    for ln, hz in zip(lines, (110, 300, 120)):
        a = int(ln['start'] * sr)
        seg = tone(1.0, sr, hz, 0.3)
        x[a:a + len(seg)] = seg
    sf.write(tmp_path / 'voice.wav', x, sr)
    f0 = vq.line_f0(lines, tmp_path, tmp_path / 'voice.wav')
    assert abs(f0['l1'] - 110) < 5 and abs(f0['l2'] - 300) < 10
    assert vq.evaluate(-1.8, 4.0, lines, f0)['checks']['f0_over'][0] == ['l2']


def test_f0_diagnostic_reports_pitch_but_keeps_it_out_of_pass():
    lines = _lines([0.25, 0.6, 0.3, 0.85, 0.4, 0.55])
    high = {x['id']: 300.0 for x in lines}
    strict = vq.evaluate(-1.8, 4.0, lines, high)
    assert strict['checks']['f0_over'][1] is False and strict['pass'] is False
    diag = vq.evaluate(-1.8, 4.0, lines, high, f0_diagnostic=True)
    assert diag['checks']['f0_over'][1] is False and diag['f0_diagnostic'] is True and diag['pass'] is True
