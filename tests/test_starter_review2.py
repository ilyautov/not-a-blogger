"""starter, ревью 2: пара final.mp4 + отчёт при сбое финала, FLOAT до мастеринга, понятные ошибки trim, проверка флагов render."""
import importlib.util
import json
import math
import sys
from types import SimpleNamespace

import numpy as np
import pytest
import soundfile as sf

from conftest import ROOT

ST = ROOT / 'starter'


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ST / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fin = load('tools/finish.py', 'starter_finish_r2')
snd = load('tools/sound.py', 'starter_sound_r2')
trim = load('voice/trim.py', 'starter_trim_r2')
rnd = load('tools/render.py', 'starter_render_r2')


def _fin_paths(monkeypatch, root):
    (root / 'output').mkdir(); (root / 'qa').mkdir()
    for k, v in {'P': root, 'OUT': root / 'output/final.mp4', 'TMP': root / 'output/final.tmp.mp4', 'REPORT': root / 'qa/final-result.json'}.items():
        monkeypatch.setattr(fin, k, v)
    fin.OUT.write_bytes(b'old video')
    fin.REPORT.write_text(json.dumps({'status': 'ready_for_user_preview', 'technical_pass': True, 'checks': {'asr_ge_0_9': True}}))


def test_finish_crash_does_not_leave_old_green_report(tmp_path, monkeypatch):
    _fin_paths(monkeypatch, tmp_path)
    def build(a):
        fin.TMP.write_bytes(b'new video')          # видео уже собрано, ASR падает
        raise RuntimeError('whisper не загрузился')
    monkeypatch.setattr(fin, 'build', build); monkeypatch.setattr(sys, 'argv', ['finish.py'])
    with pytest.raises(RuntimeError):
        fin.main()
    rep = json.loads(fin.REPORT.read_text())
    assert rep['status'] == 'technical_failed' and rep['technical_pass'] is False and 'whisper' in rep['error']
    assert rep['video'] is None and rep['video_sha256'] is None
    assert fin.OUT.read_bytes() == b'old video' and not fin.TMP.exists()   # непроверенное видео не встало на место


def test_finish_success_swaps_video_and_report_together(tmp_path, monkeypatch):
    _fin_paths(monkeypatch, tmp_path)
    def build(a):
        fin.TMP.write_bytes(b'new video')
        return {'status': 'technical_failed', 'technical_pass': False, 'checks': {'loudness': False}, 'video': 'output/final.mp4'}
    monkeypatch.setattr(fin, 'build', build); monkeypatch.setattr(sys, 'argv', ['finish.py'])
    assert fin.main() == 1
    assert fin.OUT.read_bytes() == b'new video' and not fin.TMP.exists()
    assert json.loads(fin.REPORT.read_text())['checks'] == {'loudness': False}


def test_finish_run_prints_ffmpeg_stderr(capsys):
    with pytest.raises(fin.subprocess.CalledProcessError):
        fin.run([sys.executable, '-c', 'import sys; sys.stderr.write("No such file or directory"); sys.exit(1)'])
    assert 'No such file or directory' in capsys.readouterr().err


def test_sound_mix_is_float_before_mastering(tmp_path, monkeypatch):
    (tmp_path / 'qa').mkdir(); audio = tmp_path / 'assets/audio'; audio.mkdir(parents=True)
    (tmp_path / 'story.json').write_text(json.dumps({'duration': 1.0, 'voice_track': 'assets/audio/voice-track.wav', 'cues': []}))
    (tmp_path / 'reel.json').write_text(json.dumps({'music': {'gain': 0}, 'sound_events': [{'event': 'hit', 'kind': 'thud', 'gain': 2}]}))
    (tmp_path / 'qa/events.json').write_text(json.dumps({'hit': .3})); (tmp_path / 'qa/shots.json').write_text('[0]')
    def run(c):                                     # ffmpeg подменён: нормализованный голос = тишина, мастер не нужен
        if c[-1].endswith('normalized-track.wav'): sf.write(c[-1], np.zeros(snd.SR), snd.SR)
    monkeypatch.setattr(snd, 'P', tmp_path); monkeypatch.setattr(snd, 'run', run)
    snd.main()
    assert sf.info(str(audio / 'mix.wav')).subtype == 'FLOAT' and sf.info(str(audio / 'sfx.wav')).subtype == 'FLOAT'
    mix, _ = sf.read(audio / 'mix.wav')
    assert np.abs(mix).max() > 1                    # пик выше 1 дожил до loudnorm, не срезан


def test_trim_empty_asr_is_clear_error(tmp_path, monkeypatch):
    (tmp_path / 'voice').mkdir(); sf.write(tmp_path / 'voice/raw-0.wav', np.zeros(24000), 24000)
    monkeypatch.setattr(trim, 'P', tmp_path); monkeypatch.setattr(trim, 'OUT', tmp_path / 'voice')
    asr = SimpleNamespace(transcribe=lambda *a, **k: ([], None))
    with pytest.raises(SystemExit) as e:
        trim.trim(0, asr)
    assert 'реплика 0' in str(e.value) and 'voice/raw-0.wav' in str(e.value) and 'перезапишите' in str(e.value)


def test_trim_token_mismatch_is_clear_error(tmp_path, monkeypatch):
    out = tmp_path / 'voice'; out.mkdir()
    monkeypatch.setattr(trim, 'P', tmp_path); monkeypatch.setattr(trim, 'OUT', out)
    monkeypatch.setattr(trim, 'CH', [{'text': 'Один два.', 'pause': .1}]); monkeypatch.setattr(trim, 'SHOW', ['Один два три.'])
    (out / 'asr-0.json').write_text(json.dumps({'text': 'Один два.', 'take_words': [['Один', 0, .3], ['два', .3, .6]]}, ensure_ascii=False))
    assert trim.token_errors() and 'реплика 0' in trim.token_errors()[0]
    with pytest.raises(SystemExit) as e:
        trim.track(None)
    assert 'реплика 0' in str(e.value) and 'lines.json' in str(e.value) and '3' in str(e.value)
    monkeypatch.setattr(trim, 'SHOW', ['Один_два{2}'])
    assert trim.token_errors() == []


@pytest.mark.parametrize('frames,t0,t1', [(0, 0, None), (-0.75, 0, None), (math.nan, 0, None), (0.75, 3, 2), (0.75, -1, None), (None, 5, 4)])
def test_render_rejects_bad_interval(frames, t0, t1):
    with pytest.raises(SystemExit):
        rnd.interval(frames, t0, t1, 10.0)


def test_render_interval_ok_and_clamped():
    assert rnd.interval(0.75, 0, None, 10.0) == 10.0 and rnd.interval(None, 1, 40, 10.0) == 10.0


def test_render_frames_zero_touches_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(rnd, 'P', tmp_path); monkeypatch.setattr(sys, 'argv', ['render.py', '--frames', '0'])
    monkeypatch.setattr(rnd, 'story', lambda: pytest.fail('story.json не должен переписываться'))
    with pytest.raises(SystemExit):
        rnd.main()
    assert list(tmp_path.iterdir()) == []
