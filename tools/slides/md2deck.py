#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Markdown → HTML-дек одним файлом на шаблоне deck.html.

Слайды разделяются строкой «---» (внутри блоков кода ``` или ~~~ любой длины разделитель не срабатывает;
блок закрывает только такая же ограда не короче открывающей, как в CommonMark).
В начале файла можно поставить front matter:
  ---
  title: Как сварить кофе в турке
  theme: themes/night.css
  ---
Класс слайда задаётся комментарием внутри слайда: <!-- class: center -->.
Строка «::: kicker Текст» даёт надзаголовок над заголовком слайда.
Внутри блоков кода директивы не работают: пример разметки в коде остаётся текстом.

Если установлен пакет markdown, разметка полная (таблицы, код, вложенные списки).
Без него работает встроенный упрощённый разбор: заголовки, абзацы, списки, цитаты,
код, **жирный**, *акцент*, `код`, ссылки.

Запуск:
  python3 md2deck.py examples/coffee-turka.md -o out/coffee-deck.html
  python3 md2deck.py talk.md -o talk.html --theme themes/night.css

Готовый файл открывается в браузере без сервера; PDF печатается из браузера (README).
"""
import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / 'deck.html'
START, END = '<!-- slides:start -->', '<!-- slides:end -->'
CLASS_RE = re.compile(r'<!--\s*class:\s*([\w\s-]+?)\s*-->')
KICKER_RE = re.compile(r'^:::\s*kicker\s+(.+)$')
FENCE_RE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')


def fence_step(line, fence):
    """Шаг разбора оград кода. fence: None (вне кода) или (символ, длина) открывшей ограды.
    Возвращает (новое состояние, строка — ограда?). Закрывает ограда того же символа, не короче, без хвоста."""
    m = FENCE_RE.match(line)
    if fence is None:
        if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):
            return (m.group(1)[0], len(m.group(1))), True
        return None, False
    if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2).strip():
        return None, True
    return fence, False


def split_front(text):
    meta = {}
    m = re.match(r'^---[ \t]*\n((?:[\w-]+[ \t]*:.*\n)+)---[ \t]*\n', text)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(':')
            meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def split_slides(text):
    slides, cur, fence = [], [], None
    for line in text.splitlines():
        was_in = fence is not None
        fence, is_fence = fence_step(line, fence)
        if not was_in and not is_fence and line.strip() == '---':
            slides.append('\n'.join(cur))
            cur = []
        else:
            cur.append(line)
    slides.append('\n'.join(cur))
    return [s for s in slides if s.strip()]


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def mini_markdown(md):
    """Упрощённый Markdown без зависимостей."""
    out, para, lst, code = [], [], None, None

    def flush():
        nonlocal para, lst
        if para:
            out.append('<p>' + _inline(' '.join(para)) + '</p>')
            para = []
        if lst:
            tag, items = lst
            out.append(f'<{tag}>' + ''.join(f'<li>{_inline(x)}</li>' for x in items) + f'</{tag}>')
            lst = None

    fence = None
    for line in md.splitlines():
        fence, is_fence = fence_step(line, fence)
        if code is not None:
            if is_fence:
                out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code = None
            else:
                code.append(line)
            continue
        if is_fence:
            flush()
            code = []
            continue
        s = line.strip()
        if not s:
            flush()
            continue
        m = re.match(r'(#{1,6})\s+(.*)', s)
        if m:
            flush()
            n = len(m.group(1))
            out.append(f'<h{n}>{_inline(m.group(2))}</h{n}>')
            continue
        m = re.match(r'([-*+]|\d+[.)])\s+(.*)', s)
        if m:
            if para:
                flush()
            tag = 'ol' if m.group(1)[0].isdigit() else 'ul'
            if not lst or lst[0] != tag:
                flush()
                lst = (tag, [])
            lst[1].append(m.group(2))
            continue
        if s.startswith('>'):
            flush()
            out.append('<blockquote><p>' + _inline(s.lstrip('> ')) + '</p></blockquote>')
            continue
        if s.startswith('<'):  # сырой HTML пропускаем как есть
            flush()
            out.append(s)
            continue
        para.append(s)
    if code is not None:
        out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
    flush()
    return '\n'.join(out)


def to_html(md):
    try:
        import markdown
    except ImportError:
        return mini_markdown(md)
    return markdown.markdown(md, extensions=['extra', 'sane_lists'])


def slide_html(md):
    """Директивы class и kicker берутся только из строк вне блоков кода."""
    classes, kicker, keep, fence = [], '', [], None
    for line in md.splitlines():
        was_in = fence is not None
        fence, is_fence = fence_step(line, fence)
        if was_in or is_fence:
            keep.append(line)
            continue
        classes += CLASS_RE.findall(line)
        line = CLASS_RE.sub('', line)
        m = KICKER_RE.match(line)
        if m:
            kicker = kicker or f'<div class="kicker">{html.escape(m.group(1).strip())}</div>\n'
            continue
        keep.append(line)
    md = '\n'.join(keep)
    cls = f'slide {" ".join(classes)}'.strip()
    return f'  <section class="{cls}">\n{kicker}{to_html(md.strip())}\n  </section>'


def build(md_text, template=None, theme_css=None):
    meta, body = split_front(md_text)
    tpl = (template or TEMPLATE.read_text(encoding='utf-8'))
    a, b = tpl.index(START) + len(START), tpl.index(END)
    sections = '\n'.join(slide_html(s) for s in split_slides(body))
    out = tpl[:a] + '\n' + sections + '\n' + tpl[b:]
    if meta.get('title'):
        title = f'<title>{html.escape(meta["title"])}</title>'
        out = re.sub(r'<title>.*?</title>', lambda m: title, out, count=1, flags=re.S)   # lambda: «\U» в C:\Users не escape
    if theme_css:
        out = re.sub(r'(<style id="theme">).*?(</style>)', lambda m: m.group(1) + '\n' + theme_css + '\n' + m.group(2),
                     out, count=1, flags=re.S)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Markdown → HTML-дек')
    ap.add_argument('input')
    ap.add_argument('-o', '--out', default=None, help='куда писать .html (по умолчанию рядом с .md)')
    ap.add_argument('--theme', default=None, help='CSS с :root-токенами (см. themes/)')
    ap.add_argument('--template', default=None, help='свой шаблон с маркерами slides:start / slides:end')
    a = ap.parse_args(argv)
    src = Path(a.input)
    md_text = src.read_text(encoding='utf-8')
    meta, _ = split_front(md_text)
    theme = a.theme or meta.get('theme')
    theme_css = None
    if theme:
        tp = Path(theme)
        if not tp.is_absolute() and not tp.exists():
            tp = HERE / theme
        theme_css = tp.read_text(encoding='utf-8')
    tpl = Path(a.template).read_text(encoding='utf-8') if a.template else None
    out_html = build(md_text, tpl, theme_css)
    out = Path(a.out) if a.out else src.with_suffix('.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(out_html, encoding='utf-8')
    print(f'{out}: слайдов {out_html.count(chr(60) + "section class=")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
