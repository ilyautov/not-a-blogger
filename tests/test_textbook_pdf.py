"""Сборка учебника в PDF: Markdown собирается без потерь, ссылки переписаны, PDF проходит гейты."""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('build_textbook_pdf', ROOT / 'scripts' / 'build_textbook_pdf.py')
btp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(btp)


@pytest.mark.parametrize('lang', ['ru', 'en'])
def test_book_md_has_every_chapter_and_no_relative_links(lang):
    md, titles = btp.book_md(lang)
    assert len(titles) == len(btp.ORDER)
    for stem in btp.ORDER:
        assert f'{{#{btp.anchor(stem)}}}' in md, stem
    # относительных ссылок на .md не остаётся: внутри учебника якоря, снаружи GitHub
    rel = [t for t in re.findall(r'\]\(([^)\s]+)\)', md) if not re.match(r'^(#|https?:|file:)', t)]
    assert rel == []
    assert '```mermaid' not in md


def test_learn_files_match_order():
    """Новая глава в learn/ должна попасть в ORDER, иначе её не будет в PDF."""
    for lang in ('ru', 'en'):
        stems = {p.stem for p in (ROOT / 'learn' / lang).glob('*.md')} - {'README'}
        assert stems == set(btp.ORDER), stems ^ set(btp.ORDER)


def test_mermaid_becomes_flow_steps():
    steps = btp.mermaid_steps('```mermaid\nflowchart TD\n  A[Бриф<br/>BRIEF.md] --> B[Реплики]\n  B --> C[Сцена]\n```')
    assert steps == [('Бриф', 'BRIEF.md'), ('Реплики', ''), ('Сцена', '')]
    svg = btp.mermaid_block('```mermaid\nflowchart TD\n  A[Бриф<br/>BRIEF.md] --> B[Реплики]\n```', 'Схема')
    assert '<svg' in svg and '>Бриф<' in svg and '>BRIEF.md<' in svg and 'Схема' in svg


@pytest.mark.skipif(importlib.util.find_spec('weasyprint') is None, reason='нет weasyprint')
def test_build_ru_pdf_passes_gates(tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_textbook_pdf.py'), '--lang', 'ru', '--out', str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / 'not-a-blogger-textbook-ru.pdf').stat().st_size > 100_000


def test_tilde_and_long_fences_keep_code_untouched(tmp_path):
    src = tmp_path / 'x.md'
    src.write_text('# Глава\n\n~~~~python\n# comment\n[a](03-voice.md)\n~~~~\n\n````\n# two\n```\n# still code\n````\n\n~~~~\n# longer close\n~~~~~\n', encoding='utf-8')
    out = btp.chapter_md(src, 'ru')
    assert '\n# comment\n[a](03-voice.md)\n' in out
    assert '\n# two\n```\n# still code\n' in out
    assert '\n# longer close\n' in out
    assert out.startswith('## Глава {#ch-x}')


def test_mermaid_with_unsupported_shapes_fails_loudly():
    with pytest.raises(SystemExit):
        btp.mermaid_steps('```mermaid\nflowchart TD\n  A{Ready?} -->|yes| B[Build]\n  A --> C([Stop])\n```')
    with pytest.raises(SystemExit):
        btp.mermaid_steps('```mermaid\nflowchart TD\n  A[Start] --> B>Skip]\n```')


def test_mermaid_label_may_contain_brackets():
    steps = btp.mermaid_steps('```mermaid\nflowchart LR\n  A["Scene (HTML)"] --> B[Export]\n```')
    assert steps == [('Scene (HTML)', ''), ('Export', '')]


def test_chapter_link_with_fragment_keeps_fragment():
    src = ROOT / 'learn' / 'ru' / 'ROADMAP.md'
    m = btp.LINK.search('[ударения](03-voice.md#stress)')
    assert btp.rewrite_link(m, src, 'ru') == '[ударения](https://github.com/ilyautov/not-a-blogger/blob/main/learn/ru/03-voice.md#stress)'
    m = btp.LINK.search('[ниже](#stress)')
    assert btp.rewrite_link(m, src, 'ru') == '[ниже](https://github.com/ilyautov/not-a-blogger/blob/main/learn/ru/ROADMAP.md#stress)'
    m = btp.LINK.search('[голос](03-voice.md)')
    assert btp.rewrite_link(m, src, 'ru') == '[голос](#ch-03-voice)'


def test_code_lines_fit_pdf_width():
    """Длинная строка в коде переносится в PDF посреди команды, и скопированная команда ломается."""
    long = []
    for p in sorted((ROOT / 'learn').glob('*/*.md')):
        for f in btp.FENCE.finditer(p.read_text(encoding='utf-8')):
            if btp.MERMAID.match(f.group(0)):
                continue
            long += [f'{p.relative_to(ROOT)}: {line}' for line in f.group(0).splitlines() if len(line) > btp.CODE_WIDTH]
    assert long == []


@pytest.mark.skipif(importlib.util.find_spec('weasyprint') is None, reason='нет weasyprint')
def test_check_pdf_rejects_title_only_in_toc(monkeypatch, tmp_path):
    import longread
    monkeypatch.setattr(longread, 'pdf_gates', lambda pdf: [])
    monkeypatch.setattr(btp.subprocess, 'run', lambda *a, **k: type('R', (), {'stdout': 'Содержание Глава один Глава два Глава два'})())
    assert btp.check_pdf(tmp_path / 'x.pdf', ['Глава один', 'Глава два']) == ['в PDF нет главы «Глава один» (название только в оглавлении или нигде)']
    # оглавление и заголовки есть, а текста глав нет
    bad = btp.check_pdf(tmp_path / 'x.pdf', ['Глава два'], src_len=5000)
    assert len(bad) == 1 and 'часть текста потеряна' in bad[0]


def test_split_title():
    assert btp.split_title('03. Голос и TTS') == ('03', 'Голос и TTS')
    assert btp.split_title('00а. Как это устроено') == ('00а', 'Как это устроено')
    assert btp.split_title('Словарь') == ('', 'Словарь')


def test_every_chapter_with_number_has_art():
    """Журнальная вёрстка: у обложки и каждой нумерованной главы своя иллюстрация с Горо."""
    missing = [f for k, f in btp.ART_FILES.items() if not (btp.ART / f).exists()]
    assert missing == []
    numbered = [s for s in btp.ORDER if btp.split_title(btp.chapter_title(ROOT / 'learn' / 'ru' / f'{s}.md'))[0]]
    assert set(numbered) <= set(btp.ART_FILES)


def test_cover_numbers_are_counted_from_repo():
    import json
    recipes = json.loads((ROOT / 'recipes' / 'index.json').read_text(encoding='utf-8'))
    total, proven, chapters, examples = btp.repo_stats()
    assert total == len(recipes) and proven == sum(r['status'] == 'proven' for r in recipes)
    assert chapters == 12 and examples > 0


@pytest.mark.skipif(importlib.util.find_spec('markdown') is None, reason='нет markdown')
def test_tables_and_code_span_both_columns():
    """column-span WeasyPrint не применяет к table и pre: без обёртки таблица сжимается в узкую колонку."""
    palette = {'ink': '#000', 'sub': '#555', 'accent': '#060', 'panel': '#eee', 'line': '#ccc', 'font': 'sans'}
    out = btp.chapter_html(ROOT / 'learn' / 'ru' / '00a-how-it-works.md', 'ru', palette)
    assert out.count('<table') == out.count('<div class="wide"><table') > 0
    assert out.count('<pre') == out.count('<div class="wide"><pre') > 0


def test_mermaid_caption_and_short_flow_as_cards():
    block = '```mermaid\n%% Порядок проверок\nflowchart LR\n  A[Звук<br/>LUFS] --> B[Кадры] --> C[Человек]\n```'
    assert btp.mermaid_caption(block) == 'Порядок проверок'
    out = btp.mermaid_block(block, 'Схема')
    assert 'Порядок проверок' in out and '<rect' in out and '>LUFS<' in out
    assert btp.mermaid_caption('```mermaid\nflowchart LR\n  A --> B\n```') == ''


def test_svg_labels_wrap_by_words():
    assert btp.wrap('Синтез каждого дубля отдельно', 12) == ['Синтез', 'каждого', 'дубля', 'отдельно']
    assert btp.wrap('a b c', 10) == ['a b c']


def test_recipe_labels_and_done_bar():
    html = '<p><strong>Проблема.</strong> x</p><p><strong>Где ломается.</strong> y</p><p><strong>Готово, когда</strong> z</p>'
    out = btp.label_paragraphs(html, 'ru')
    assert 'class="lab lab-prob"' in out and 'class="lab lab-break"' in out and 'class="done"' in out
    assert 'class="lab lab-do"' in btp.label_paragraphs('<p><strong>What we do.</strong> x</p>', 'en')


def test_recipe_strip_counts_match_recipes():
    rs = btp.recipes_for('03-voice')
    assert rs and all(r['path'].endswith('.md') for r in rs)
    strip = btp.recipe_strip('03-voice', 'ru')
    assert f'<b>{len(rs)}</b>' in strip
    # каждый рецепт привязан к главе: сумма по главам равна числу рецептов
    import json
    total = len(json.loads((ROOT / 'recipes' / 'index.json').read_text(encoding='utf-8')))
    assert sum(len(btp.recipes_for(s)) for s in btp.ORDER) == total


def test_roadmap_stages_parsed_from_table():
    for lang in ('ru', 'en'):
        st = btp.roadmap_stages(lang)
        assert [n for n, *_ in st] == ['1', '2', '3', '4'] and all(t and d and g for _, t, d, g in st)
