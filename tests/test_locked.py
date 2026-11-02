"""The machine-wide lock follows the command, including signal cleanup."""
import os
import signal
import subprocess
import sys
import time

import pytest

from conftest import ROOT

LOCKED = ROOT / 'starter' / 'locked.py'


def wait_for(predicate, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.02)
    pytest.fail('worker did not reach the expected state')


def test_lock_covers_signal_cleanup_and_command_exit_status(tmp_path):
    worker = tmp_path / 'worker.py'
    worker.write_text('''import os, signal, sys, time
from pathlib import Path
root = Path(sys.argv[1])
def stop(*_):
    (root / 'signaled').touch()
    while not (root / 'release').exists():
        time.sleep(.02)
    sys.exit(23)
signal.signal(signal.SIGTERM, stop)
(root / 'ready').write_text(str(os.getpid()))
while True:
    time.sleep(.02)
''')
    env = {**os.environ, 'LOCK_DIR': str(tmp_path)}
    command = [sys.executable, str(LOCKED), 'signal-test', '--', sys.executable]
    first = subprocess.Popen(command + [str(worker), str(tmp_path)], env=env, start_new_session=True)
    second = None
    try:
        wait_for(lambda: (tmp_path / 'ready').exists())
        second = subprocess.Popen(command + ['-c', 'from pathlib import Path; import sys; Path(sys.argv[1]).touch()',
                                            str(tmp_path / 'contender')], env=env, start_new_session=True)
        time.sleep(.2)
        assert not (tmp_path / 'contender').exists(), 'lock did not serialize live workers'
        first.send_signal(signal.SIGTERM)
        # Before exec, SIGTERM kills only the wrapper and frees the lock.
        wait_for(lambda: first.poll() is not None or (tmp_path / 'signaled').exists())
        time.sleep(.2)
        assert not (tmp_path / 'contender').exists(), 'lock released while the actual worker was alive'
        assert (tmp_path / 'signaled').exists(), 'command did not receive SIGTERM'
        (tmp_path / 'release').touch()
        assert first.wait(timeout=5) == 23
        assert second.wait(timeout=5) == 0
        assert (tmp_path / 'contender').exists()
    finally:
        (tmp_path / 'release').touch()
        # Also reap the worker PID if this runs against the old spawning wrapper.
        worker_pid = int((tmp_path / 'ready').read_text()) if (tmp_path / 'ready').exists() else None
        if worker_pid is not None and worker_pid != first.pid:
            try:
                os.kill(worker_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for process in (first, second):
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)


@pytest.mark.parametrize('kind', ['symlink', 'hardlink', 'directory'])
def test_lock_rejects_unsafe_files(tmp_path, kind):
    target = tmp_path / 'target'
    target.write_text('untouched')
    lock = tmp_path / 'not-a-blogger-unsafe.lock'
    if kind == 'symlink':
        lock.symlink_to(target)
    elif kind == 'hardlink':
        os.link(target, lock)
    else:
        lock.mkdir()
    result = subprocess.run([sys.executable, str(LOCKED), 'unsafe', '--', sys.executable, '-c',
                             'raise AssertionError("command must not run")'],
                            env={**os.environ, 'LOCK_DIR': str(tmp_path)}, capture_output=True, text=True, timeout=5)
    assert result.returncode != 0
    assert 'AssertionError' not in result.stderr
    assert target.read_text() == 'untouched'
