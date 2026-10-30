# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""tools/slides: дек из Markdown на шаблоне deck.html."""
from conftest import TOOLS, load

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
