"""motion_lint на фикстурах GSAP, still_lint на синтетической Canvas-сцене с контрактом setTime."""
import json
import textwrap

import pytest

from conftest import load

ml = load('lint', 'motion_lint')

FLAT = """
const tl = gsap.timeline();
tl.to('.card', {opacity: 1, duration: 0.5, ease: 'power2.out'}, 0);
tl.to('.card2', {opacity: 1, duration: 0.5, ease: 'power2.out'}, 1);
"""

GOOD = """
const tl = gsap.timeline();
tl.from('.title', {y: 80, opacity: 0, duration: 0.4, ease: 'power4.out'}, 0)
  .from('.word', {x: -40, opacity: 0, duration: 1.6, ease: 'sine.inOut', stagger: 0.05}, 0.4)
  .to('#world', {scale: 1.2, duration: 3.0, ease: 'expo.inOut'}, 1.2)
  .to('#world', {xPercent: -10, duration: 0.2, ease: 'power1.in'}, 4.5)
  .from('.badge', {scale: 0, rotation: -20, duration: 0.7, ease: 'back.out(2)'}, 2)
  .to('.bg', {filter: 'blur(6px)', duration: 2.4, ease: 'circ.out'}, 3)
  .to('.count', {yPercent: 50, duration: 0.25, ease: 'expo.out'}, 5.2)
  .to('.end', {opacity: 0, duration: 1.1, ease: 'sine.in'}, 6.3);
"""


def test_flat_scene_fails(tmp_path):
    rep, checks = ml.analyse(FLAT, 10)
    failed = [k for k, v in checks.items() if not v]
    assert 'ease_families>=4' in failed and 'camera_tweens>=2' in failed
    p = tmp_path / 'scene.js'; p.write_text(FLAT)
    assert ml.main([str(p), '--duration', '10']) == 1


def test_good_scene_passes(tmp_path):
    rep, checks = ml.analyse(GOOD, 15)
    assert all(checks.values()), [k for k, v in checks.items() if not v]
    p = tmp_path / 'scene.js'; p.write_text(GOOD)
    story = tmp_path / 'story.json'; story.write_text(json.dumps({'duration': 15}))
    out = tmp_path / 'qa' / 'ml.json'
    assert ml.main([str(p), '--story', str(story), '--out', str(out)]) == 0
    assert json.loads(out.read_text())['ok'] is True


def test_random_fails():
    _, checks = ml.analyse(GOOD + "\nconst j = Math.random();", 15)
    assert checks['no_random_or_clock'] is False


def test_custom_camera_selector():
    src = GOOD.replace('#world', '#cam')
    assert ml.analyse(src, 15, camera='#world')[1]['camera_tweens>=2'] is False
    assert ml.analyse(src, 15, camera='#cam')[1]['camera_tweens>=2'] is True


# ---------- still_lint ----------
def _playwright_ok():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


SCENE = textwrap.dedent("""
<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#000}</style>
<canvas id="c" width="360" height="640"></canvas>
<script>
const FREEZE = %s;            // [от, до] — отрезок, где кадр замирает
const c = document.getElementById('c').getContext('2d');
window.shotTimes = [0, 4];
window.setTime = async (t) => {
  if (FREEZE && t > FREEZE[0] && t < FREEZE[1]) t = FREEZE[0];
  c.fillStyle = '#123'; c.fillRect(0, 0, 360, 640);
  c.fillStyle = '#fd4'; c.fillRect(20 + (t * 40) %% 280, 200, 60, 60);
};
window.setTime(0).then(() => { window.ready = true; });
</script>
""")


@pytest.fixture(scope='module')
def browser_ok():
    if not _playwright_ok():
        pytest.skip('нет Chromium для Playwright (playwright install chromium)')


def _project(tmp_path, freeze):
    (tmp_path / 'index.html').write_text(SCENE % (json.dumps(freeze) if freeze else 'null'))
    (tmp_path / 'story.json').write_text(json.dumps({'duration': 12, 'width': 360, 'height': 640}))
    return tmp_path


def test_still_spans_and_samples():
    sl = load('lint', 'still_lint')
    assert sl.scene_spans([4, 0], 12) == [(0, 4), (4, 12)]
    assert sl.scene_spans([], 5) == [(0.0, 5)]
    times, idx = sl.sample_times([(0, 0.6)], 0.5)
    assert len(times) == 1


def test_still_lint_live_scene_clean(tmp_path, browser_ok):
    sl = load('lint', 'still_lint')
    r = sl.run(_project(tmp_path, None), step=0.5, max_still=3.0)
    assert r['scenes'] == 2 and r['bad'] == 0


def test_still_lint_frozen_segment(tmp_path, browser_ok):
    sl = load('lint', 'still_lint')
    r = sl.run(_project(tmp_path, [6, 10]), step=0.5, max_still=3.0)
    assert r['bad'] == 1
    bad = [x for x in r['rows'] if x['verdict'] != 'ok'][0]
    assert bad['scene'] == 1 and 3.5 <= bad['still'] <= 4.5
    assert (tmp_path / 'qa' / 'still' / 'contact.jpg').exists()
    assert sl.main([str(tmp_path)]) == 1
