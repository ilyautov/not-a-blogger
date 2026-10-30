#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Учебник learn/<lang>/ одним PDF A4 в журнальной вёрстке.

Порядок: обложка, оглавление с номерами страниц, маршрут обучения, главы 00, 00a, 01–10, словарь, задняя обложка.
Глава открывается рубрикой, заголовком, вводным абзацем и иллюстрацией из assets/textbook/; текст идёт в две
колонки, код, таблицы и выноски на всю ширину. Ссылки между главами становятся переходами внутри PDF, остальные
относительные ссылки ведут на GitHub. Схема mermaid рисуется SVG-линией шагов: WeasyPrint mermaid не понимает.

Запуск (нужны weasyprint и markdown из tools/carousels/requirements.txt и poppler: pdfinfo, pdftotext;
шрифты PT Sans, PT Sans Narrow, PT Serif по имени, OFL; без них WeasyPrint подставит Noto):
  python3 scripts/build_textbook_pdf.py                 # ru и en в dist/
  python3 scripts/build_textbook_pdf.py --lang ru --out dist

Проверки после рендера: каждая страница A4, в тексте PDF нет длинного тире, все главы попали в PDF.
Коды возврата: 0 успех; 2 проверки PDF не прошли; 3 нет зависимостей.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'carousels'))
REPO_URL = 'https://github.com/ilyautov/not-a-blogger'
ART = ROOT / 'assets' / 'textbook'

ORDER = ['ROADMAP', '00-first-video', '00a-how-it-works', '01-idea-hook-script', '02-text-humanizer', '03-voice',
         '04-image-and-frame', '05-camera-editing', '06-sound-captions', '07-assembly-qa', '08-vertical-publishing',
         '09-carousels-slides', '10-working-with-agent', 'glossary']

# иллюстрация главы: файл в assets/textbook/; нет файла, глава открывается без картинки
ART_FILES = {'cover': 'cover.jpg', '00-first-video': 'ch00.jpg', '00a-how-it-works': 'ch00a.jpg',
             '01-idea-hook-script': 'ch01.jpg', '02-text-humanizer': 'ch02.jpg', '03-voice': 'ch03.jpg',
             '04-image-and-frame': 'ch04.jpg', '05-camera-editing': 'ch05.jpg', '06-sound-captions': 'ch06.jpg',
             '07-assembly-qa': 'ch07.jpg', '08-vertical-publishing': 'ch08.jpg', '09-carousels-slides': 'ch09.jpg',
             '10-working-with-agent': 'ch10.jpg'}

META = {
    'ru': {'cover': ['Ролики', 'с агентом'], 'strap': 'без блогерства: как ИИ-агент собирает короткие видео и как их проверять',
           'tags': 'ИИ / видео / агенты', 'edition': 'Учебник · маршрут, двенадцать глав и словарь',
           'lead': 'Агент собирает ролик. Человек решает, выходит ли он.',
           'stats': ['рецептов в репозитории', 'проверены на наших роликах', 'глав учебника', 'разборов роликов'],
           'footer': 'Ролики с агентом · учебник', 'toc': 'Содержание', 'contents_kicker': 'Что внутри',
           'inside': 'Что внутри', 'inside_kicker': 'Цифры и маршрут',
           'inside_text': 'Каждый совет учебника опирается на рецепт: короткую карточку с проблемой, решением и тем, как мы '
                          'это увидели. «Проверено» значит, что рецепт сработал на наших роликах; «гипотеза» значит, что '
                          'пока это только идея. Цифры ниже считаются по репозиторию при каждой сборке.',
           'proven': 'проверено', 'hypothesis': 'гипотеза', 'by_section': 'Рецепты по разделам',
           'share': 'проверено', 'route': 'Маршрут обучения: четыре ступени', 'recipes_ch': 'рецептов к главе',
           'sections': 'разделы',
           'labels': {'prob': ('Проблема.',), 'seen': ('Как мы это увидели.',), 'do': ('Что делаем.', 'Что делаешь.'),
                      'break': ('Где ломается.',), 'done': ('Готово, когда', 'Готово')},
           'chapter': 'Глава', 'ROADMAP': 'С чего начать', 'glossary': 'Справочник', 'diagram': 'Схема конвейера',
           'back_kicker': 'not-a-blogger · 2026', 'back_title': 'Спасибо, что дочитал.',
           'back_text': 'Учебник живёт в открытом репозитории вместе с рецептами, шаблонами и разборами роликов. '
                        'Нашёл ошибку или проверил рецепт на своём ролике: открой issue или pull request.',
           'back_links': [('Репозиторий', REPO_URL), ('Telegram', 'https://t.me/gorilla_under_hood'),
                          ('Сайт', 'https://aifrontier.tech')]},
    'en': {'cover': ['Videos', 'with an agent'], 'strap': 'no blogging: how an AI agent builds short videos and how to check them',
           'tags': 'AI / video / agents', 'edition': 'Textbook · roadmap, twelve chapters and a glossary',
           'lead': 'The agent builds the video. A person decides whether it ships.',
           'stats': ['recipes in the repo', 'proven on our own videos', 'textbook chapters', 'video teardowns'],
           'footer': 'Videos with an agent · textbook', 'toc': 'Contents', 'contents_kicker': 'Inside',
           'inside': 'Inside', 'inside_kicker': 'Numbers and route',
           'inside_text': 'Every piece of advice in the textbook rests on a recipe: a short card with the problem, the fix '
                          'and how we saw it. "Proven" means the recipe worked on our own videos; "hypothesis" means it is '
                          'only an idea so far. The numbers below are counted from the repository on every build.',
           'proven': 'proven', 'hypothesis': 'hypothesis', 'by_section': 'Recipes by section',
           'share': 'proven', 'route': 'Learning roadmap: four stages', 'recipes_ch': 'recipes for this chapter',
           'sections': 'sections',
           'labels': {'prob': ('Problem.',), 'seen': ('How we saw it.',), 'do': ('What we do.', 'What you do.'),
                      'break': ('Where it breaks.',), 'done': ('Done when', 'Done')},
           'chapter': 'Chapter', 'ROADMAP': 'Start here', 'glossary': 'Reference', 'diagram': 'Pipeline diagram',
           'back_kicker': 'not-a-blogger · 2026', 'back_title': 'Thanks for reading.',
           'back_text': 'The textbook lives in an open repository together with recipes, templates and video teardowns. '
                        'Found a mistake or tested a recipe on your own video: open an issue or a pull request.',
           'back_links': [('Repository', REPO_URL), ('Telegram', 'https://t.me/gorilla_under_hood'),
                          ('Site', 'https://aifrontier.tech')]},
}

INK, PAPER, LIME, OLIVE, RED, SUB, LINE, PANEL = ('#1a2023', '#fbfbf8', '#c8f03c', '#4b6410', '#c0392b', '#5a6168',
                                                  '#dfe3d9', '#f2f5ec')
SANS = "'PT Sans','Noto Sans',sans-serif"
NARROW = "'PT Sans Narrow','PT Sans','Noto Sans',sans-serif"
SERIF = "'PT Serif','Noto Serif',serif"
MONO = "'JetBrains Mono','Menlo','Noto Sans Mono',monospace"

CSS = f"""
@page {{ size:A4; margin:21mm 17mm 19mm; background:{PAPER};
  @top-left {{ content:"NOT-A-BLOGGER"; font:700 7.5pt {SANS}; letter-spacing:1.2px; color:{INK};
    vertical-align:bottom; padding-bottom:2mm; border-bottom:2pt solid {LIME}; }}
  @top-right {{ content:string(chap); font:400 7.5pt {SANS}; letter-spacing:1px; text-transform:uppercase; color:{SUB};
    vertical-align:bottom; padding-bottom:2mm; border-bottom:.5pt solid {LINE}; }}
  @bottom-left {{ content:"%FOOTER%"; font:400 7.5pt {SANS}; letter-spacing:1px; text-transform:uppercase; color:{SUB};
    border-top:.5pt solid {LINE}; padding-top:2mm; vertical-align:top; }}
  @bottom-right {{ content:counter(page, decimal-leading-zero); font:700 8pt {SANS}; color:{INK};
    border-top:.5pt solid {LINE}; padding-top:2mm; vertical-align:top; }} }}
@page cover {{ margin:0; @top-left {{ content:none; border:none; }} @top-right {{ content:none; border:none; }}
  @bottom-left {{ content:none; border:none; }} @bottom-right {{ content:none; border:none; }} }}
@page back {{ margin:0; background:{INK}; @top-left {{ content:none; border:none; }} @top-right {{ content:none; border:none; }}
  @bottom-left {{ content:none; border:none; }} @bottom-right {{ content:none; border:none; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:{SERIF}; font-size:9.6pt; line-height:1.5; color:{INK}; }}
a {{ color:{OLIVE}; text-decoration:none; }}
p {{ margin:0 0 2.4mm; }}
strong {{ font-weight:700; }}
code {{ font-family:{MONO}; font-size:.84em; background:{PANEL}; padding:0 .6mm; border-radius:.8mm; overflow-wrap:break-word; }}

/* обложка */
.cover {{ page:cover; width:210mm; height:297mm; padding:13mm 17mm 0; position:relative; background:{PAPER}; }}
.ctop {{ font:700 7.5pt {SANS}; letter-spacing:1.2px; text-transform:uppercase; padding-bottom:2mm;
  border-bottom:.5pt solid {LINE}; }}
.ctop .l {{ border-bottom:2pt solid {LIME}; padding-bottom:2mm; }}
.ctop .r {{ float:right; font-weight:400; color:{SUB}; }}
.cover h1 {{ font:700 66pt/0.93 {NARROW}; text-transform:uppercase; letter-spacing:-.5pt; margin:13mm 0 6mm; }}
.strap {{ font:700 17pt/1.25 {SANS}; max-width:150mm; margin-bottom:6mm; }}
.edition {{ font:700 10pt {SANS}; border-top:1.2pt solid {INK}; padding-top:3mm; }}
.cimg {{ position:absolute; left:0; right:0; top:110mm; height:130mm; overflow:hidden; }}
.cimg img {{ width:210mm; height:130mm; object-fit:cover; display:block; }}
.cbottom {{ position:absolute; left:17mm; right:17mm; top:250mm; }}
.cbottom .lead {{ font:700 13.5pt/1.3 {SANS}; width:72mm; float:left; }}
.stats {{ margin-left:80mm; }}
.stat {{ display:inline-block; width:22mm; vertical-align:top; margin-right:1mm; }}
.stat b {{ display:block; font:700 24pt/1 {NARROW}; color:{RED}; }}
.stat span {{ display:block; font:400 7pt/1.25 {SANS}; color:{SUB}; margin-top:1.5mm; }}

/* оглавление */
.toc {{ break-before:page; }}
.toc ol {{ list-style:none; margin:4mm 0 0; padding:0; }}
.toc li {{ border-bottom:.5pt solid {LINE}; padding:2.6mm 0; }}
.toc a {{ color:{INK}; font:400 12pt {SANS}; display:block; }}
.toc a::after {{ content:leader(' ') target-counter(attr(href), page, decimal-leading-zero); font-weight:700; }}
.toc .n {{ display:inline-block; width:15mm; font:700 17pt/1 {NARROW}; color:{RED}; }}

/* глава */
.chap {{ break-before:page; }}
.kicker {{ font:700 7.5pt {SANS}; letter-spacing:1.3px; text-transform:uppercase; color:{OLIVE}; margin:0 0 3mm; }}
.kicker::before {{ content:""; display:inline-block; width:7mm; height:2pt; background:{LIME}; vertical-align:middle; margin-right:2mm; }}
h2.ct {{ font:700 34pt/1 {NARROW}; margin:0 0 4mm; string-set:chap content(); bookmark-level:1; text-wrap:balance; }}
.toc h2.ct {{ string-set:none; }}
.lede {{ font:400 12pt/1.4 {SANS}; color:#3b4249; margin:0 0 5mm; padding-bottom:4mm; border-bottom:1.2pt solid {INK}; }}
.lede p {{ margin:0; }}
.hero {{ margin:0 0 6mm; }}
.hero img {{ width:100%; height:100mm; object-fit:cover; display:block; }}
.body {{ columns:2; column-gap:8mm; text-align:justify; hyphens:auto; }}
.body h3 {{ font:700 12.5pt/1.2 {SANS}; text-align:left; margin:4.5mm 0 2mm; break-after:avoid; bookmark-level:2; hyphens:manual; }}
.body h3::before {{ content:""; display:block; width:9mm; height:2pt; background:{LIME}; margin-bottom:2mm; }}
.body h4 {{ font:700 10pt/1.25 {SANS}; text-align:left; margin:3.5mm 0 1.5mm; break-after:avoid; bookmark-level:none; }}
.body h5 {{ font:700 9.5pt {SANS}; margin:3mm 0 1mm; }}
.body ul, .body ol {{ margin:0 0 2.6mm 4.5mm; padding:0; text-align:left; }}
.body li {{ margin:.8mm 0; }}
.body li::marker {{ color:{OLIVE}; font-family:{SANS}; font-weight:700; }}
.body .wide, .body .box, .body .fig, .body img, .body blockquote, .body hr {{ column-span:all; }}
pre {{ background:{INK}; color:#e9eef0; font:400 7.9pt/1.5 {MONO}; padding:3.2mm 4mm; margin:2mm 0 4mm;
  border-left:2.5pt solid {LIME}; border-radius:1.2mm; white-space:pre-wrap; overflow-wrap:break-word; text-align:left;
  break-inside:avoid; }}
pre code {{ background:none; color:inherit; padding:0; font-size:inherit; }}
table {{ border-collapse:collapse; width:100%; margin:2mm 0 5mm; font:400 8.6pt/1.4 {SANS}; text-align:left; }}
th {{ background:{INK}; color:#fff; font-weight:700; padding:1.8mm 2.2mm; vertical-align:bottom; }}
td {{ padding:1.6mm 2.2mm; border-bottom:.5pt solid {LINE}; vertical-align:top; }}
td:first-child {{ font-weight:700; }}
tr {{ break-inside:avoid; }}
.box {{ background:{PANEL}; border-top:2.5pt solid {LIME}; padding:4mm 5mm; margin:2mm 0 5mm; break-inside:avoid;
  font-family:{SANS}; font-size:9.3pt; text-align:left; }}
.box > .h {{ font:700 7.5pt {SANS}; letter-spacing:1.3px; text-transform:uppercase; color:{OLIVE}; margin-bottom:2mm; }}
.box > :last-child {{ margin-bottom:0; }}
.box.caveat, .box.bad {{ border-top-color:{RED}; }} .box.caveat > .h, .box.bad > .h {{ color:{RED}; }}
blockquote {{ margin:3mm 0 5mm; padding:1mm 0 1mm 5mm; border-left:3pt solid {LIME}; font:700 12.5pt/1.35 {SANS};
  text-align:left; break-inside:avoid; }}
blockquote p {{ margin:0 0 1.5mm; }}
.body img {{ max-width:100%; max-height:85mm; display:block; margin:2mm auto 4mm; }}
.fig {{ margin:2mm 0 5mm; break-inside:avoid; }}
.figcap {{ font:700 7.5pt {SANS}; letter-spacing:1.3px; text-transform:uppercase; color:{OLIVE}; margin-bottom:2mm;
  border-bottom:.5pt solid {LINE}; padding-bottom:1.5mm; }}

/* метки абзацев «проблема → как увидели → что делаем → где ломается» и «готово, когда» */
.lab > strong:first-child {{ font:700 6.8pt {SANS}; letter-spacing:1px; text-transform:uppercase; padding:.5mm 1.6mm;
  border-radius:.8mm; margin-right:1.2mm; vertical-align:1px; }}
.lab-prob > strong:first-child {{ background:{RED}; color:#fff; }}
.lab-seen > strong:first-child {{ background:#e1e5da; color:{INK}; }}
.lab-do > strong:first-child {{ background:{LIME}; color:{INK}; }}
.lab-break > strong:first-child {{ background:#f2d48f; color:{INK}; }}
.lab-prob {{ margin-top:3.5mm; }}
p.done {{ background:{INK}; color:#e9eef0; padding:2.6mm 3.4mm 2.6mm 3.4mm; border-left:3pt solid {LIME}; text-align:left;
  font-family:{SANS}; font-size:9pt; break-inside:avoid; }}
p.done > strong:first-child {{ color:{LIME}; }}
p.done a {{ color:{LIME}; }} p.done code {{ background:#2c363b; color:#fff; }}

/* полоса рецептов главы */
.rstrip {{ margin:0 0 6mm; padding:3mm 0; border-top:.5pt solid {LINE}; border-bottom:.5pt solid {LINE}; font-family:{SANS}; }}
.rs-n {{ display:inline-block; width:36mm; vertical-align:middle; }}
.rs-n b {{ font:700 26pt/1 {NARROW}; color:{RED}; margin-right:1.5mm; }}
.rs-n span {{ display:inline-block; width:18mm; font-size:7.6pt; line-height:1.2; color:{SUB}; vertical-align:middle; }}
.rs-bar {{ display:inline-block; width:46mm; height:4.2mm; background:#e1e5da; vertical-align:middle; margin-right:4mm; }}
.rs-bar i {{ display:block; height:4.2mm; background:{LIME}; border-right:1pt solid {INK}; }}
.rs-leg {{ display:inline-block; vertical-align:middle; font-size:8pt; line-height:1.35; color:{SUB}; width:86mm; }}
.rs-leg b {{ color:{INK}; }}
.sw {{ display:inline-block; width:2.6mm; height:2.6mm; margin:0 1mm 0 2mm; vertical-align:-.3mm; }}
.sw.p {{ background:{LIME}; border:.5pt solid {INK}; }} .sw.h {{ background:#e1e5da; }}

/* страница «что внутри» */
.inside {{ break-before:page; }}
.inside .intro {{ font:400 11pt/1.45 {SANS}; color:#3b4249; margin:0 0 6mm; max-width:150mm; }}
.stages {{ margin:0 0 7mm; }}
.stage {{ display:inline-block; width:41mm; vertical-align:top; margin-right:2.3mm; border-top:2.5pt solid {INK};
  padding-top:2.5mm; font-family:{SANS}; }}
.stage:last-child {{ margin-right:0; }}
.stage b {{ display:block; font:700 30pt/1 {NARROW}; color:{RED}; }}
.stage .t {{ display:block; font-weight:700; font-size:10.5pt; margin:1.5mm 0 1mm; }}
.stage .d {{ display:block; font-size:7.6pt; color:{OLIVE}; text-transform:uppercase; letter-spacing:.8px; margin-bottom:1.2mm; }}
.stage .g {{ display:block; font-size:8pt; line-height:1.3; color:{SUB}; }}
.duo {{ margin-top:2mm; }}
.duo .chart {{ display:inline-block; width:118mm; vertical-align:top; }}
.duo .donut {{ display:inline-block; width:52mm; margin-left:5mm; vertical-align:top; text-align:center; font-family:{SANS}; }}
.donut .cap {{ font-size:8pt; color:{SUB}; margin-top:1mm; }}

/* задняя обложка */
.back {{ page:back; break-before:page; width:210mm; height:297mm; padding:30mm 20mm; color:#fff; background:{INK}; }}
.back .kicker {{ color:{LIME}; }}
.back h2 {{ font:700 54pt/1 {NARROW}; margin:6mm 0 8mm; color:#fff; bookmark-level:none; }}
.back p {{ font:400 13pt/1.45 {SANS}; color:#c9d0d4; max-width:150mm; }}
.links {{ margin-top:14mm; border:.5pt solid #3a454b; border-radius:2mm; padding:6mm 7mm; background:#222b30; }}
.links div {{ font:400 11pt/1.9 {SANS}; }}
.links b {{ display:inline-block; width:34mm; color:#8d979c; font-weight:400; }}
.links a {{ color:{LIME}; }}
"""

# ограждение кода: ``` или ~~~ любой длины, закрывается тем же; внутри заголовки и ссылки не трогаем
FENCE = re.compile(r'^(?P<f>`{3,}|~{3,})[^\n]*\n.*?^(?P=f)(?:(?<=`)`*|(?<=~)~*)[ \t]*$', re.M | re.S)
MERMAID = re.compile(r'^(`{3,}|~{3,})mermaid')
CODE_WIDTH = 80  # столько символов моноширинного влезает в строку PDF; длиннее строка переносится внутри команды
LINK = re.compile(r'(!?)\[([^\]]*)\]\(([^)\s]+)\)')
HEAD = re.compile(r'^(#{1,3}) ', re.M)


def anchor(stem):
    return 'ch-' + stem.lower()


def mermaid_steps(block):
    """flowchart: «A[Бриф<br/>BRIEF.md] --> B[...]» → [(подпись, подстрочник)] в порядке появления узлов."""
    lines = [l.strip() for l in block.splitlines()[1:-1] if l.strip() and not l.strip().startswith('%%')]
    # поддерживаем только линейную схему: узлы A или A[подпись], стрелки -->. Ромбы, скобки, подписи стрелок
    # потерялись бы в линии шагов, поэтому лучше упасть и переписать схему. Подписи вырезаем до проверки формы:
    # скобки внутри подписи в кавычках («A["Scene (HTML)"]») законны
    node = r'\w+(?:\[(?:"[^"]*"|[^\]"]*)\])?'
    ok = re.compile(rf'^{node}(?:\s*-->\s*{node})*;?$')
    if not lines or not re.match(r'^(flowchart|graph)\b', lines[0]) or not all(ok.match(l) for l in lines[1:]):
        raise SystemExit('mermaid: поддерживается только flowchart с узлами A[...] и стрелками -->')
    seen, steps = set(), []
    for node, label in re.findall(r'(\w+)\[("[^"]*"|[^\]"]*)\]', '\n'.join(lines[1:])):
        if node in seen:
            continue
        seen.add(node)
        parts = re.split(r'\s*<br\s*/?>\s*', label.strip().strip('"'), maxsplit=1)
        head, sub = (parts + [''])[:2]
        steps.append((head.strip(), sub.strip()))
    return steps


def mermaid_caption(block):
    """Первая строка-комментарий %% внутри блока mermaid: подпись схемы в PDF (GitHub её не показывает)."""
    for l in block.splitlines()[1:]:
        if l.strip().startswith('%%'):
            return l.strip()[2:].strip()
        if l.strip():
            return ''
    return ''


def wrap(text, width):
    """Перенос по словам для подписей SVG: в SVG 1.1 текст сам не переносится."""
    lines, cur = [], ''
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f'{cur} {w}'.strip()
    return lines + ([cur] if cur else [])


def chevrons_svg(steps):
    """До шести шагов: карточки в ряд со стрелками, номер в лаймовом круге, подпись и файл под ней."""
    n, W, gap = len(steps), 900, 26
    w = (W - gap * (n - 1)) / n
    hl = max(8, int(w / 9.6))
    sl = max(8, int(w / 8.4))
    heads = [wrap(h, hl) for h, _ in steps]
    subs = [wrap(s, sl) if s else [] for _, s in steps]
    H = 62 + 22 * max(len(x) for x in heads) + 17 * max(len(x) for x in subs) + 14
    e = []
    for i in range(n):
        x = i * (w + gap)
        e.append(f'<rect x="{x:.1f}" y="18" width="{w:.1f}" height="{H - 22}" rx="6" fill="{PANEL}" stroke="{INK}" stroke-width="1.6"/>')
        e.append(f'<rect x="{x:.1f}" y="18" width="{w:.1f}" height="6" fill="{LIME}"/>')
        e.append(f'<circle cx="{x + 24:.1f}" cy="18" r="16" fill="{LIME}" stroke="{INK}" stroke-width="1.6"/>')
        e.append(f'<text x="{x + 24:.1f}" y="24" text-anchor="middle" font-family="PT Sans Narrow, PT Sans, sans-serif" '
                 f'font-weight="700" font-size="17" fill="{INK}">{i + 1}</text>')
        y = 60
        for line in heads[i]:
            e.append(f'<text x="{x + 12:.1f}" y="{y}" font-family="PT Sans, sans-serif" font-weight="700" font-size="16.5" '
                     f'fill="{INK}">{html.escape(line)}</text>')
            y += 22
        y += 2
        for line in subs[i]:
            e.append(f'<text x="{x + 12:.1f}" y="{y}" font-family="Menlo, monospace" font-size="12.5" '
                     f'fill="{SUB}">{html.escape(line)}</text>')
            y += 17
        if i < n - 1:
            ax, ay = x + w + 3, 18 + (H - 22) / 2
            e.append(f'<path d="M{ax:.1f} {ay - 9:.1f} L{ax + gap - 6:.1f} {ay:.1f} L{ax:.1f} {ay + 9:.1f} Z" fill="{INK}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">{"".join(e)}</svg>'


def flow_svg(steps):
    """Шаги конвейера линией метро в две колонки: номер в лаймовом круге, подпись, файл под ней."""
    half = (len(steps) + 1) // 2
    row, W = 64, 900
    H = row * half + 8
    e = []
    for i, (head, sub) in enumerate(steps):
        col, r = divmod(i, half)
        x, y = 8 + col * 450, 8 + r * row
        if r < half - 1 and i < len(steps) - 1:
            e.append(f'<line x1="{x + 21}" y1="{y + 42}" x2="{x + 21}" y2="{y + row}" stroke="{INK}" stroke-width="2.4"/>')
        e.append(f'<circle cx="{x + 21}" cy="{y + 21}" r="20" fill="{LIME}" stroke="{INK}" stroke-width="2"/>')
        e.append(f'<text x="{x + 21}" y="{y + 28}" text-anchor="middle" font-family="PT Sans Narrow, PT Sans, sans-serif" '
                 f'font-weight="700" font-size="20" fill="{INK}">{i + 1}</text>')
        e.append(f'<text x="{x + 54}" y="{y + 19}" font-family="PT Sans, sans-serif" font-weight="700" font-size="18" '
                 f'fill="{INK}">{html.escape(head)}</text>')
        if sub:
            e.append(f'<text x="{x + 54}" y="{y + 41}" font-family="Menlo, monospace" font-size="14" '
                     f'fill="{SUB}">{html.escape(sub)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">{"".join(e)}</svg>'


def mermaid_block(block, title):
    steps = mermaid_steps(block)
    svg = chevrons_svg(steps) if len(steps) <= 6 else flow_svg(steps)
    cap = mermaid_caption(block) or title
    return f'\n<div class="fig" markdown="0"><div class="figcap">{html.escape(cap)}</div>{svg}</div>\n'


def recipes_for(stem):
    recipes = json.loads((ROOT / 'recipes' / 'index.json').read_text(encoding='utf-8'))
    learn = {}
    for r in recipes:
        m = re.search(r'^learn:\s*(\S+)', (ROOT / r['path']).read_text(encoding='utf-8'), re.M)
        if m and Path(m.group(1)).stem == stem:
            learn[r['id']] = r
    return list(learn.values())


def recipe_strip(stem, lang):
    """Полоса под иллюстрацией: сколько рецептов у главы, доля проверенных, разделы. Считается по recipes/."""
    rs = recipes_for(stem)
    if not rs:
        return ''
    m = META[lang]
    proven = sum(r['status'] == 'proven' for r in rs)
    secs = sorted({r['section'] for r in rs})
    pct = 100 * proven / len(rs)
    return (f'<div class="rstrip"><div class="rs-n"><b>{len(rs)}</b><span>{m["recipes_ch"]}</span></div>'
            f'<div class="rs-bar"><i style="width:{pct:.1f}%"></i></div>'
            f'<div class="rs-leg"><span class="sw p"></span><b>{proven}</b> {m["proven"]}'
            f'<span class="sw h"></span><b>{len(rs) - proven}</b> {m["hypothesis"]}'
            f' · {m["sections"]}: {", ".join(secs)}</div></div>')


def label_paragraphs(body_html, lang):
    """Абзацы-рецепты внутри глав получают цветную метку, «готово, когда» становится тёмной плашкой."""
    for kind, words in META[lang]['labels'].items():
        cls = 'done' if kind == 'done' else f'lab lab-{kind}'
        for w in words:
            body_html = body_html.replace(f'<p><strong>{w}</strong>', f'<p class="{cls}"><strong>{w}</strong>')
    return body_html


def rewrite_link(m, src, lang):
    bang, text, target = m.groups()
    if re.match(r'^[a-z]+:', target):
        return m.group(0)
    if target.startswith('#'):
        # якорь подраздела внутри главы: в PDF у подразделов нет id, на GitHub есть
        if bang:
            return m.group(0)
        return f'[{text}]({REPO_URL}/blob/main/{src.relative_to(ROOT).as_posix()}{target})'
    path, _, frag = target.partition('#')
    abs_path = (src.parent / path).resolve()
    if bang:
        return f'![{text}]({abs_path.as_uri()})'
    try:
        rel = abs_path.relative_to(ROOT)
    except ValueError:
        return text
    # ссылка на главу без якоря ведёт внутрь PDF; с якорем подраздела на GitHub, где этот якорь есть
    if rel.parent == Path('learn') / lang and rel.stem in ORDER and not frag:
        return f'[{text}](#{anchor(rel.stem)})'
    kind = 'tree' if abs_path.is_dir() else 'blob'
    return f'[{text}]({REPO_URL}/{kind}/main/{rel.as_posix()}' + (f'#{frag}' if frag else '') + ')'


def chapter_md(src, lang):
    """Одна глава → кусок общего Markdown: без строки-переключателя языка, заголовки на уровень ниже,
    якорь главы, ссылки переписаны, mermaid заменён SVG. Код в ``` не трогаем."""
    text = src.read_text(encoding='utf-8')
    text = re.sub(r'^\[(English version|Русская версия)\]\([^)]*\)\s*\n', '', text)
    out, pos = [], 0
    for f in FENCE.finditer(text):
        out.append(('t', text[pos:f.start()]))
        out.append(('c', f.group(0)))
        pos = f.end()
    out.append(('t', text[pos:]))
    parts = []
    for kind, chunk in out:
        if kind == 'c':
            parts.append(mermaid_block(chunk, META[lang]['diagram']) if MERMAID.match(chunk) else chunk)
            continue
        chunk = HEAD.sub(lambda h: '#' * (len(h.group(1)) + 1) + ' ', chunk)
        chunk = LINK.sub(lambda m: rewrite_link(m, src, lang), chunk)
        parts.append(chunk)
    body = ''.join(parts).strip()
    # первый заголовок главы получает якорь для оглавления и переходов: attr_list из markdown extra
    return re.sub(r'^## (.+)$', lambda h: f'## {h.group(1)} {{#{anchor(src.stem)}}}', body, count=1, flags=re.M)


def chapter_title(src):
    for line in src.read_text(encoding='utf-8').splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return src.stem


def split_title(title):
    """«03. Голос и TTS» → ('03', 'Голос и TTS'); без номера ('', title)."""
    m = re.match(r'^(\d+[a-zа]?)\.\s+(.+)$', title)
    return (m.group(1), m.group(2)) if m else ('', title)


def chapter_files(lang):
    d = ROOT / 'learn' / lang
    files = [d / f'{s}.md' for s in ORDER]
    missing = [str(f.relative_to(ROOT)) for f in files if not f.exists()]
    if missing:
        raise SystemExit('нет глав: ' + ', '.join(missing))
    return files


def book_md(lang):
    """Весь учебник одним Markdown (для проверок и подсчёта объёма) и названия глав."""
    files = chapter_files(lang)
    return '\n\n'.join(chapter_md(f, lang) for f in files) + '\n', [chapter_title(f) for f in files]


def plain_len(md):
    """Грубая длина текста главы без разметки: для сравнения с текстом PDF."""
    md = re.sub(r'<svg.*?</svg>', '', md, flags=re.S)
    md = re.sub(r'<[^>]+>', '', md)
    md = re.sub(r'\]\([^)]*\)', ']', md)
    return len(re.sub(r'[\s#*_`|>\[\]:{}-]', '', md))


def repo_stats():
    """Цифры для обложки считаются по репозиторию, а не пишутся руками."""
    recipes = json.loads((ROOT / 'recipes' / 'index.json').read_text(encoding='utf-8'))
    proven = sum(1 for r in recipes if r.get('status') == 'proven')
    examples = sum(1 for p in (ROOT / 'examples').iterdir() if (p / 'README.md').exists())
    chapters = sum(1 for s in ORDER if split_title(chapter_title(ROOT / 'learn' / 'ru' / f'{s}.md'))[0])
    return [len(recipes), proven, chapters, examples]


def art(key):
    p = ART / ART_FILES.get(key, '')
    return p.as_uri() if key in ART_FILES and p.exists() else ''


def inline_md(text):
    import markdown
    return markdown.markdown(text, extensions=['extra'])


LEDE_STOP = re.compile(r'^(#|[-*+] |\d+\. |\||<|:::|`|~|>|!\[|\*\*[^*]+\*\*\s*$)')


def chapter_html(src, lang, palette):
    import longread
    m = META[lang]
    md = chapter_md(src, lang)
    num, name = split_title(chapter_title(src))
    body = md.split('\n', 1)[1] if md.startswith('## ') else md
    blocks = body.strip().split('\n\n')
    lede = blocks.pop(0) if blocks and not LEDE_STOP.match(blocks[0].strip()) else ''
    kicker = f'{m["chapter"]} {num}' if num else m.get(src.stem, '')
    hero = art(src.stem)
    body_md = '\n\n'.join(blocks)
    # column-span WeasyPrint применяет к блокам, но не к table и pre: оборачиваем их в div на всю ширину
    body_html = re.sub(r'<(table|pre)\b', r'<div class="wide"><\1', longread.md_to_html(body_md, palette))
    body_html = re.sub(r'</(table|pre)>', r'</\1></div>', body_html)
    body_html = label_paragraphs(body_html, lang)
    return (f'<section class="chap"><div class="kicker">{html.escape(kicker)}</div>'
            f'<h2 class="ct" id="{anchor(src.stem)}">{html.escape(name)}</h2>'
            + (f'<div class="lede">{inline_md(lede)}</div>' if lede else '')
            + (f'<div class="hero"><img src="{hero}" alt=""></div>' if hero else '')
            + recipe_strip(src.stem, lang)
            + f'<div class="body">{body_html}</div></section>')


def cover_html(lang):
    m = META[lang]
    stats = ''.join(f'<div class="stat"><b>{v}</b><span>{html.escape(t)}</span></div>'
                    for v, t in zip(repo_stats(), m['stats']))
    img = art('cover')
    return (f'<section class="cover"><div class="ctop"><span class="l">NOT-A-BLOGGER</span>'
            f'<span class="r">{html.escape(m["tags"])}</span></div>'
            f'<h1>{"<br>".join(html.escape(x) for x in m["cover"])}</h1>'
            f'<div class="strap">{html.escape(m["strap"])}</div><div class="edition">{html.escape(m["edition"])}</div>'
            + (f'<div class="cimg"><img src="{img}" alt=""></div>' if img else '')
            + f'<div class="cbottom"><div class="lead">{html.escape(m["lead"])}</div><div class="stats">{stats}</div></div>'
            f'</section>')


def toc_html(lang, files):
    m = META[lang]
    rows = []
    for f in files:
        num, name = split_title(chapter_title(f))
        rows.append(f'<li><a href="#{anchor(f.stem)}"><span class="n">{num or "·"}</span>{html.escape(name)}</a></li>')
    return (f'<section class="toc"><div class="kicker">{html.escape(m["contents_kicker"])}</div>'
            f'<h2 class="ct">{html.escape(m["toc"])}</h2><ol>{"".join(rows)}</ol></section>')


def roadmap_stages(lang):
    """Строки первой таблицы ROADMAP: ступень, время, результат."""
    text = (ROOT / 'learn' / lang / 'ROADMAP.md').read_text(encoding='utf-8')
    rows = [r for r in re.findall(r'^\|(.+)\|\s*$', text, re.M)]
    out = []
    for r in rows[2:]:
        cells = [c.strip() for c in r.split('|')]
        if len(cells) < 3 or not re.match(r'^\d+\.', cells[0]):
            break
        num, _, name = cells[0].partition('.')
        out.append((num, name.strip(), cells[1], cells[2]))
    return out


def section_bars_svg(lang):
    recipes = json.loads((ROOT / 'recipes' / 'index.json').read_text(encoding='utf-8'))
    by = {}
    for r in recipes:
        p, h = by.get(r['section'], (0, 0))
        by[r['section']] = (p + (r['status'] == 'proven'), h + (r['status'] != 'proven'))
    rows = sorted(by.items(), key=lambda kv: (-sum(kv[1]), kv[0]))
    vmax = max(sum(v) for _, v in rows)
    row, W = 21, 560
    unit = 330 / vmax
    e = []
    for i, (sec, (p, h)) in enumerate(rows):
        y = i * row
        e.append(f'<text x="128" y="{y + 15}" text-anchor="end" font-family="Menlo, monospace" font-size="13" fill="{INK}">{sec}</text>')
        e.append(f'<rect x="138" y="{y + 3}" width="{p * unit:.1f}" height="15" fill="{LIME}" stroke="{INK}" stroke-width="1"/>')
        e.append(f'<rect x="{138 + p * unit:.1f}" y="{y + 3}" width="{h * unit:.1f}" height="15" fill="#e1e5da"/>')
        e.append(f'<text x="{146 + (p + h) * unit:.1f}" y="{y + 15}" font-family="PT Sans, sans-serif" font-size="13" '
                 f'fill="{SUB}">{p} + {h}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {row * len(rows) + 4}" width="100%">{"".join(e)}</svg>'


def donut_svg(part, total):
    import math
    a = 2 * math.pi * part / total
    r, cx, cy = 80, 100, 100
    x, y = cx + r * math.sin(a), cy - r * math.cos(a)
    big = 1 if a > math.pi else 0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e1e5da" stroke-width="34"/>'
            f'<path d="M{cx} {cy - r} A{r} {r} 0 {big} 1 {x:.2f} {y:.2f}" fill="none" stroke="{LIME}" stroke-width="34"/>'
            f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-family="PT Sans Narrow, PT Sans, sans-serif" '
            f'font-weight="700" font-size="44" fill="{INK}">{round(100 * part / total)}%</text>'
            f'<text x="{cx}" y="{cy + 30}" text-anchor="middle" font-family="PT Sans, sans-serif" font-size="14" '
            f'fill="{SUB}">{part} / {total}</text></svg>')


def inside_html(lang):
    m = META[lang]
    total, proven, _, _ = repo_stats()
    stages = ''.join(f'<div class="stage"><b>{n}</b><span class="t">{html.escape(t)}</span>'
                     f'<span class="d">{html.escape(d)}</span><span class="g">{html.escape(g)}</span></div>'
                     for n, t, d, g in roadmap_stages(lang))
    return (f'<section class="inside"><div class="kicker">{html.escape(m["inside_kicker"])}</div>'
            f'<h2 class="ct">{html.escape(m["inside"])}</h2><p class="intro">{html.escape(m["inside_text"])}</p>'
            f'<div class="figcap">{html.escape(m["route"])}</div><div class="stages">{stages}</div>'
            f'<div class="figcap">{html.escape(m["by_section"])}: <span class="sw p"></span>{m["proven"]}'
            f'<span class="sw h"></span>{m["hypothesis"]}</div>'
            f'<div class="duo"><div class="chart">{section_bars_svg(lang)}</div>'
            f'<div class="donut">{donut_svg(proven, total)}<div class="cap">{m["share"]}</div></div></div></section>')


def back_html(lang):
    m = META[lang]
    links = ''.join(f'<div><b>{html.escape(k)}</b><a href="{u}">{html.escape(u.split("://", 1)[1])}</a></div>'
                    for k, u in m['back_links'])
    return (f'<section class="back"><div class="kicker">{html.escape(m["back_kicker"])}</div>'
            f'<h2>{html.escape(m["back_title"])}</h2><p>{html.escape(m["back_text"])}</p>'
            f'<div class="links">{links}</div></section>')


def book_html(lang):
    files = chapter_files(lang)
    palette = {'ink': INK, 'sub': SUB, 'accent': OLIVE, 'accent2': RED, 'panel': PANEL, 'line': LINE,
               'font': 'PT Sans, Noto Sans, sans-serif'}
    css = CSS.replace('%FOOTER%', META[lang]['footer'].replace('"', "'"))
    body = cover_html(lang) + toc_html(lang, files) + inside_html(lang) + ''.join(chapter_html(f, lang, palette) for f in files) + back_html(lang)
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def check_pdf(pdf, titles, src_len=0):
    import longread
    bad = longread.pdf_gates(pdf)
    txt = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True).stdout
    flat = ' '.join(txt.split())
    for t in titles:
        # один раз название стоит в оглавлении, второй раз заголовком самой главы
        if flat.count(' '.join(t.split())) < 2:
            bad.append(f'в PDF нет главы «{t}» (название только в оглавлении или нигде)')
    # оглавление с заголовками без текста глав прошло бы проверку названий; сверяем объём текста
    got = len(re.sub(r'[\s#*_`|>\[\]:{}-]', '', txt))
    if src_len and got < 0.8 * src_len:
        bad.append(f'в PDF {got} знаков текста при {src_len} в главах: часть текста потеряна')
    return bad


def build(lang, out_dir):
    from weasyprint import HTML
    md, titles = book_md(lang)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / f'not-a-blogger-textbook-{lang}.pdf'
    HTML(string=book_html(lang), base_url=str(ROOT)).write_pdf(pdf)
    return pdf, [split_title(t)[1] for t in titles], plain_len(md)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Учебник learn/<lang>/ одним PDF A4')
    ap.add_argument('--lang', choices=['ru', 'en', 'all'], default='all')
    ap.add_argument('--out', default=str(ROOT / 'dist'))
    a = ap.parse_args(argv)
    try:
        import markdown  # noqa: F401
        import weasyprint  # noqa: F401
    except ImportError as e:
        print(f'нет зависимости: {e.name}. pip install -r tools/carousels/requirements.txt', file=sys.stderr)
        return 3
    missing = [c for c in ('pdfinfo', 'pdftotext') if not shutil.which(c)]
    if missing:
        print(f'нет {", ".join(missing)}: поставь poppler (brew install poppler, apt install poppler-utils)', file=sys.stderr)
        return 3
    code = 0
    for lang in (['ru', 'en'] if a.lang == 'all' else [a.lang]):
        pdf, titles, src_len = build(lang, Path(a.out))
        bad = check_pdf(pdf, titles, src_len)
        pages = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout
        n = re.search(r'Pages:\s+(\d+)', pages)
        print(f'{pdf} {n.group(1) if n else "?"} стр.' + (': ' + '; '.join(bad) if bad else ''))
        code = code or (2 if bad else 0)
    return code


if __name__ == '__main__':
    sys.exit(main())
