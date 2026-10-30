"""ru_tts_text, gaps, tail_trim, aac_safe, sfx — на синтетике numpy."""
import json

import numpy as np
import pytest
import soundfile as sf

from conftest import load, needs_ffmpeg, silence, tone

ru = load('voice', 'ru_tts_text')
gaps = load('audio', 'gaps')
tail = load('audio', 'tail_trim')
sfx = load('audio', 'sfx')


# ---------- ru_tts_text ----------
def test_colon_becomes_period():
    assert ru.prepare('Отчёт: готов')[0] == 'Отчёт. готов'


def test_ii_is_warned_not_replaced():
    # автозамена на «нейросеть» ломала падеж («у нейросеть»); правило репозитория (gotchas/lang/ru.md)
    # выполняет автор реплики, утилита только указывает место
    assert ru.prepare('Спроси у ИИ')[0] == 'Спроси у ИИ'
    assert any('нейросеть' in w for w in ru.prepare('Спроси у ИИ')[2])
    assert any('нейросеть' in w for w in ru.prepare('Вот ИИ-агент вернул ответ')[2])
    assert not any('нейросеть' in w for w in ru.prepare('Вот ИИС работает')[2])
    assert all('И-И' not in rep for _, rep, _ in ru.RULES)


def test_stress_marks_removed_and_exclamations_warned():
    out, notes, warn = ru.prepare('Прове\u0301рка заня\u0301ла мину\u0301ту!')
    assert out == 'Проверка заняла минуту!' and '\u0301' not in out
    assert any('U+0301' in n for n in notes)
    assert any('«!»' in w for w in warn)
    assert ru.exclamation_share(['Да!', 'Нет.', 'Ну?!', 'Ага.']) == 0.5
    assert ru.exclamation_share([]) == 0.0


def test_ai_replaced_only_standalone():
    assert ru.prepare('Вот AI-агент')[0] == 'Вот эй-ай-агент'
    assert ru.prepare('Вот OpenAI и X-AI')[0] == 'Вот OpenAI и X-AI'


def test_digits_warn_and_short_first_word():
    _, _, warn = ru.prepare('Вернул 200 рублей')
    assert any('цифры' in w for w in warn)
    _, _, warn = ru.prepare('Да, это так')
    assert any('короткое первое слово' in w for w in warn)


def test_ru_cli_strict(capsys):
    assert ru.main(['Отчёт готов полностью']) == 0
    assert ru.main(['--strict', 'Вернул 200']) == 1


# ---------- gaps ----------
def test_single_gap():
    sr = 24000
    x = np.concatenate([tone(1.0, sr), silence(0.3, sr), tone(1.0, sr)])
    g = gaps.find_gaps(x, sr)
    assert len(g) == 1
    t, d = g[0]
    assert abs(t - 1.0) <= 0.02 and abs(d - 0.3) <= 0.02


def test_gaps_all_silent_is_one_long_gap(tmp_path):
    sr = 24000
    assert gaps.find_gaps(silence(5, sr), sr) == [(0.0, 5.0)]
    p = tmp_path / 'zero.wav'
    sf.write(p, silence(5, sr), sr)
    assert gaps.main([str(p), '--max-gap', '0.8']) == 1
    # равномерный шум на −90 dBFS — тоже тишина
    noise = 10 ** (-90 / 20) * np.random.default_rng(0).normal(size=5 * sr)
    assert gaps.find_gaps(noise, sr) == [(0.0, 5.0)]
    # обычная речь с паузой не меняется от пола
    x = np.concatenate([tone(1, sr), silence(1, sr), tone(1, sr)])
    assert gaps.find_gaps(x, sr) == gaps.find_gaps(x, sr, floor_db=-300)


def test_gaps_empty_input(tmp_path, capsys):
    p = tmp_path / 'empty.wav'
    sf.write(p, np.zeros(0), 24000)
    assert gaps.main([str(p), '--max-gap', '0.8']) == 2
    assert 'пуст' in capsys.readouterr().err
    assert gaps.find_gaps(np.zeros(0), 24000) == []

def test_gaps_json_has_basename_only(tmp_path, capsys):
    sr = 24000
    p = tmp_path / 'v.wav'
    sf.write(p, np.concatenate([tone(1, sr), silence(1.0, sr), tone(1, sr)]), sr)
    assert gaps.main([str(p), '--json']) == 0
    out = capsys.readouterr().out
    assert '"file": "v.wav"' in out and str(tmp_path) not in out


def test_gaps_cli(tmp_path):
    sr = 24000
    p = tmp_path / 'v.wav'
    sf.write(p, np.concatenate([tone(1, sr), silence(1.0, sr), tone(1, sr)]), sr)
    assert gaps.main([str(p), '--max-gap', '0.8', '--json']) == 1
    assert gaps.main([str(p), '--max-gap', '1.5']) == 0


# ---------- tail_trim ----------
def test_tail_is_cut_at_pause(tmp_path):
    sr = 24000
    x = np.concatenate([tone(2.0, sr), silence(0.2, sr), tone(0.5, sr, 330), silence(0.3, sr)])
    y, info = tail.trim(x, sr)
    assert info['trimmed'] is True
    assert abs(info['cut_at'] - 2.0) <= 0.02
    assert abs(len(y) / sr - (2.0 + 0.20)) <= 0.03          # речь + pad


def test_long_tail_untouched(tmp_path):
    sr = 24000
    x = np.concatenate([tone(2.0, sr), silence(0.2, sr), tone(2.0, sr, 330), silence(0.3, sr)])
    y, info = tail.trim(x, sr)
    assert y is None and info['trimmed'] is False
    p = tmp_path / 'raw.wav'
    sf.write(p, x, sr)
    assert tail.main([str(p)]) == 2
    assert not (tmp_path / 'raw.cut.wav').exists()


def test_tail_cli_writes(tmp_path, capsys):
    sr = 24000
    p = tmp_path / 'raw.wav'
    sf.write(p, np.concatenate([tone(2.0, sr), silence(0.2, sr), tone(0.5, sr), silence(0.3, sr)]), sr)
    assert tail.main([str(p), '--json']) == 0
    assert (tmp_path / 'raw.cut.wav').exists()
    assert json.loads(capsys.readouterr().out)['file'] == 'raw.wav'


# ---------- aac_safe ----------
@needs_ffmpeg
def test_aac_safe_brings_peaks_under_ceiling(tmp_path):
    aac = load('audio', 'aac_safe')
    sr = 48000
    rng = np.random.default_rng(1)
    x = 0.2 * rng.normal(0, 0.3, sr * 2).clip(-1, 1)
    for k in (12000, 40000, 70000):          # импульсы −1 dBFS
        x[k:k + 30] = 10 ** (-1 / 20) * np.sign(np.sin(np.arange(30)))
    x = np.column_stack([x, x])
    src, out = tmp_path / 'm.wav', tmp_path / 'm-aac.wav'
    sf.write(src, x, sr, subtype='PCM_24')
    code = aac.main(['--in', str(src), '--out', str(out), '--ceiling', '-3.2', '--json'])
    y, sr2 = sf.read(out, always_2d=True)
    assert sr2 == sr and len(y) == len(x)
    d = aac.aac_roundtrip(y, sr)
    peak = 20 * np.log10(np.abs(d).max())
    assert peak <= -3.2 + 0.1
    assert code == 0



@needs_ffmpeg
@pytest.mark.parametrize('sr', [24000, 44100])
def test_aac_safe_checks_the_final_48k_encode(tmp_path, sr):
    """Мастер не 48 кГц: оптимизация идёт на частоте итогового mp4, отчёт меряет готовый файл."""
    from conftest import ffmpeg
    aac = load('audio', 'aac_safe')
    rng = np.random.default_rng(2)
    x = 0.2 * rng.normal(0, 0.3, sr * 2).clip(-1, 1)
    for k in (sr // 4, sr, sr + sr // 2):
        x[k:k + 15] = 10 ** (-1 / 20) * np.sign(np.sin(np.arange(15)))
    x = np.column_stack([x, x])
    src, out, pic, fin = tmp_path / 'm.wav', tmp_path / 'm-aac.wav', tmp_path / 'p.mp4', tmp_path / 'final.mp4'
    sf.write(src, x, sr, subtype='PCM_24')
    ffmpeg('-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=2:r=10', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', pic)
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = aac.main(['--in', str(src), '--out', str(out), '--video', str(pic), '--out-video', str(fin),
                         '--ceiling', '-3.2', '--json'])
    rep = json.loads(buf.getvalue())
    assert rep['sr'] == 48000 and sf.info(out).samplerate == 48000
    m = aac.measure_track(fin, -3.2)                       # независимый замер готового mp4
    assert m['sr'] == 48000
    assert rep['final'] == m
    assert m['peak_dbfs'] <= -3.2 + 0.1 and m['over'] == 0
    assert code == 0 and rep['ok'] is True


def test_aac_safe_video_flags_go_together(tmp_path):
    aac = load('audio', 'aac_safe')
    src = tmp_path / 'm.wav'
    sf.write(src, np.zeros((2400, 2)), 24000, subtype='PCM_24')
    with pytest.raises(SystemExit):
        aac.main(['--in', str(src), '--out', str(tmp_path / 'o.wav'), '--video', 'v.mp4'])

def test_aac_safe_without_ffmpeg(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv('FFMPEG', str(tmp_path / 'no-such-ffmpeg'))
    aac = load('audio', 'aac_safe')
    src = tmp_path / 'm.wav'
    sf.write(src, np.zeros((2400, 2)), 24000, subtype='PCM_24')
    assert aac.main(['--in', str(src), '--out', str(tmp_path / 'o.wav')]) == 2
    assert 'ffmpeg not found' in capsys.readouterr().err


# ---------- sfx ----------
@pytest.mark.parametrize('kind', list(sfx.KINDS))
def test_sfx_kind(kind):
    length = 0.4
    a = sfx.render(kind, length=length, seed=3)
    b = sfx.render(kind, length=length, seed=3)
    assert len(a) == round(length * sfx.SR)
    assert np.isfinite(a).all()
    assert np.abs(a).max() <= 1.0
    assert a.tobytes() == b.tobytes()


def test_sfx_cli(tmp_path):
    p = tmp_path / 'w.wav'
    assert sfx.main(['whip', '--out', str(p), '--length', '0.3']) == 0
    x, sr = sf.read(p)
    assert len(x) == round(0.3 * sr)
    with pytest.raises(ValueError):
        sfx.render('nope')
