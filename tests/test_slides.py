# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""tools/slides: дек из Markdown на шаблоне deck.html."""
from conftest import TOOLS, load
import pytest

md2deck = load('slides', 'md2deck')

THREE = """---
title: Три слайда
---
# Первый
Текст.

---

## Второй
- пункт

---

<!-- class: center -->
## Третий
```bash
echo "---"
```
"""


def test_three_slides_three_sections():
    out = md2deck.build(THREE)
    assert out.count('<section class="slide') == 3
    assert '<title>Три слайда</title>' in out
    assert 'class="slide center"' in out


def test_fallback_parser_three_sections():
    body = md2deck.split_front(THREE)[1]
    slides = md2deck.split_slides(body)
    assert len(slides) == 3  # «---» внутри блока кода не режет слайд
    html = md2deck.mini_markdown(slides[1])
    assert '<h2>Второй</h2>' in html and '<li>пункт</li>' in html


def test_template_has_navigation_and_print():
    tpl = (TOOLS / 'slides' / 'deck.html').read_text(encoding='utf-8')
    assert 'ArrowRight' in tpl and 'ArrowLeft' in tpl
    assert "id=\"pg\"" in tpl and '@media print' in tpl
    assert tpl.count('<section class="slide') == 3


def test_theme_replaced(tmp_path):
    css = (TOOLS / 'slides' / 'themes' / 'night.css').read_text(encoding='utf-8')
    out = md2deck.build(THREE, theme_css=css)
    assert '#15171b' in out


def test_cli_example(tmp_path):
    out = tmp_path / 'deck.html'
    assert md2deck.main([str(TOOLS / 'slides' / 'examples' / 'coffee-turka.md'), '-o', str(out)]) == 0
    assert out.read_text(encoding='utf-8').count('<section class="slide') == 5


def test_title_with_backslashes_kept_literally():
    out = md2deck.build('---\ntitle: C:\\Users\\Alice \\1 \\g<0>\n---\n# Слайд\n')
    assert '<title>C:\\Users\\Alice \\1 \\g&lt;0&gt;</title>' in out


def test_directives_and_separators_inside_fences_are_text():
    md = """# Пример разметки
````markdown
<!-- class: center -->
::: kicker Не надзаголовок
```bash
echo hi
```
---
````

---

~~~~
---
~~~
---
~~~~
## Второй
"""
    secs = md2deck.split_slides(md)
    assert len(secs) == 2, secs
    first = md2deck.slide_html(secs[0])
    assert 'class="slide"' in first and 'class="kicker"' not in first
    assert '::: kicker Не надзаголовок' in first and 'class: center' in first
    second = md2deck.slide_html(secs[1])
    assert '<h2>' in second
    real = md2deck.slide_html('<!-- class: center -->\n::: kicker Да\n# Заголовок')
    assert 'class="slide center"' in real and '<div class="kicker">Да</div>' in real


def test_mini_markdown_long_and_tilde_fences():
    html_ = md2deck.mini_markdown('````\n```\ninner\n```\n````\n\n~~~\nt\n~~~\nпосле')
    assert html_.count('<pre><code>') == 2
    assert '```\ninner\n```' in html_ and '<p>после</p>' in html_


@pytest.mark.parametrize('slide,block,descendant', [(2, 'table', '#cell'), (3, 'pre', 'code')])
def test_focused_overflow_arrows_scroll_content_without_changing_slide(tmp_path, slide, block, descendant):
    pw = pytest.importorskip('playwright.sync_api')
    template = (TOOLS / 'slides' / 'deck.html').read_text(encoding='utf-8')
    start, end = '<!-- slides:start -->', '<!-- slides:end -->'
    content = '''<section class="slide"><h1>Start</h1></section>
    <section class="slide"><h2>Wide table</h2><table tabindex="0">
    <tr><th>First column</th><th>Second column</th><th>Third column</th><th>Fourth column</th></tr>
    <tr><td><span id="cell" tabindex="0">First value</span></td><td>Second value</td>
    <td>Third value</td><td>Fourth value</td></tr></table></section>
    <section class="slide"><h2>Wide command</h2><pre tabindex="0"><code tabindex="0">''' + (
        'python3 tools/lint/still_lint.py starter --step 0.5 --max-still 3 --threshold 0.35'
    ) + '</code></pre></section>'
    path = tmp_path / 'deck.html'
    path.write_text(template.split(start)[0] + start + content + end + template.split(end)[1], encoding='utf-8')
    with pw.sync_playwright() as engine:
        try:
            browser = engine.chromium.launch(headless=True)
        except pw.Error as e:
            if "Executable doesn't exist" in str(e):
                pytest.skip('Chromium missing; run playwright install chromium')
            raise
        try:
            page = browser.new_page(viewport={'width': 390, 'height': 844})
            page.set_default_timeout(3000)
            page.goto(path.as_uri() + f'#{slide}')
            area = page.locator(block)
            assert area.evaluate('el => el.scrollWidth > el.clientWidth')
            # Both the scroll region itself and a focused descendant own their arrows.
            for target in (area, page.locator(descendant)):
                target.focus()
                area.evaluate('el => el.scrollLeft = 0')
                page.keyboard.press('ArrowRight')
                assert page.evaluate('location.hash') == f'#{slide}'
                page.wait_for_function('selector => document.querySelector(selector).scrollLeft > 0', arg=block)
                page.keyboard.press('ArrowLeft')
                page.wait_for_function('selector => document.querySelector(selector).scrollLeft === 0', arg=block)
                assert page.evaluate('location.hash') == f'#{slide}'
                # Reaching either edge must not unexpectedly navigate the deck.
                page.keyboard.press('ArrowLeft')
                assert page.evaluate('location.hash') == f'#{slide}'
                area.evaluate('el => el.scrollLeft = el.scrollWidth')
                page.keyboard.press('ArrowRight')
                assert page.evaluate('location.hash') == f'#{slide}'
            page.locator('.nav button').first.click()
            assert page.evaluate('location.hash') == f'#{slide - 1}'
            page.keyboard.press('ArrowRight')  # focus is now on a navigation button, outside overflow content
            assert page.evaluate('location.hash') == f'#{slide}'
            page.keyboard.press('ArrowLeft')
            assert page.evaluate('location.hash') == f'#{slide - 1}'
        finally:
            browser.close()
