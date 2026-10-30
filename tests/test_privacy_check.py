"""scripts/privacy_check.sh on a temp copy of a repo with planted files.

The nick and the other personal values are read from the script itself: the tests add no personal data of their own.
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'privacy_check.sh'
BASH = shutil.which('bash')


def script_value(var):
    """`VAR="ab""cd"` in the script -> "abcd"."""
    m = re.search(rf'(?m)\b{var}="((?:[^"\n]*"")*[^"\n]*)"', SCRIPT.read_text(encoding='utf-8'))
    assert m, var
    return m.group(1).replace('""', '')


NICK = script_value('I')
# Home-path prefixes are assembled from pieces so that this file does not trip the check itself.
MAC_HOME = '/' + 'Users' + '/'
LINUX_HOME = '/' + 'home' + '/'


def check(tmp_path, files):
    """Plant files into a fresh tree with a copy of the script, run it on that tree, return (returncode, output)."""
    repo = tmp_path / 'repo'
    (repo / 'scripts').mkdir(parents=True)
    shutil.copy(SCRIPT, repo / 'scripts' / 'privacy_check.sh')
    for name, body in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            p.write_bytes(body)
        else:
            p.write_text(body, encoding='utf-8')
    r = subprocess.run([BASH, str(repo / 'scripts' / 'privacy_check.sh'), str(repo)],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


pytestmark = pytest.mark.skipif(BASH is None, reason='no bash')


def test_clean_tree_passes(tmp_path):
    rc, out = check(tmp_path, {'README.md': 'nothing personal here\n'})
    assert rc == 0, out


def test_macos_home_path_fails(tmp_path):
    rc, out = check(tmp_path, {'doc.md': f'see {MAC_HOME}x/proj/file.py for details\n'})
    assert rc == 1 and 'doc.md' in out, out


def test_linux_home_path_with_nick_fails(tmp_path):
    rc, out = check(tmp_path, {'doc.md': f'ran it from {LINUX_HOME}{NICK}/proj/x.py\n'})
    assert rc == 1 and 'doc.md' in out, out


def test_linux_home_path_other_user_fails(tmp_path):
    rc, out = check(tmp_path, {'doc.md': f'ran it from {LINUX_HOME}someone/proj/x.py\n'})
    assert rc == 1 and 'doc.md' in out, out


def test_github_slug_is_allowed(tmp_path):
    rc, out = check(tmp_path, {'doc.md': f'Tool: [repo](https://github.com/{NICK}/repo) (MIT)\n'})
    assert rc == 0, out


def test_bare_nick_fails(tmp_path):
    rc, out = check(tmp_path, {'doc.md': f'ask {NICK} about it\n'})
    assert rc == 1 and 'doc.md' in out, out


def test_binary_file_with_hit_fails(tmp_path):
    body = b'\x89PNG\r\n\x1a\n\x00\x00' + (MAC_HOME + 'x/Pictures/a.png').encode() + b'\x00\xff\xfe' * 20
    rc, out = check(tmp_path, {'img.png': body})
    assert rc == 1 and 'img.png' in out and 'бинарный' in out, out


def test_placeholder_paths_in_rules_are_allowed(tmp_path):
    rc, out = check(tmp_path, {'RULES.md': 'No paths like `/Users/имя` or `/home/ник` in recipes.\n'})
    assert rc == 0, out


GIT = shutil.which('git')


@pytest.mark.skipif(GIT is None, reason='no git')
def test_git_repo_skips_ignored_but_checks_untracked(tmp_path):
    """In a git work tree only committable files count: a gitignored cache passes, a new untracked file fails."""
    files = {'.gitignore': 'cache/\n', 'README.md': 'nothing personal here\n',
             'cache/state.json': f'{{"p": "{MAC_HOME}x/.cache/blob"}}\n'}
    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run([GIT, 'init', '-q', str(repo)], check=True)
    rc, out = check(tmp_path, files)
    assert rc == 0, out
    (repo / 'new.md').write_text(f'see {MAC_HOME}x/proj\n', encoding='utf-8')
    r = subprocess.run([BASH, str(repo / 'scripts' / 'privacy_check.sh'), str(repo)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1 and 'new.md' in r.stdout, r.stdout + r.stderr
