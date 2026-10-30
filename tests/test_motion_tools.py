"""motion_gate и breakdown на синтетических клипах: статичный цвет против движущегося квадрата."""
import importlib.util
import json

import numpy as np
import pytest

from conftest import encode_frames, ffmpeg, load, needs_ffmpeg

pytestmark = [needs_ffmpeg,
              pytest.mark.skipif(importlib.util.find_spec('cv2') is None, reason='нет cv2 (opencv-python-headless)')]

mg = load('qa', 'motion_gate')
bd = load('qa', 'breakdown')


def _moving_box(n=90, h=180, w=320, speed=10):
    frames = np.full((n, h, w), 40, np.uint8)
    bw = w // 4
    for i in range(n):
        x = (i * speed) % (w - bw)
        frames[i, h // 4:h // 4 + bw, x:x + bw] = 230
    return frames


@pytest.fixture(scope='module')
def clips(tmp_path_factory):
    d = tmp_path_factory.mktemp('clips')
    static, moving = d / 'static.mp4', d / 'moving.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'color=c=gray:s=320x180:d=3:r=30', '-pix_fmt', 'yuv420p', static)
    encode_frames(_moving_box(), moving)
    return static, moving


def test_static_clip_is_dead(clips, tmp_path):
    static, _ = clips
    r = mg.analyse(str(static))
    assert r['active_ratio'] < 0.10
    assert r['verdict'] == 'dead'
    js = tmp_path / 'qa' / 'mg.json'
    assert mg.main([str(static), '--json', str(js)]) == 2
    rep = json.loads(js.read_text())
    assert rep['file'] == 'static.mp4'                    # имя файла, не путь к домашней папке


def test_moving_clip_passes(clips, tmp_path):
    _, moving = clips
    r = mg.analyse(str(moving))
    assert r['active_ratio'] > 0.5
    assert r['fast_ratio'] > 0.5
    assert r['dead_shots'] == 0
    md = tmp_path / 'mg.md'
    assert mg.main([str(moving), '--md', str(md)]) == 0
    assert 'no "dead" alarm' in md.read_text()


def test_mask_and_limit(clips):
    _, moving = clips
    full = mg.analyse(str(moving), limit=2.0)
    assert full['analyzed_s'] <= 2.1
    masked = mg.analyse(str(moving), mask=(0.0, 0.75))     # квадрат лежит в верхних 3/4 кадра
    assert masked['active_ratio'] < full['active_ratio']


def test_calib_tsv(clips, tmp_path, capsys):
    static, moving = clips
    tsv = tmp_path / 'calib.tsv'
    tsv.write_text(f'{moving.name}\tgood\n{static.name}\tbad\tflat colour\n', encoding='utf-8')
    (tmp_path / moving.name).symlink_to(moving)
    (tmp_path / static.name).symlink_to(static)
    assert mg.main(['--calib', str(tsv)]) == 0
    out = capsys.readouterr().out
    assert 'active_ratio' in out and 'separates' in out


def test_missing_ffmpeg_is_exit_1(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv('FFMPEG', str(tmp_path / 'no-ffmpeg'))
    monkeypatch.setenv('FFPROBE', str(tmp_path / 'no-ffprobe'))
    assert load('qa', 'motion_gate').main([str(tmp_path / 'a.mp4')]) == 1
    assert 'ffmpeg not found' in capsys.readouterr().err
    assert load('qa', 'breakdown').main([str(tmp_path / 'a.mp4'), '--no-images']) == 1
    assert 'ffmpeg not found' in capsys.readouterr().err


def test_breakdown_no_images(clips, tmp_path):
    _, moving = clips
    out = tmp_path / 'bd'
    assert bd.main([str(moving), '--out', str(out), '--no-images']) == 0
    js = json.loads((out / 'breakdown.json').read_text())
    ref = js['reference']
    assert ref['file'] == 'moving.mp4'
    assert ref['shot_count'] >= 1 and len(ref['shots']) >= 1
    assert ref['fast_ratio'] > 0.5
    assert not list(out.glob('*.jpg')) and not list(out.glob('*.png'))
    assert (out / 'breakdown.md').exists()


def test_breakdown_images_and_compare(clips, tmp_path):
    static, moving = clips
    out = tmp_path / 'bd'
    assert bd.main([str(moving), '--compare', str(static), '--out', str(out)]) == 0
    for name in ('sheet.jpg', 'keys.jpg', 'heat.jpg', 'timeline.png', 'compare/keys.jpg'):
        assert (out / name).exists(), name
    js = json.loads((out / 'breakdown.json').read_text())
    assert js['compare']['file'] == 'static.mp4'
    assert js['compare']['fast_ratio'] < js['reference']['fast_ratio']
    assert '| | reference | remake |' in (out / 'breakdown.md').read_text()
