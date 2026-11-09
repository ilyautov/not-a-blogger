"""scene_gate: camera compensation, action flags and composition repeats on synthetic frames and clips."""
import json

import numpy as np

from conftest import encode_frames, load, needs_ffmpeg

sg = load('qa', 'scene_gate')


def texture(h=142, w=80, seed=0):
    rng = np.random.default_rng(seed)
    img = rng.uniform(0, 255, (h // 4 + 2, w // 4 + 2)).astype(np.float32)
    return np.kron(img, np.ones((4, 4), np.float32))[:h + 4, :w + 4]   # coarse texture: a shift is visible


def test_camera_pan_is_compensated():
    big = texture()
    a, b = big[2:144, 2:82], big[2:144, 4:84]          # 2 px pan
    raw, res = sg.aligner(80, 142).residual(a, b)
    assert raw > 5 and res < 0.3 * raw


def test_subject_action_survives_compensation():
    a = texture()[2:144, 2:82]
    b = a.copy()
    b[50:90, 20:60] = texture(seed=1)[50:90, 20:60]     # something changed by itself in the centre
    raw, res = sg.aligner(80, 142).residual(a, b)
    assert res > 0.5 * raw


def test_freeze_frame_is_flagged_still():
    F = np.stack([texture()[2:144, 2:82]] * 12)        # 3 s of a freeze frame
    sc = sg.action(F, 4.0, [(0, 3.0)], sg.aligner(80, 142))
    assert sc[0]['flag'] == 'still'


def test_return_counted_and_loop_tail_skipped():
    A, B = np.zeros((4, 4)), np.full((4, 4), 100.0)
    T = np.stack([A] * 3 + [B] * 6 + [A] * 3)          # A comes back after 9 s
    r = sg.repeats(T)
    assert r['repeat_seconds'] == 3 and r['spans'][0]['at'] == 9
    assert sg.repeats(T, tail_skip=3)['repeat_seconds'] == 0   # a loop: the tail equals the start on purpose


def test_no_repeat_in_distinct_frames():
    T = np.stack([np.full((4, 4), 20.0 * i) for i in range(12)])
    assert sg.repeats(T)['repeat_seconds'] == 0


@needs_ffmpeg
def test_cli_on_clip_warns_but_exits_zero(tmp_path, capsys):
    frames = np.full((30 * 10, 180, 320), 60, np.uint8)   # 10 s freeze frame: still and repeating
    mp4 = tmp_path / 'still.mp4'
    encode_frames(frames, mp4)
    out = tmp_path / 'r.json'
    assert sg.main([str(mp4), '--json', str(out)]) == 0
    r = json.loads(out.read_text())
    assert r['verdict'] == 'warn' and r['still_share'] == 1.0 and r['repeat_share'] > 0.1


def test_missing_file_exits_one(tmp_path):
    assert sg.main([str(tmp_path / 'nope.mp4')]) == 1
