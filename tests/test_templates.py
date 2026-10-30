"""Smoke tests for templates/: each template runs end to end on placeholders, in a temp copy.

Heavy steps skip when their tool is missing (Playwright Chromium, ffmpeg, tsc, soundfile). Nothing here downloads
models or calls a real CLI: the experiment runs against a fake `claude`.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'templates'
PY = sys.executable


def has(mod):
    return importlib.util.find_spec(mod) is not None


def chromium_ok():
    if not has('playwright'): return False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


CHROMIUM = chromium_ok()
needs_audio = pytest.mark.skipif(not has('soundfile'), reason='no soundfile')
needs_chromium = pytest.mark.skipif(not CHROMIUM, reason='no Playwright Chromium')


def copy(name, tmp_path):
    dst = tmp_path / name
    shutil.copytree(T / name, dst, ignore=shutil.ignore_patterns('__pycache__', 'output', 'stills', 'audio', 'timeline.json', 'runs'))
    return dst


def run(args, cwd, ok=True, **kw):
    r = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, timeout=600, **kw)
    if ok: assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return r


def not_flat(jpg: Path):
    """A rendered still is not a blank frame: pixel spread via Pillow if installed, else a file-size floor."""
    assert jpg.exists() and jpg.stat().st_size > 8000, jpg
    if has('PIL'):
        from PIL import Image
        a = np.asarray(Image.open(jpg).convert('L'), dtype=np.float32)
        assert a.std() > 8, f'{jpg.name}: almost uniform image (std {a.std():.1f})'


# ---------------------------------------------------------------- hygiene (always runs)

def test_templates_hygiene():
    bad_ext = {'.mp4', '.mov', '.wav', '.mp3', '.png', '.jpg', '.jpeg', '.safetensors', '.pt', '.ckpt', '.onnx', '.hdr'}
    files = [p for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    assert not [p for p in files if p.suffix.lower() in bad_ext], 'binary media in templates/'
    for p in files:
        if p.suffix in {'.js', '.ts', '.py', '.json', '.md', '.html', '.sh', '.tsv'} and 'vendor' not in p.parts:
            s = p.read_text(errors='ignore')
            assert '/' + 'Users/' not in s, f'absolute user path in {p}'
            assert '#d6ff43' not in s.lower(), f'author brand color in {p}'
    for d in ('3d-skit', 'skit', 'data-reel', 'experiment', 'real-tool-reel'):
        assert (T / d / 'README.md').exists(), d
    assert (T / 'THIRD-PARTY.md').exists() and (T / '3d-skit/vendor/three/LICENSE').exists()


# ---------------------------------------------------------------- 3d-skit

@needs_audio
def test_3d_skit_timeline(tmp_path):
    d = copy('3d-skit', tmp_path)
    run([PY, 'build_timeline.py'], d)
    tl = json.loads((d / 'timeline.json').read_text())
    script = json.loads((d / 'script.json').read_text())
    assert len(tl['lines']) == len(script['lines'])
    assert all(s['end'] - s['start'] >= 0.4 for s in tl['shots'])
    assert tl['duration'] > tl['lines'][-1]['end']
    assert all(len(l['env']) > 0 and max(l['env']) <= 1.0 for l in tl['lines'])
    assert (d / 'audio/mix.wav').exists()


@needs_audio
@needs_chromium
@pytest.mark.parametrize('style', ['voxel', 'ps1', 'clean'])
def test_3d_skit_still(tmp_path, style):
    d = copy('3d-skit', tmp_path)
    run([PY, 'build_timeline.py', '--no-audio'], d)
    run([PY, 'render.py', '--style', style, '--stills', '2', '--out', d / 'stills'], d)
    shots = sorted((d / 'stills').glob(f'{style}-*.jpg'))
    assert shots, list((d / 'stills').iterdir())
    not_flat(shots[0])


# ---------------------------------------------------------------- skit

@needs_audio
def test_skit_timeline(tmp_path):
    d = copy('skit', tmp_path)
    run([PY, 'build_audio.py'], d)
    tl = json.loads((d / 'timeline.json').read_text())
    assert all(s['end'] - s['start'] >= 0.5 for s in tl['shots'])
    assert tl['marks'], 'events on words were not found'
    assert all(l['words'] for l in tl['lines'])
    assert (d / 'audio/mix.wav').exists()


@needs_audio
def test_skit_asr_times_follow_trimmed_take(tmp_path, monkeypatch):
    """A take with 1 s of leading silence: ASR word times are shifted onto the trimmed audio used in the mix."""
    import soundfile as sf
    spec = importlib.util.spec_from_file_location('skit_build_audio', T / 'skit/build_audio.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    sr = 24000
    t = np.arange(int(0.8 * sr)) / sr
    x = np.concatenate([np.zeros(sr), 0.5 * np.sin(2 * np.pi * 220 * t), np.zeros(sr // 2)])
    take = tmp_path / 'take.wav'; sf.write(take, x, sr)
    y, offset = m.load_take(take)
    assert abs(offset - 0.96) < 0.02                                   # 1 s minus the 40 ms pre-roll
    # fake ASR on the ORIGINAL file: speech 1.0-1.8 s, plus a hallucinated word in the silence
    monkeypatch.setattr(m, 'asr_words', lambda path, lang: [['uh', 0.1, 0.3], ['hello', 1.0, 1.4], ['there', 1.4, 1.8]])
    words = m.take_words(take, 'hello there', y, offset, True, 'en')
    assert [w for w, _, _ in words] == ['hello', 'there']
    assert abs(words[0][1] - 0.04) < 0.02 and abs(words[1][2] - 0.84) < 0.02
    assert all(0 <= s <= e <= len(y) / m.SR for _, s, e in words)

@needs_audio
@needs_chromium
def test_skit_still(tmp_path):
    d = copy('skit', tmp_path)
    run([PY, 'build_audio.py'], d)
    run([PY, 'render.py', '--stills', '2', '--out', d / 'stills'], d)
    shots = sorted((d / 'stills').glob('*.jpg'))
    assert shots
    not_flat(shots[0])


# ---------------------------------------------------------------- data-reel

def fake_tree(root: Path):
    """A small folder tree with known sizes: no real user data."""
    (root / 'Videos').mkdir(parents=True); (root / 'Archives').mkdir(); (root / 'Notes 2024').mkdir()
    (root / 'Videos/clip.mp4').write_bytes(b'\0' * 3_000_000)
    (root / 'Videos/old.mov').write_bytes(b'\0' * 1_000_000)
    os.utime(root / 'Videos/old.mov', (1_500_000_000, 1_500_000_000))
    (root / 'Archives/backup.zip').write_bytes(b'\0' * 2_000_000)
    (root / 'Notes 2024/a.md').write_bytes(b'x' * 400_000)
    (root / 'loose.pdf').write_bytes(b'x' * 100_000)


def data_reel(tmp_path):
    d = copy('data-reel', tmp_path)
    fake_tree(tmp_path / 'Target')
    run([PY, 'measure_folders.py', tmp_path / 'Target'], d)
    run([PY, 'reel_from_numbers.py'], d)
    return d


def test_data_reel_measure_and_generate(tmp_path):
    d = data_reel(tmp_path)
    n = json.loads((d / 'real-numbers.json').read_text())
    assert n['target_label'] == 'Target' and str(tmp_path) not in json.dumps(n)       # no full path in the file
    assert n['files'] == 5 and n['total_bytes'] == 6_500_000
    assert n['by_folder'][0]['name'] == 'Videos' and n['by_kind']['video']['files'] == 2
    assert n['older_than_1y_gb'] == 0.0 and n['older_than_1y_share'] == round(1_000_000 / 6_500_000, 3)
    run([PY, 'measure_folders.py', tmp_path / 'Target', '--hide-names', '--out', tmp_path / 'h.json'], d)
    assert all(f['name'].startswith('Folder ') for f in json.loads((tmp_path / 'h.json').read_text())['by_folder'])
    lines = json.loads((d / 'voice/lines.json').read_text())
    chunks = json.loads((d / 'voice/chunks.json').read_text())
    reel = json.loads((d / 'reel.json').read_text())
    assert len(lines) == len(chunks) == 5 and not any(re.search(r'\{[a-z_]+\}', l) for l in lines)
    assert reel['n']['fmt']['total_gb'] in lines[0] and 'Target' in lines[0]
    assert run([PY, 'check_numbers.py'], d).returncode == 0


def test_data_reel_gate_catches_typed_number(tmp_path):
    d = data_reel(tmp_path)
    lines = json.loads((d / 'voice/lines.json').read_text())
    lines[3] = 'Ровно 73 процента не менялось.'                         # a number nobody measured
    (d / 'voice/lines.json').write_text(json.dumps(lines, ensure_ascii=False))
    r = run([PY, 'check_numbers.py'], d, ok=False)
    assert r.returncode == 1 and '73' in r.stdout



def load_measure():
    spec = importlib.util.spec_from_file_location('measure_folders', T / 'data-reel/measure_folders.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def test_data_reel_du_uses_one_metric(tmp_path):
    """--du: totals, folders, kinds and "old" all in allocated bytes, so shares add up and never pass 100 %."""
    fake_tree(tmp_path / 'Target')
    with open(tmp_path / 'Target/Videos/sparse.mp4', 'wb') as f:      # 50 MB logical, almost nothing allocated
        f.truncate(50_000_000)
    os.utime(tmp_path / 'Target/Videos/sparse.mp4', (1_500_000_000, 1_500_000_000))
    out = tmp_path / 'du.json'
    run([PY, T / 'data-reel/measure_folders.py', tmp_path / 'Target', '--du', '--out', out], tmp_path)
    n = json.loads(out.read_text())
    alloc = sum(os.lstat(p).st_blocks * 512 for p in (tmp_path / 'Target').rglob('*') if p.is_file())
    assert n['size_metric'] == 'allocated' and n['total_bytes'] == alloc
    assert n['total_bytes'] < 50_000_000                                  # sparse file counted by blocks, not size
    assert abs(sum(k['share'] for k in n['by_kind'].values()) - 1) < 0.01
    assert all(0 <= f['share'] <= 1 for f in n['by_folder']) and 0 <= n['older_than_1y_share'] <= 1
    kinds_gb = sum(k['gb'] for k in n['by_kind'].values())
    assert abs(kinds_gb - n['total_gb']) < 0.02
    run([PY, T / 'data-reel/measure_folders.py', tmp_path / 'Target', '--out', out], tmp_path)
    assert json.loads(out.read_text())['size_metric'] == 'logical'


def test_data_reel_unreadable_dir_marks_incomplete(tmp_path, monkeypatch):
    m = load_measure()
    fake_tree(tmp_path / 'Target')
    real_walk = os.walk

    def walk_with_denied(top, onerror=None, followlinks=False):
        onerror(PermissionError(13, 'Permission denied', str(Path(top) / 'secret')))
        yield from real_walk(top, onerror=onerror, followlinks=followlinks)

    monkeypatch.setattr(m.os, 'walk', walk_with_denied)
    w = m.walk(tmp_path / 'Target/Videos', 0)
    assert w['skipped_dirs'] == 1 and w['files'] == 2


@pytest.mark.skipif(not hasattr(os, 'geteuid') or os.geteuid() == 0, reason='root reads everything')
def test_data_reel_incomplete_flows_through_pipeline(tmp_path):
    d = copy('data-reel', tmp_path)
    fake_tree(tmp_path / 'Target')
    locked = tmp_path / 'Target/Videos/locked'; locked.mkdir(); (locked / 'big.mov').write_bytes(b'\0' * 1000)
    locked.chmod(0)
    try:
        r = run([PY, 'measure_folders.py', tmp_path / 'Target'], d)
    finally:
        locked.chmod(0o755)
    n = json.loads((d / 'real-numbers.json').read_text())
    assert n['complete'] is False and n['unreadable_dirs'] == 1 and n['unreadable_entries'] == 1
    assert 'incomplete' in r.stderr
    r = run([PY, 'reel_from_numbers.py'], d, ok=False)
    assert r.returncode != 0 and 'incomplete' in r.stderr and not (d / 'reel.json').exists()
    run([PY, 'reel_from_numbers.py', '--allow-incomplete'], d)
    reel = json.loads((d / 'reel.json').read_text())
    assert 'incomplete' in reel['source'] and reel['measurement_incomplete'] == 1
    assert run([PY, 'check_numbers.py'], d).returncode == 0
    reel.pop('measurement_incomplete'); (d / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False))
    r = run([PY, 'check_numbers.py'], d, ok=False)
    assert r.returncode == 1 and 'incomplete' in r.stdout
    reel['measurement_incomplete'] = 1; reel['source'] = 'all folders measured'     # visible caveat removed
    (d / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False))
    r = run([PY, 'check_numbers.py'], d, ok=False)
    assert r.returncode == 1 and 'source line' in r.stdout


def test_data_reel_du_counts_hardlink_once(tmp_path):
    t = tmp_path / 'Target'; (t / 'a').mkdir(parents=True); (t / 'b').mkdir()
    (t / 'a/big.mov').write_bytes(os.urandom(200_000)); os.link(t / 'a/big.mov', t / 'b/same.mov')
    work = tmp_path / 'w'; work.mkdir()
    run([PY, T / 'data-reel/measure_folders.py', t, '--du'], work)
    du = json.loads((work / 'real-numbers.json').read_text())
    run([PY, T / 'data-reel/measure_folders.py', t], work)
    plain = json.loads((work / 'real-numbers.json').read_text())
    assert du['files'] == 1 and du['total_bytes'] < 2 * 200_000      # one inode, counted once (like du)
    assert plain['files'] == 2 and plain['total_bytes'] == 400_000    # logical sizes: every name counts

def find_tsc():
    for c in (os.environ.get('TSC'), shutil.which('tsc'), str(ROOT / 'starter/node_modules/.bin/tsc')):
        if c and Path(c).exists(): return c
    return None


@pytest.mark.skipif(find_tsc() is None, reason='no tsc (set TSC=/path/to/tsc)')
def test_data_reel_scene_compiles(tmp_path):
    d = data_reel(tmp_path)
    st = tmp_path / 'starter'
    shutil.copytree(ROOT / 'starter', st, ignore=shutil.ignore_patterns('node_modules', 'output', 'build', 'qa', '__pycache__', '*.wav'))
    run([PY, d / 'reel_from_numbers.py', '--numbers', d / 'real-numbers.json', '--into', st], d)
    shutil.copy(d / 'scene.ts', st / 'scene/scene.ts')
    run([find_tsc(), '-p', 'scene'], st)
    assert (st / 'build/scene.js').exists()
    if not (CHROMIUM and has('soundfile')): return
    run([PY, 'voice/fake_track.py'], st)
    run([PY, 'tools/render.py', '--probe'], st)
    ev = json.loads((st / 'qa/events.json').read_text()); shots = json.loads((st / 'qa/shots.json').read_text())
    assert set(ev) == {'total', 'top', 'kinds', 'old'} and len(shots) == 5 and shots == sorted(shots)


# ---------------------------------------------------------------- experiment

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, sys
if '--version' in sys.argv: print('0.0.0 (fake)'); sys.exit(0)
sp = sys.argv[sys.argv.index('--system-prompt') + 1]
good = ["10063", "6", "apple, banana, fig, pear", "Saturday", "MCMXCIV"]
ans = good if 'career' in sp else good[:4] + ["MCMXCVI"]
print(json.dumps({"result": json.dumps({"answers": ans}), "modelUsage": {"fake-model-1": {}}}))
'''


def test_experiment_with_fake_cli(tmp_path):
    d = copy('experiment', tmp_path)
    fake = tmp_path / 'claude'; fake.write_text(FAKE_CLAUDE); fake.chmod(0o755)
    dry = run([PY, 'run.py', '--dry-run', '--n', '1', '--models', 'm', '--claude-bin', fake], d)
    assert dry.stdout.count('would run:') == 2 and not (d / 'runs').exists()
    run([PY, 'run.py', '--n', '2', '--models', 'm', '--claude-bin', fake], d)
    runs = sorted((d / 'runs').glob('*.json'))
    assert [p.name for p in runs] == ['A-control-m-1.json', 'A-control-m-2.json', 'B-advice-m-1.json', 'B-advice-m-2.json']
    rec = json.loads(runs[0].read_text())
    assert rec['returncode'] == 0 and '<system_prompt>' in rec['command'] and rec['cli'] == '0.0.0 (fake)'
    res = (d / 'results.md').read_text()
    assert re.search(r'\| A-control \| fake-model-1 \| 2 \| 0 \| 4\.00 \| 4–4 \|', res), res
    assert re.search(r'\| B-advice \| fake-model-1 \| 2 \| 0 \| 5\.00 \| 5–5 \|', res), res
    again = run([PY, 'run.py', '--n', '2', '--models', 'm', '--claude-bin', fake], d)
    assert again.stdout.count('skip') == 4                                  # resumes, does not overwrite


# ---------------------------------------------------------------- real-tool-reel

def load_nag():
    spec = importlib.util.spec_from_file_location('focus_nag', T / 'real-tool-reel/tool/focus_nag.py')
    m = importlib.util.module_from_spec(spec)
    sys.modules['focus_nag'] = m                     # dataclasses look the module up while the class is built
    spec.loader.exec_module(m); return m


def test_focus_nag_logic():
    m = load_nag()
    assert m.is_blocked('https://m.youtube.com/x', ['youtube.com'])
    assert not m.is_blocked('https://notyoutube.com', ['youtube.com'])
    assert not m.is_blocked(None, ['youtube.com'])
    z = m.Nag(blocklist=['youtube.com'], lines=['say:1', 'say:2', 'say:3'], work_url='https://example.com/', reset_after_s=100, nag_every_s=20)
    assert [a.arg for a in z.step('Safari', 'https://youtube.com', 0)] == ['say:1']
    assert z.step('Safari', 'https://youtube.com', 5) == []                 # still there, too soon
    assert [a.arg for a in z.step('Safari', 'https://youtube.com', 25)] == ['say:2']   # stayed: nag again
    assert z.step('Terminal', None, 30) == []
    assert [a.kind for a in z.step('Safari', 'https://youtube.com', 31)] == ['say', 'close_tab', 'open'] and z.strikes == 0
    z.step('Safari', 'https://youtube.com', 40); z.step('Safari', 'https://example.com', 41)
    assert [a.arg for a in z.step('Safari', 'https://youtube.com', 200)] == ['say:1']  # reset after quiet time


def test_focus_nag_dry_run_is_default(tmp_path):
    d = copy('real-tool-reel', tmp_path)
    r = run([PY, 'tool/focus_nag.py', '--feed', 'tool/demo.tsv'], d)
    assert r.stdout.count('-> say') == 3 and '-> close_tab' in r.stdout and '-> open https://example.com/' in r.stdout
    r = run([PY, 'tool/focus_nag.py'], d, input='Safari https://www.tiktok.com/\n')
    assert '-> say say:Again?' in r.stdout



def test_focus_nag_live_close_rechecks_tab(monkeypatch):
    """--live: after the line plays, the tab is closed only if the same browser, the same tab and URL are in front."""
    m = load_nag()
    calls = []
    state = {'app': 'Safari', 'url': 'https://youtube.com/watch?v=1', 'tab': '7:2'}

    def fake_run(cmd, timeout=3):
        calls.append(cmd)
        if cmd[0] == 'osascript':
            script = cmd[-1]
            if 'close t' in script:          # emulate the AppleScript: close only the same tab with the same URL
                same = m._as_str(state['tab']) in script and m._as_str(state['url']) in script
                return 'closed' if same else 'kept'
            if 'return (id of w' in script:
                return state['tab']
            return state['url']
        return ''

    monkeypatch.setattr(m, '_run', fake_run)
    monkeypatch.setattr(m, 'front_app', lambda: state['app'])
    mac = m.Mac({'Safari': 'safari', 'Google Chrome': 'chrome'})
    z = m.Nag(blocklist=['youtube.com'], lines=['say:1'], work_url='https://example.com/')
    acts = z.step(*mac.observe(), 0)
    close = next(a for a in acts if a.kind == 'close_tab')
    assert close.url == state['url'] and mac.seen_tab == '7:2'

    state['url'] = 'https://docs.example.com/my-work'     # user switched tab while the line played
    assert mac.do(close) is False
    state.update(url='https://youtube.com/watch?v=1', tab='7:3')   # another tab with the same URL
    assert mac.do(close) is False
    state.update(tab='7:2', app='Terminal')               # or switched app entirely
    n = len(calls)
    assert mac.do(close) is False and len(calls) == n      # nothing sent to the browser
    state['app'] = 'Safari'
    assert mac.do(close) is True                           # still the same tab: closed
    script = calls[-1][-1]
    assert 'current tab of w' in script and '"https://youtube.com/watch?v=1"' in script and '"7:2"' in script
    assert m._as_str('a"b\\c') == '"a\\"b\\\\c"'
    assert mac.do(m.Action('close_tab', browser='Safari')) is False   # no recorded URL: never close blindly
    mac.seen_tab = None
    assert mac.do(close) is False                          # tab identity unknown: never close blindly

# ---------------------------------------------------------------- hygiene of outputs and config (audit 2026-10-24)

def test_data_reel_default_out_is_cwd_not_repo(tmp_path):
    """Default --out lands in the working folder: personal folder names never appear in the repo tree."""
    fake_tree(tmp_path / 'Target')
    work = tmp_path / 'work'; work.mkdir()
    run([PY, T / 'data-reel/measure_folders.py', tmp_path / 'Target'], work)
    assert (work / 'real-numbers.json').exists()
    assert not (T / 'data-reel/real-numbers.json').exists()


def test_gitignore_covers_template_outputs():
    gi = (ROOT / '.gitignore').read_text()
    assert 'templates/data-reel/real-numbers.json' in gi and 'templates/**/output/' in gi


def test_experiment_temp_cwd_is_removed(tmp_path):
    d = copy('experiment', tmp_path)
    fake = tmp_path / 'claude'; fake.write_text(FAKE_CLAUDE); fake.chmod(0o755)
    tmpdir = tmp_path / 'tmp'; tmpdir.mkdir()
    env = dict(os.environ, TMPDIR=str(tmpdir))
    run([PY, 'run.py', '--n', '1', '--models', 'm', '--claude-bin', fake], d, env=env)
    assert len(list((d / 'runs').glob('*.json'))) == 2
    assert list(tmpdir.iterdir()) == [], 'temp cwd left behind'


def test_focus_nag_rejects_empty_lines(tmp_path):
    m = load_nag()
    with pytest.raises(ValueError, match='non-empty list'):
        m.Nag(blocklist=['youtube.com'], lines=[])
    with pytest.raises(ValueError, match='empty or non-string'):
        m.Nag(blocklist=['youtube.com'], lines=['say:1', ''])
    d = copy('real-tool-reel', tmp_path)
    cfg = json.loads((d / 'tool/config.json').read_text()); cfg['lines'] = []
    (d / 'tool/config.json').write_text(json.dumps(cfg))
    r = run([PY, 'tool/focus_nag.py', '--feed', 'tool/demo.tsv'], d, ok=False)
    assert r.returncode == 2 and 'lines' in r.stderr and 'Traceback' not in r.stderr
