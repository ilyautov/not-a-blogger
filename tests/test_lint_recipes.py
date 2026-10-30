"""scripts/lint_recipes.py on synthetic recipe trees: the valid one passes, each broken rule is reported."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'lint_recipes.py'


def load():
    spec = importlib.util.spec_from_file_location('lint_recipes', SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lr = load()

GOOD = """---
id: {id}
title: Do the thing
section: {section}
lang: {lang}
status: {status}
evidence: {evidence}
added: 2026-10-23
---

## When
Symptom.

## Do
1. Step.

## Verify
Check.

## Evidence
3 of 10 takes.
{tail}
## Related
- [neighbour]({link})
"""


def recipe(root, section='voice', id='voice-thing', lang='any', status='proven', link='neighbour.md', tail='', name=None,
           evidence='measurement'):
    d = root / 'recipes' / section
    d.mkdir(parents=True, exist_ok=True)
    (d / 'neighbour.md').write_text(GOOD.format(id='neighbour', section=section, lang='any', status='proven',
                                                evidence='measurement', link=f'{id}.md', tail=''), encoding='utf-8')
    p = d / f'{name or id}.md'
    p.write_text(GOOD.format(id=id, section=section, lang=lang, status=status, evidence=evidence, link=link, tail=tail),
                 encoding='utf-8')
    return p


def errors_of(root):
    _, errors = lr.lint(root)
    return errors


def test_valid_recipe_passes(tmp_path):
    recipe(tmp_path)
    assert errors_of(tmp_path) == []
    assert lr.main([str(tmp_path)]) == 0


def test_missing_required_key(tmp_path):
    p = recipe(tmp_path)
    p.write_text(p.read_text().replace('evidence: measurement\n', ''))
    assert any('missing field evidence' in e for e in errors_of(tmp_path))


def test_bad_status_enum(tmp_path):
    recipe(tmp_path, status='maybe')
    assert any("status 'maybe' not in" in e for e in errors_of(tmp_path))


def test_proven_requires_measured_evidence(tmp_path):
    recipe(tmp_path, status='proven', evidence='experience')
    errs = errors_of(tmp_path)
    assert any('status proven requires evidence' in e and "'experience'" in e for e in errs), errs


def test_proven_with_measured_evidence_passes(tmp_path):
    for ev in ('measurement', 'ab-test', 'video-metric'):
        recipe(tmp_path, status='proven', evidence=ev)
        assert errors_of(tmp_path) == [], ev


def test_hypothesis_allows_any_evidence(tmp_path):
    recipe(tmp_path, status='hypothesis', evidence='viewer-feedback')
    assert errors_of(tmp_path) == []


def test_broken_link(tmp_path):
    recipe(tmp_path, link='../nowhere/missing.md')
    assert any('broken link ../nowhere/missing.md' in e for e in errors_of(tmp_path))


def test_id_differs_from_file_name(tmp_path):
    recipe(tmp_path, id='voice-thing', name='voice-other')
    assert any("id 'voice-thing' != file name" in e for e in errors_of(tmp_path))


def test_lang_ru_without_contribute_invite(tmp_path):
    recipe(tmp_path, lang='ru')
    errs = errors_of(tmp_path)
    assert any("lang=ru" in e and 'contribute' in e for e in errs), errs


def test_lang_ru_with_contribute_invite_passes(tmp_path):
    recipe(tmp_path, lang='ru', tail='\nHave the same issue in another language? Contribute a sibling recipe next to this one (lang: <code>).\n')
    assert errors_of(tmp_path) == []


def test_zero_recipes_fails(tmp_path):
    (tmp_path / 'recipes').mkdir()
    assert lr.main([str(tmp_path)]) == 1


def test_missing_recipes_folder_fails(tmp_path):
    assert lr.main([str(tmp_path)]) == 1


def test_help_does_not_lint(tmp_path):
    r = subprocess.run([sys.executable, '-I', str(SCRIPT), '--help'], capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0 and 'usage:' in r.stdout and 'recipes:' not in r.stdout


def test_real_repo_is_clean():
    recipes, errors = lr.lint(ROOT)
    assert recipes and errors == [], errors
