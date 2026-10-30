"""Общие помощники тестов: загрузка утилиты по пути, синтетические wav и видео."""
import importlib.util
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
FFMPEG = shutil.which('ffmpeg')

needs_ffmpeg = pytest.mark.skipif(FFMPEG is None, reason='нет ffmpeg')


def load(group, name):
    """Импортировать tools/<group>/<name>.py как модуль."""
    path = TOOLS / group / f'{name}.py'
    spec = importlib.util.spec_from_file_location(f'{group}_{name}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tone(seconds, sr=24000, freq=220.0, amp=0.3):
    t = np.arange(int(seconds * sr)) / sr
    return amp * np.sin(2 * np.pi * freq * t)


def silence(seconds, sr=24000):
    return np.zeros(int(seconds * sr))


def ffmpeg(*args):
    subprocess.run([FFMPEG, '-v', 'error', '-y', *map(str, args)], check=True)


def encode_frames(frames, path, fps=30):
    """numpy (n, h, w) uint8 серые кадры → mp4 почти без потерь."""
    n, h, w = frames.shape
    p = subprocess.Popen([FFMPEG, '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{w}x{h}',
                          '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '4', '-pix_fmt', 'yuv420p', str(path)],
                         stdin=subprocess.PIPE)
    p.communicate(frames.astype(np.uint8).tobytes())
    assert p.returncode == 0
