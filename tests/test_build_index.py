"""scripts/build_index.py --check on a temp copy of recipes/: fresh passes, a changed title makes it stale.

Also: --check fails when a hand-written section README misses a recipe, lists a wrong status or links a missing file.

Also covers the other generated files: recipes/index.json, recipes/BY-SYMPTOM.md and docs/CHANGELOG.md.

Only --check is run against the real repository; writing is tested on the temp copy.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'build_index.py'


def run(*args, cwd=None):
    return subprocess.run([sys.executable, '-I', str(SCRIPT), *map(str, args)], capture_output=True, text=True, cwd=cwd)


GENERATED = ['recipes/README.md', 'recipes/index.json', 'recipes/BY-SYMPTOM.md', 'docs/CHANGELOG.md']


def temp_repo(tmp_path):
    repo = tmp_path / 'repo'
    shutil.copytree(ROOT / 'recipes', repo / 'recipes', ignore=shutil.ignore_patterns('__pycache__'))
    (repo / 'docs').mkdir()
    shutil.copy(ROOT / 'docs/CHANGELOG.md', repo / 'docs/CHANGELOG.md')
    return repo


def first_recipe(repo):
    return next(x for x in sorted((repo / 'recipes').glob('*/*.md')) if x.name != 'README.md')


RECIPE = """---
id: {id}
title: {title}
section: {section}
lang: any
status: {status}
evidence: measurement
tools: [ffmpeg, "Python"]
learn: ../../learn/en/00-first-video.md
added: {added}
updated: {updated}
contributors: [test]
---

## When
{when}

Second paragraph that must not reach the index.

## Do
Something.

## Verify
Something.

## Evidence
1 of 5 before, 5 of 5 after.
"""


def mini_repo(tmp_path):
    """Three hand-written recipes in two sections, nothing generated yet."""
    repo = tmp_path / 'mini'
    rows = [
        ('voice', 'voice-b', 'Voice B', 'proven', '2026-10-01', '2026-10-05',
         'The first word is eaten\nand the line starts mid-word.'),
        ('voice', 'voice-a', 'Voice A', 'hypothesis', '2026-10-05', '2026-10-05', 'The voice is too quiet.'),
        ('idea', 'idea-x', 'Idea X', 'hypothesis', '2026-10-01', '2026-10-01', '- No hook\n- No ending'),
    ]
    for section, rid, title, status, added, updated, when in rows:
        d = repo / 'recipes' / section
        d.mkdir(parents=True, exist_ok=True)
        (d / f'{rid}.md').write_text(RECIPE.format(id=rid, title=title, section=section, status=status,
                                                   added=added, updated=updated, when=when), encoding='utf-8')
        readme = d / 'README.md'
        head = readme.read_text(encoding='utf-8') if readme.exists() else \
            f'# {section}\n\n| Recipe | Status | Lang | Gist |\n|---|---|---|---|\n'
        readme.write_text(head + f'| [{title}]({rid}.md) | {status} | any | gist |\n', encoding='utf-8')
    return repo


def test_check_fresh_copy_passes(tmp_path):
    repo = temp_repo(tmp_path)
    r = run('--check', repo)
    assert r.returncode == 0 and 'fresh' in r.stdout, r.stdout + r.stderr


def test_check_after_title_change_is_stale_and_rebuild_fixes(tmp_path):
    repo = temp_repo(tmp_path)
    p = first_recipe(repo)
    text = p.read_text(encoding='utf-8')
    p.write_text(text.replace('title: ', 'title: CHANGED ', 1), encoding='utf-8')
    r = run('--check', repo)
    assert r.returncode == 1 and 'stale' in r.stdout, r.stdout + r.stderr
    r = run(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    for rel in GENERATED:
        assert 'CHANGED' in (repo / rel).read_text(encoding='utf-8'), rel
    assert run('--check', repo).returncode == 0


def test_check_names_each_stale_file(tmp_path):
    repo = temp_repo(tmp_path)
    (repo / 'recipes' / 'BY-SYMPTOM.md').write_text('stale', encoding='utf-8')
    (repo / 'docs/CHANGELOG.md').unlink()
    r = run('--check', repo)
    assert r.returncode == 1, r.stdout
    assert 'recipes/BY-SYMPTOM.md is stale' in r.stdout and 'docs/CHANGELOG.md is stale' in r.stdout
    assert 'recipes/README.md is stale' not in r.stdout and 'recipes/index.json is stale' not in r.stdout


def test_when_change_makes_symptom_files_stale(tmp_path):
    repo = temp_repo(tmp_path)
    p = first_recipe(repo)
    p.write_text(p.read_text(encoding='utf-8').replace('## When\n', '## When\nWHENCHANGED ', 1), encoding='utf-8')
    r = run('--check', repo)
    assert r.returncode == 1
    assert 'recipes/index.json is stale' in r.stdout and 'recipes/BY-SYMPTOM.md is stale' in r.stdout
    assert 'recipes/README.md is stale' not in r.stdout and 'docs/CHANGELOG.md is stale' not in r.stdout


def test_index_json_fields_order_and_when(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    raw = (repo / 'recipes' / 'index.json').read_text(encoding='utf-8')
    assert raw.endswith(']\n')
    items = json.loads(raw)
    assert [x['id'] for x in items] == ['idea-x', 'voice-a', 'voice-b']   # SECTIONS order, then file name
    b = items[2]
    assert list(b) == ['id', 'title', 'section', 'lang', 'status', 'evidence', 'tools', 'path', 'added', 'updated', 'when']
    assert b['tools'] == ['ffmpeg', 'Python'] and b['path'] == 'recipes/voice/voice-b.md'
    assert b['when'] == 'The first word is eaten and the line starts mid-word.'
    assert items[0]['when'] == 'No hook; No ending'
    assert 'Second paragraph' not in raw


def test_outputs_are_deterministic_and_non_ascii_kept(tmp_path):
    repo = mini_repo(tmp_path)
    p = repo / 'recipes' / 'voice' / 'voice-a.md'
    p.write_text(p.read_text(encoding='utf-8').replace('too quiet.', 'too quiet — «тихо».'), encoding='utf-8')
    assert run(repo).returncode == 0
    first = {rel: (repo / rel).read_bytes() for rel in GENERATED}
    assert run(repo).returncode == 0
    assert first == {rel: (repo / rel).read_bytes() for rel in GENERATED}
    assert '«тихо»' in first['recipes/index.json'].decode('utf-8')
    assert run('--check', repo).returncode == 0


def test_by_symptom_groups_by_section_with_links(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    text = (repo / 'recipes' / 'BY-SYMPTOM.md').read_text(encoding='utf-8')
    assert 'do not edit by hand' in text
    assert text.index('## Idea and script') < text.index('## Voice and TTS')
    assert '- The voice is too quiet. → [Voice A](voice/voice-a.md) · hypothesis' in text
    assert '[Voice B](voice/voice-b.md) · proven' in text


def test_changelog_added_vs_updated_by_date(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    text = (repo / 'docs/CHANGELOG.md').read_text(encoding='utf-8')
    assert 'generated' in text.lower() and 'front matter' in text
    assert text.index('## 2026-10-05') < text.index('## 2026-10-01')
    oct5, oct1 = text.split('## 2026-10-01')
    # voice-a added on 10-05 (updated == added: not repeated as Updated); voice-b updated on 10-05
    assert oct5.count('voice-a.md') == 1 and '### Added\n\n- [Voice A](../recipes/voice/voice-a.md)' in oct5
    assert '### Updated\n\n- [Voice B](../recipes/voice/voice-b.md)' in oct5
    assert '### Added' in oct1 and 'idea-x.md' in oct1 and 'voice-b.md' in oct1 and '### Updated' not in oct1
    assert text.endswith('\n') and not text.endswith('\n\n')


def test_help_does_not_write(tmp_path):
    repo = temp_repo(tmp_path)
    index = repo / 'recipes' / 'README.md'
    index.write_text('stale on purpose', encoding='utf-8')
    r = run('--help', cwd=repo)
    assert r.returncode == 0 and 'usage:' in r.stdout
    assert index.read_text(encoding='utf-8') == 'stale on purpose'


def test_missing_recipes_folder_fails(tmp_path):
    r = run('--check', tmp_path)
    assert r.returncode == 1 and 'no recipes/' in r.stdout


def test_real_index_is_fresh():
    r = run('--check')
    assert r.returncode == 0, r.stdout + r.stderr


def test_section_readme_missing_row_fails(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    assert run('--check', repo).returncode == 0
    readme = repo / 'recipes' / 'voice' / 'README.md'
    readme.write_text('\n'.join(x for x in readme.read_text(encoding='utf-8').splitlines() if 'voice-a.md' not in x) + '\n',
                      encoding='utf-8')
    r = run('--check', repo)
    assert r.returncode == 1 and 'no row for voice-a.md' in r.stdout, r.stdout + r.stderr


def test_section_readme_wrong_status_and_dangling_row_fail(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    readme = repo / 'recipes' / 'voice' / 'README.md'
    text = readme.read_text(encoding='utf-8').replace('(voice-b.md) | proven', '(voice-b.md) | hypothesis')
    readme.write_text(text + '| [Gone](voice-gone.md) | proven | any | gist |\n', encoding='utf-8')
    r = run('--check', repo)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "voice-b.md listed as 'hypothesis', front matter says 'proven'" in r.stdout
    assert 'row links missing recipe voice-gone.md' in r.stdout


def test_section_readme_absent_fails(tmp_path):
    repo = mini_repo(tmp_path)
    assert run(repo).returncode == 0
    (repo / 'recipes' / 'idea' / 'README.md').unlink()
    r = run('--check', repo)
    assert r.returncode == 1 and 'recipes/idea/README.md is missing' in r.stdout, r.stdout + r.stderr
