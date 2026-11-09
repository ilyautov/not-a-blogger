"""picture_checks: hook motion and single-frame flashes on synthetic clips (ffmpeg lavfi, no project)."""
import json

import numpy as np
import pytest

from conftest import encode_frames, ffmpeg, load, needs_ffmpeg

pc = load('qa', 'picture_checks')
pytestmark = needs_ffmpeg


@pytest.fixture(scope='module')
def clips(tmp_path_factory):
    d = tmp_path_factory.mktemp('pc')
    still, moving, flash = d / 'still.mp4', d / 'moving.mp4', d / 'flash.mp4'
    ffmpeg('-f', 'lavfi', '-i', 'color=c=gray:s=320x180:r=30:d=3', '-pix_fmt', 'yuv420p', still)
    ffmpeg('-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=30:d=3', '-pix_fmt', 'yuv420p', moving)
    frames = np.full((90, 180, 320), 128, np.uint8)
    frames[45] = 255                                     # one white frame in a grey clip
    encode_frames(frames, flash)
    return still, moving, flash


def test_hook_still_fails(clips):
    h = pc.hook_motion(clips[0])
    assert not h['ok'] and h['mean'] < 0.1


def test_hook_moving_passes(clips):
    assert pc.hook_motion(clips[1])['ok']


def test_pop_found_on_the_flash_frame(clips):
    r = pc.frame_pops(clips[2])
    assert r['count'] == 1 and r['pops'][0]['frame'] == 45


def test_no_pops_in_still_or_moving(clips):
    assert pc.frame_pops(clips[0])['count'] == 0
    assert pc.frame_pops(clips[1])['count'] == 0


def test_cli_warns_with_exit_zero_and_strict_two(clips, tmp_path, capsys):
    out = tmp_path / 'p.json'
    assert pc.main([str(clips[0]), '--json', str(out)]) == 0
    assert 'hook_motion' in json.loads(out.read_text())['warnings']
    assert pc.main([str(clips[0]), '--strict']) == 2
    assert pc.main([str(clips[1]), '--strict']) == 0
