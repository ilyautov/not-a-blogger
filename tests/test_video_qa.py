"""frame_fill и jitter на ffmpeg color/testsrc и синтетических кадрах."""
import numpy as np
import pytest

from conftest import encode_frames, ffmpeg, load, needs_ffmpeg

ff = load('qa', 'frame_fill')
jit = load('qa', 'jitter')


def test_missing_ffmpeg_is_a_clear_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv('FFMPEG', str(tmp_path / 'no-ffmpeg'))
    monkeypatch.setenv('FFPROBE', str(tmp_path / 'no-ffprobe'))
    assert load('qa', 'jitter').main([str(tmp_path / 'a.mp4')]) == 2
    assert 'ffmpeg not found' in capsys.readouterr().err
    assert load('qa', 'frame_fill').main([str(tmp_path / 'a.mp4')]) == 2
    assert 'ffmpeg not found' in capsys.readouterr().err


@needs_ffmpeg
def test_gray_is_empty(tmp_path):
    p = tmp_path / 'gray.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'color=c=gray:s=1080x1920:d=6:r=30', '-pix_fmt', 'yuv420p', p)
    r = ff.analyse(str(p))
    assert r['median'] == 0
    assert r['file'] == 'gray.mp4'                 # в отчёт идёт имя, не путь к домашней папке
    assert len(r['empty_runs']) == 1
    assert ff.main([str(p), '--fail-on-empty']) == 1


@needs_ffmpeg
def test_testsrc_is_full(tmp_path):
    p = tmp_path / 'src.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'testsrc=s=1280x720:d=6:r=30', '-pix_fmt', 'yuv420p', p)
    r = ff.analyse(str(p))
    assert r['median'] > 50
    assert r['empty_runs'] == []
    g = ff.analyse(str(p), mode='grid')
    assert g['median'] > 50


@needs_ffmpeg
def test_subtitle_band_ignored(tmp_path):
    p = tmp_path / 'subs.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'color=c=gray:s=1080x1920:d=6:r=30',
           '-vf', 'drawbox=x=100:y=1700:w=880:h=150:color=white:t=fill', '-pix_fmt', 'yuv420p', p)
    r = ff.analyse(str(p))
    assert r['median'] == 0
    r2 = ff.analyse(str(p), subs_band=0.0)
    assert r2['median'] > 0


def _moving_box(n, h, w, speed, drop_every=None):
    frames = np.full((n, h, w), 40, np.uint8)
    bw = w // 8
    pos = 0.0
    for i in range(n):
        if drop_every and i % drop_every == drop_every - 1:
            frames[i] = frames[i - 1]           # задвоенный кадр вместо следующего шага
            pos += speed
            continue
        x = int(pos) % (w - bw)
        frames[i, h // 3:h // 3 + bw, x:x + bw] = 230
        pos += speed
    return frames


@needs_ffmpeg
@pytest.mark.parametrize('size', [(384, 216), (270, 480)])
def test_jitter_detects_dropped_frames(tmp_path, size):
    h, w = size
    smooth, jerky = tmp_path / 's.mp4', tmp_path / 'j.mp4'
    encode_frames(_moving_box(60, h, w, 3), smooth)
    encode_frames(_moving_box(60, h, w, 3, drop_every=3), jerky)
    a = jit.jitter(jit.read_gray(str(smooth)))
    b = jit.jitter(jit.read_gray(str(jerky)))
    assert b['jerk_ratio'] > 2 * a['jerk_ratio'] + 0.1


@needs_ffmpeg
def test_jitter_full_hd(tmp_path):
    p = tmp_path / 'hd.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'testsrc=s=1920x1080:d=1:r=30', '-pix_fmt', 'yuv420p', p)
    r = jit.jitter(jit.read_gray(str(p)))
    assert r['frames'] == 30
    assert jit.main([str(p)]) == 0
