"""motion_lint на фикстурах GSAP, still_lint на синтетической Canvas-сцене с контрактом setTime."""
import json
import textwrap
import subprocess
import sys
import os
import shutil

import pytest

from conftest import load, ROOT, TOOLS

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
    assert sl.sample_times([(0, 3)], .5) == ([.5, 1.0, 1.5, 2.0, 2.5], [0] * 5)


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


@pytest.mark.parametrize('step', ['0', '-1', 'nan', 'inf', '-inf'])
def test_sample_times_rejects_invalid_step_without_looping(step):
    # Bound the real public call so a regression cannot hang the test runner.
    code = f'''import runpy
sample = runpy.run_path({str(TOOLS / 'lint' / 'still_lint.py')!r})['sample_times']
try:
    sample([(0, 5)], float({step!r}))
except ValueError as e:
    assert 'step' in str(e)
else:
    raise AssertionError('invalid step accepted')
'''
    result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=3)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('field,value', [('step', 0), ('step', -1), ('step', float('nan')),
    ('step', float('inf')), ('max_still', -1), ('max_still', float('nan')), ('max_still', float('inf')),
    ('threshold', -1), ('threshold', float('nan')), ('threshold', float('inf'))])
def test_run_rejects_parameters_before_opening_browser(tmp_path, monkeypatch, field, value):
    sl = load('lint', 'still_lint')
    monkeypatch.setattr(sl, 'shoot', lambda *a, **kw: pytest.fail('browser opened for invalid input'))
    with pytest.raises(ValueError, match=field):
        sl.run(_project(tmp_path, None), **{field: value})


@pytest.mark.parametrize('args', [['--step', '0'], ['--step', '-1'], ['--step', 'nan'], ['--step', 'inf'],
    ['--threshold', '-1'], ['--threshold', 'nan'], ['--threshold', 'inf'],
    ['--max-still', '-1'], ['--max-still', 'nan'], ['--max-still', 'inf']])
def test_still_cli_explains_invalid_parameters_without_loading_scene(tmp_path, args):
    result = subprocess.run([sys.executable, str(TOOLS / 'lint' / 'still_lint.py'), str(tmp_path), *args],
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 2
    assert args[0][2:].replace('-', '_') in result.stderr
    assert 'finite' in result.stderr and 'Traceback' not in result.stderr


CAMERA_SCENE = '''<!doctype html><style>body{margin:0}canvas{display:block}</style>
<canvas width="360" height="640"></canvas><script>
const c = document.querySelector('canvas').getContext('2d');
let qa = false;
window.setQAMode = enabled => {qa = enabled};
window.setTime = async t => {
  c.resetTransform(); c.fillStyle = '#123'; c.fillRect(0, 0, 360, 640);
  if (!qa) {c.translate(t * 16, 0); c.scale(1 + t * .02, 1 + t * .02)}
  c.fillStyle = '#fd4'; c.fillRect(20 + OBJECT_SPEED * t, 200, 60, 60);
  // Camera/postprocessing alone must not count as moving the object.
  if (!qa) {c.resetTransform(); c.fillStyle = t % 1 ? '#182838' : '#283848'; c.fillRect(0, 0, 360, 70)}
};
window.ready = true;
</script>'''


@pytest.mark.parametrize('object_speed,bad', [(0, 1), (20, 0)])
def test_canvas_qa_mode_distinguishes_camera_from_object_motion(tmp_path, browser_ok, object_speed, bad):
    sl = load('lint', 'still_lint')
    _project(tmp_path, None)
    (tmp_path / 'index.html').write_text(CAMERA_SCENE.replace('OBJECT_SPEED', str(object_speed)))
    r = sl.run(tmp_path, shot_times=[0])
    assert r['bad'] == bad
    assert r['camera_control']['method'] == 'setQAMode'
    kept = sl.run(tmp_path, keep_camera=True, shot_times=[0])
    assert kept['bad'] == 0 and kept['camera_control']['method'] == 'kept'


def test_camera_control_reports_unsupported_and_preserves_pre_js(tmp_path, browser_ok):
    sl = load('lint', 'still_lint')
    r = sl.run(_project(tmp_path, None), shot_times=[0])
    assert r['camera_control']['method'] == 'unsupported'
    assert r['camera_control']['warning']
    r = sl.run(tmp_path, pre_js='window.setTime(0)', shot_times=[0])
    assert r['bad'] == 1 and r['camera_control']['pre_js'] is True


def test_dom_camera_fallback_still_works(tmp_path, browser_ok):
    sl = load('lint', 'still_lint')
    _project(tmp_path, None)
    (tmp_path / 'index.html').write_text('''<!doctype html><style>body{margin:0;background:#123}
    #world{width:60px;height:60px;background:#fd4;margin:200px 20px}</style><div id="world"></div>
    <script>window.setTime = async t => {document.querySelector('#world').style.transform=`translateX(${t*20}px)`};
    window.ready = true;</script>''')
    r = sl.run(tmp_path, shot_times=[0])
    assert r['bad'] == 1 and r['camera_control']['method'] == 'dom-world'
    assert sl.run(tmp_path, keep_camera=True, shot_times=[0])['bad'] == 0


@pytest.mark.parametrize('source,lines', [
    ('scene/scene.ts', [('кода', 'без', 'монтажки'), ('голос', 'кадры', 'звук', 'пару'), ('200', 'строк', 'повтори')]),
    ('examples/subscription/scene.ts', [('200',), ('продление',), ('0',), ('чек',)])])
def test_bundled_canvas_qa_mode_is_reversible(tmp_path, browser_ok, source, lines):
    tsc = os.environ.get('TSC') or shutil.which('tsc')
    if not tsc:
        local = ROOT / 'starter/node_modules/.bin/tsc'
        if local.exists():
            tsc = str(local)
        else:
            pytest.skip('TypeScript compiler missing; run npm ci in starter')
    words, cues = [], []
    for i, line in enumerate(lines):
        start = i * 3
        cues.append({'id': i, 'start': start, 'end': start + 2.8, 'text': ' '.join(line)})
        for j, text in enumerate(line):
            at = start + .6 + j * .5
            words.append({'line': i, 'text': text, 'start': at, 'end': at + .35})
    (tmp_path / 'story.json').write_text(json.dumps({'duration': 14, 'cues': cues, 'words': words}))
    (tmp_path / 'index.html').write_text('''<!doctype html><meta charset="utf-8"><style>body{margin:0}canvas{display:block}</style>
    <canvas id="film" width="1080" height="1920"></canvas><script src="scene.js"></script>''')
    subprocess.run([tsc, str(ROOT / 'starter' / source), '--target', 'ES2020', '--lib', 'DOM,ES2020',
                    '--strict', '--skipLibCheck', '--outFile', str(tmp_path / 'scene.js')], check=True,
                   capture_output=True, timeout=30)
    sl = load('lint', 'still_lint')
    normal, _, _ = sl.shoot(tmp_path, [11.5, 12.5], 1080, 1920, keep_camera=True)
    qa, _, control = sl.shoot(tmp_path, [11.5, 12.5], 1080, 1920)
    restored, _, _ = sl.shoot(tmp_path, [11.5], 1080, 1920,
                              pre_js='window.setQAMode(false); window.setTime(11.5)')
    assert control['method'] == 'setQAMode' and normal[0] != qa[0]
    assert restored[0] == normal[0], 'turning QA mode off must restore the authored render'
    if source == 'scene/scene.ts':
        assert qa[0] == qa[1], 'settled objects must not move from hidden camera/noise in QA mode'
        assert normal[0] != normal[1], 'normal render retains authored camera/noise'
