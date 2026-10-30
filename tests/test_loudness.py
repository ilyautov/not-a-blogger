"""loudness: логика окна и потолка; ebur128 на синусе известной громкости (нужен ffmpeg)."""
import json
import math

import pytest

from conftest import ffmpeg, load, needs_ffmpeg

ld = load('qa', 'loudness')


def _amp(lufs):
    """Амплитуда моно-синуса 1 кГц для заданных LUFS: полная шкала = −3,01 LUFS (BS.1770)."""
    return 10 ** ((lufs + 3.01) / 20)


def test_evaluate_final_window_and_peak():
    assert ld.evaluate(-15.2, -2.0)['pass'] is True
    r = ld.evaluate(-13.5, -2.0)
    assert r['checks']['integrated'] == [-13.5, False] and r['pass'] is False
    r = ld.evaluate(-15.0, -1.2)
    assert r['checks']['true_peak'] == [-1.2, False]
    assert r['window'] == [-16.0, -14.0] and r['tp_max'] == -1.5


def test_evaluate_take_target_and_overrides():
    assert ld.evaluate(-16.3, -2.5, target='take')['pass'] is True
    assert ld.evaluate(-15.0, -2.5, target='take')['pass'] is True       # край окна −17…−15
    assert ld.evaluate(-14.5, -2.5, target='take')['pass'] is False
    assert ld.evaluate(-14.5, -2.5, target='take', lufs=-14)['pass'] is True


def test_silence_is_null_not_infinity():
    r = ld.evaluate(-math.inf, -math.inf)
    assert r['integrated'] is None and r['pass'] is False
    json.dumps(r, allow_nan=False)


def _sine(path, lufs, seconds=5):
    ffmpeg('-f', 'lavfi', '-i', f'aevalsrc={_amp(lufs):.5f}*sin(2*PI*1000*t):s=48000:d={seconds}', path)


@needs_ffmpeg
def test_measure_sine_at_known_level(tmp_path):
    p = tmp_path / 's.wav'
    _sine(p, -15)
    i, tp, _ = ld.measure(p)
    assert i == pytest.approx(-15, abs=0.3)
    assert tp == pytest.approx(-12, abs=0.3)


@needs_ffmpeg
def test_main_pass_fail_and_take(tmp_path, capsys):
    ok, loud, take = tmp_path / 'ok.wav', tmp_path / 'loud.wav', tmp_path / 'take.wav'
    _sine(ok, -15)
    _sine(loud, -3.5)                      # ≈ −0,5 dBTP: громко и пик выше потолка
    _sine(take, -16)
    assert ld.main([str(ok)]) == 0
    assert json.loads(capsys.readouterr().out)['pass'] is True
    assert ld.main([str(ok), str(loud)]) == 1
    rows = [json.loads(x) for x in capsys.readouterr().out.splitlines()]
    assert [r['pass'] for r in rows] == [True, False]
    assert rows[1]['checks']['true_peak'][1] is False
    assert ld.main(['--target', 'take', str(take)]) == 0
    assert json.loads(capsys.readouterr().out)['target'] == 'take'


@needs_ffmpeg
def test_main_on_mp4_and_unreadable(tmp_path, capsys):
    wav, mp4 = tmp_path / 's.wav', tmp_path / 's.mp4'
    _sine(wav, -15)
    ffmpeg('-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=5', '-i', wav, '-shortest', '-c:v', 'libx264',
           '-c:a', 'aac', '-b:a', '192k', mp4)
    assert ld.main([str(mp4)]) == 0
    capsys.readouterr()
    bad = tmp_path / 'bad.wav'
    bad.write_text('not audio')
    assert ld.main([str(bad)]) == 2
