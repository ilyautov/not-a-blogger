#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Статья в Markdown → PDF-методичка A4 с выносками. Дальше slice.py режет её в карусель.

Один источник, два формата: PDF (документ для LinkedIn, сайта, скачивания) и карусель 4:5.

Входной Markdown:
  ---
  title: Кофе в турке
  kicker: Методичка
  subtitle: Одна страница на тему
  footer: Кофейные заметки
  cover: art.png        # необязательно: AI-фон без текста, путь от файла .md
  ---
  Вступление...
  ## Каждый H2 начинает новую страницу
  :::callout Заголовок выноски
  Текст в **Markdown**.
  :::
  :::caveat Осторожно      (красная рамка)
  :::good Так / :::bad Не так  (зелёная / красная граница слева)
  :::numbers               (строки «число | подпись», SVG-карточки)
  :::bars Заголовок        (строки «подпись | число», SVG-столбики)
  :::flow                  (строка на шаг, SVG-схема со стрелками)
  > цитата                 (выделенный абзац)

Обложка: если задан cover, картинка идёт фоном на всю страницу, а заголовок кладётся
поверх CSS-слоем со скримом. Модель, которая рисовала фон, буквы не рисует никогда.

Проверки: до рендера текстовые гейты из cards.py (длинное тире, «не просто X, а Y»,
квадраты), после рендера pdfinfo (каждая страница A4 595×842 pt) и pdftotext (0 «—»).

Запуск:
  python3 longread.py examples/coffee-turka.md --theme paper --out out/longread
  python3 slice.py out/longread/coffee-turka.pdf --out out/longread-slides

Коды возврата: 0 успех; 1 гейты текста; 2 размер страницы или тире в PDF; 3 нет зависимостей.
"""
import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cards as cardlib  # noqa: E402  гейты и темы общие с движком карточек
import infographics as ig  # noqa: E402

A4_PT = (595.28, 841.89)

CSS = """
@page { size:A4; margin:18mm 18mm 16mm; background:var(--bg);
  @bottom-left { content:"%FOOTER%"; font-family:var(--font-sans); font-size:8pt; color:var(--sub); }
  @bottom-right { content:counter(page); font-family:var(--font-sans); font-size:8pt; color:var(--sub); } }
@page cover { margin:0; @bottom-left { content:none; } @bottom-right { content:none; } }
* { box-sizing:border-box; }
body { font-family:var(--font-sans); color:var(--ink); font-size:12.5pt; line-height:1.58; margin:0; }
p { margin:0 0 3.2mm; } strong { font-weight:700; }
h2 { font-family:var(--font-head); font-weight:700; font-size:25pt; line-height:1.1; letter-spacing:-.5px;
  margin:2mm 0 5mm; break-before:page; page-break-before:always; break-after:avoid; }
h2:after { content:""; display:block; width:22mm; height:3px; background:var(--accent); margin-top:4mm; }
body > h2:first-of-type { break-before:auto; page-break-before:auto; }  /* вступление и первый H2 на одной странице */
h3 { font-size:14pt; margin:5mm 0 2mm; break-after:avoid; }
ul, ol { margin:0 0 3.2mm 6mm; padding:0; } li { margin:1mm 0; }
code { font-family:'JetBrains Mono','Noto Sans Mono',monospace; font-size:.9em; }
.cover { page:cover; position:relative; width:210mm; height:297mm; overflow:hidden;
  background:var(--bg) no-repeat center/cover; }
.cover .scrim { position:absolute; top:0; left:0; right:0; height:62%;
  background:linear-gradient(180deg, var(--scrim-a), var(--scrim-b) 45%, rgba(0,0,0,0)); }
.cover .bl { position:absolute; top:34mm; left:18mm; right:18mm; }
.cover .k { font-weight:700; font-size:11pt; letter-spacing:4px; text-transform:uppercase; color:var(--accent); margin-bottom:6mm; }
.cover .t { font-family:var(--font-head); font-size:40pt; font-weight:700; line-height:1.04; letter-spacing:-1px; }
.cover .s { margin-top:7mm; font-size:13pt; line-height:1.45; color:var(--sub); max-width:150mm; }
.cover .f { position:absolute; bottom:14mm; left:18mm; font-weight:600; font-size:11pt; color:var(--sub); }
.box { margin:5mm 0; padding:6mm 7mm; background:var(--panel-bg); border:1px solid var(--panel-br);
  border-radius:5mm; break-inside:avoid; }
.box > .h { font-weight:700; font-size:10pt; letter-spacing:2px; text-transform:uppercase; color:var(--accent); margin-bottom:3mm; }
.box > :last-child { margin-bottom:0; }
.caveat { border-left:4px solid var(--bad); } .caveat > .h { color:var(--bad); }
.bad { border-left:4px solid var(--bad); } .bad > .h { color:var(--bad); }
.good { border-left:4px solid var(--good); } .good > .h { color:var(--good); }
blockquote { margin:5mm 0; padding:4mm 6mm; border-left:3px solid var(--accent); background:var(--chip-bg);
  font-family:var(--font-head); font-size:15pt; line-height:1.4; break-inside:avoid; }
blockquote p { margin:0; }
.fig { margin:4mm 0; break-inside:avoid; }
"""

BLOCK = re.compile(r'^:::(\w+)[ \t]*(.*?)\n(.*?)^:::[ \t]*$', re.M | re.S)
VAR = re.compile(r'var\(\s*(--[\w-]+)\s*\)')


def theme_tokens(css):
    """--имя: значение из :root темы."""
    root = re.search(r':root\s*\{(.*?)\}', css, re.S)
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', root.group(1))) if root else {}


def resolve_vars(css, tokens):
    """Подставить var(--x) значениями темы. WeasyPrint понимает var() не везде (например в @page)."""
    for _ in range(3):
        css = VAR.sub(lambda m: tokens.get(m.group(1), m.group(0)), css)
    return css


def split_front(text):
    meta = {}
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.split(' #')[0].strip()
        text = text[m.end():]
    return meta, text


def _lines(body):
    return [ln.strip() for ln in body.strip().splitlines() if ln.strip()]


def _pairs(body):
    out = []
    for ln in _lines(body):
        a, _, b = ln.partition('|')
        out.append((a.strip(), b.strip()))
    return out


def md_to_html(md, palette):
    import markdown

    def conv(s):
        return markdown.markdown(s, extensions=['extra', 'sane_lists'])

    def block(m):
        kind, title, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        head = f'<div class="h">{html.escape(title)}</div>' if title else ''
        if kind == 'numbers':
            return '\n' + ig.numbers(_pairs(body), palette) + '\n'
        if kind == 'bars':
            items = [(a, float(b.replace(',', '.') or 0)) for a, b in _pairs(body)]
            return f'\n<div class="box">{head}{ig.bars(items, palette)}</div>\n'
        if kind == 'flow':
            return '\n' + ig.flow(_lines(body), palette) + '\n'
        cls = kind if kind in ('caveat', 'bad', 'good') else 'callout'
        return f'\n<div class="box {cls}">{head}{conv(body)}</div>\n'

    parts, pos = [], 0
    for m in BLOCK.finditer(md):
        parts.append(conv(md[pos:m.start()]))
        parts.append(block(m))
        pos = m.end()
    parts.append(conv(md[pos:]))
    return ''.join(parts)


def build_html(md_text, theme_css, base_dir):
    meta, body = split_front(md_text)
    tokens = theme_tokens(theme_css)
    palette = {'ink': tokens.get('--ink'), 'sub': tokens.get('--sub'), 'accent': tokens.get('--accent'),
               'accent2': tokens.get('--accent2'), 'panel': tokens.get('--panel-bg'), 'line': tokens.get('--panel-br'),
               'font': (tokens.get('--font-sans') or '').replace("'", '')}
    palette = {k: v for k, v in palette.items() if v}
    tokens.setdefault('--scrim-a', 'rgba(255,255,255,.85)')
    tokens.setdefault('--scrim-b', 'rgba(255,255,255,.5)')
    footer = meta.get('footer', '').replace('"', "'")
    css = resolve_vars(CSS.replace('%FOOTER%', footer) + theme_css, tokens)
    style = ''
    if meta.get('cover'):
        uri = (Path(base_dir) / meta['cover']).resolve().as_uri()
        style = f' style="background-image:url(\'{uri}\')"'
    cover = (f'<div class="cover"{style}><div class="scrim"></div><div class="bl">'
             f'<div class="k">{html.escape(meta.get("kicker", ""))}</div>'
             f'<div class="t">{html.escape(meta.get("title", ""))}</div>'
             f'<div class="s">{html.escape(meta.get("subtitle", ""))}</div></div>'
             f'<div class="f">{html.escape(meta.get("footer", ""))}</div></div>')
    doc = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{css}</style></head>'
           f'<body>{cover}{md_to_html(body, palette)}</body></html>')
    return meta, doc


def text_gates(md_text):
    """Гейты текста до рендера: те же, что у карточек, на весь документ одной «карточкой»."""
    issues = cardlib.check_cards([{'name': 'doc', 'body': md_text, 'last': True}])
    return cardlib.hard(issues)


def pdf_gates(pdf):
    bad = cardlib.check_pdf_size(pdf, *A4_PT)
    if shutil.which('pdftotext'):
        txt = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True).stdout
        if '—' in txt:
            bad.append(f'в PDF {txt.count("—")} длинных тире (проверь подписи SVG и колонтитулы)')
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description='Markdown → PDF-методичка A4')
    ap.add_argument('input')
    ap.add_argument('--theme', default='paper', help='тема из themes/ или путь к CSS')
    ap.add_argument('--out', default='out/longread')
    a = ap.parse_args(argv)

    src = Path(a.input)
    md_text = src.read_text(encoding='utf-8')
    issues = text_gates(md_text)
    for s in issues:
        print(s)
    if issues:
        return 1
    try:
        import markdown  # noqa: F401
        from weasyprint import HTML
    except ImportError as e:
        print(f'нет зависимости ({e.name}): pip install -r requirements.txt', file=sys.stderr)
        return 3
    if not shutil.which('pdfinfo'):
        print('нет pdfinfo: поставь poppler', file=sys.stderr)
        return 3
    meta, doc = build_html(md_text, cardlib.load_theme(a.theme), src.parent)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / f'{src.stem}.pdf'
    HTML(string=doc, base_url=str(src.parent)).write_pdf(str(pdf))
    bad = pdf_gates(pdf)
    for s in bad:
        print(s, file=sys.stderr)
    if bad:
        return 2
    print(pdf)
    return 0


if __name__ == '__main__':
    sys.exit(main())
