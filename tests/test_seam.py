"""seam: стык петли на синтетических кадрах и на закодированном mp4."""
import numpy as np

from conftest import encode_frames, load, needs_ffmpeg

sm = load('qa', 'seam')


def _ramp(h=48, w=32):
    """Полоса едет вниз на 1 px за кадр с заворотом: последний кадр в одном шаге от первого."""
    base = np.zeros((h, w), np.float32)
    base[:6] = 255
    return np.stack([np.roll(base, i, axis=0) for i in range(h)])


def test_seamless_loop_ratio_near_one():
    r = sm.seam_stats(_ramp())
    assert r['ratio'] <= 2.0


def test_jump_at_seam_detected():
    f = _ramp()
    f[-1] = 255 - f[-1]                    # последний кадр резко другой
    assert sm.seam_stats(f)['ratio'] > 5


@needs_ffmpeg
def test_main_on_mp4(tmp_path):
    p = tmp_path / 'loop.mp4'
    encode_frames(_ramp().astype(np.uint8), p)
    assert sm.main([str(p), '--json']) == 0
    f = _ramp()
    f[-3:] = 255
    q = tmp_path / 'bad.mp4'
    encode_frames(f.astype(np.uint8), q)
    assert sm.main([str(q)]) == 1
