#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Пак карточек 1080×1350 (4:5) для каруселей Telegram, Threads, Instagram, LinkedIn.

Конвейер: JSON с карточками → гейты текста → HTML + тема CSS → WeasyPrint PDF →
проверка размера страницы через pdfinfo → pdftoppm PNG по одной карточке.

Контент отделён от вида: карточки пишутся в JSON (body = HTML из классов компонентов,
список в README.md), вид задаёт один CSS-файл темы с переменными в :root.

Гейты (жёсткие, до рендера):
  * 0 длинных тире «—» (и &mdash;);
  * нумерация «N / M» совпадает с позицией карточки и их числом;
  * нет конструкций «не просто X, а Y» и «не только X, но и Y»;
  * нет глифов, которые в шрифте превращаются в квадраты (⏵ ⏴ ⏶ ⏷, U+FFFD, private use);
  * последняя карточка помечена "last": true;
  * слова из "ban_words" входного файла не встречаются.
Мягкие (с пометкой SOFT, рендер не останавливают): двусмысленный номер «N / N» на одной карточке.
После рендера pdfinfo проверяет, что страница 810×1012.5 pt (= 1080×1350 px). Если нет,
CSS сломался и страница уехала в A4 (грабля WeasyPrint, см. README).

Запуск:
  python3 cards.py examples/coffee-turka.json --theme paper --out out/coffee
  python3 cards.py examples/coffee-turka.json --check-only

Относительные пути картинок в body (<img src="assets/photo.png">) считаются от папки входного JSON.

Коды возврата: 0 успех; 1 жёсткие гейты; 2 размер страницы не тот, коллизия имён или картинка не загрузилась;
3 нет зависимостей.
"""
import argparse
import html
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
THEMES_DIR = HERE / 'themes'

W_PX, H_PX = 1080, 1350
# WeasyPrint: 1px = 0.75pt. pdftoppm -r 96 переводит обратно в 1080×1350.
W_PT, H_PT = W_PX * 0.75, H_PX * 0.75

BASE_CSS = """
@page { size: 1080px 1350px; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:1080px; font-family: var(--font-sans); }
.card { position:relative; width:1080px; height:1350px; padding:96px 88px; overflow:hidden;
  color:var(--ink); background:var(--bg); break-after:page; page-break-after:always; }
.card:last-child { break-after:auto; page-break-after:auto; }
.inner { position:relative; height:100%; display:flex; flex-direction:column; justify-content:space-between; }
.toprow { display:flex; align-items:flex-start; justify-content:space-between; }
.label { font-size:30px; font-weight:700; letter-spacing:7px; color:var(--eyebrow); text-transform:uppercase; }
.num { font-size:28px; font-weight:700; letter-spacing:2px; color:var(--sub); }
.giant { font-size:340px; font-weight:800; line-height:0.92; letter-spacing:-6px; color:var(--accent); }
.gianttag { font-size:38px; font-weight:700; letter-spacing:2px; color:var(--sub); margin-top:6px; }
.h1 { font-family: var(--font-head); font-size:96px; font-weight:800; line-height:1.02; letter-spacing:-2px; margin-top:30px; }
.phrase { font-family: var(--font-head); font-size:150px; font-weight:800; line-height:0.98; letter-spacing:-3px; }
.lead { font-size:46px; font-weight:400; line-height:1.28; color:var(--sub); margin-top:38px; max-width:880px; }
.accent { color:var(--accent); }
.accent2 { color:var(--accent2); }
.bignum-grid { display:flex; flex-wrap:wrap; gap:28px; margin-top:36px; }
.bignum { flex:1 1 40%; padding:34px 36px; border-radius:26px;
  background:var(--panel-bg); border:1px solid var(--panel-br); box-shadow:var(--panel-shadow); }
.bignum .n { font-size:92px; font-weight:800; line-height:1; letter-spacing:-2px; color:var(--accent); }
.bignum .cap { font-size:30px; font-weight:500; color:var(--sub); margin-top:12px; }
.check { margin-top:34px; }
.check .item { font-size:42px; font-weight:500; line-height:1.32; padding-left:54px; position:relative; margin-bottom:22px; }
.check .item:before { content:'✓'; position:absolute; left:0; top:0; color:var(--accent); font-weight:800; }
.chip { display:inline-block; margin-top:42px; padding:18px 28px; border-radius:999px;
  font-size:30px; font-weight:600; background:var(--chip-bg); border:1px solid var(--chip-br); color:var(--accent); }
.note { font-size:30px; color:var(--sub); margin-top:26px; }
.panel { background:var(--panel-bg); border:1px solid var(--panel-br); border-radius:28px;
  box-shadow:var(--panel-shadow); padding:36px 40px; margin-top:32px; }
.bad { border-left:8px solid var(--bad); }
.good { border-left:8px solid var(--good); }
.foot { padding-top:44px; border-top:1px solid var(--footline);
  display:flex; align-items:center; justify-content:space-between; }
.who { display:flex; align-items:center; gap:22px; font-size:34px; font-weight:700; }
.logo { width:64px; height:64px; border-radius:50%; object-fit:cover; }
.swipe { font-size:30px; font-weight:600; color:var(--accent); }
"""

UNSAFE_GLYPHS = ['⏵', '⏴', '⏶', '⏷', '�']
HARD_BANS = [
    (r'не\s+просто\s+[^,.!?]+,\s*а\b', '«не просто X, а Y»'),
    (r'не\s+только\b[^.!?]*\bно\s+и\b', '«не только X, но и Y»'),
]
EM_DASH = re.compile(r'—|&mdash;|&#8212;|&#x2014;', re.I)
TAG = re.compile(r'<[^>]+>')


def plain(s):
    """HTML → текст для проверок (теги убираем, сущности раскрываем)."""
    return html.unescape(TAG.sub(' ', s or ''))


def check_cards(cards, ban_words=()):
    """Гейты до рендера. Возвращает список строк; строки без префикса SOFT жёсткие."""
    issues = []
    total = len(cards)
    if not total:
        return ['HARD: пустой пак']
    for i, c in enumerate(cards, 1):
        name = c.get('name') or f'card-{i:02d}'
        raw = f"{c.get('label', '')} {c.get('body', '')}"
        text = plain(raw)
        low = text.lower()
        if EM_DASH.search(raw):
            issues.append(f'HARD [{name}]: длинное тире «—» запрещено, замени на точку, запятую или двоеточие')
        for pat, title in HARD_BANS:
            if re.search(pat, low):
                issues.append(f'HARD [{name}]: конструкция {title}')
        for g in UNSAFE_GLYPHS:
            if g in text:
                issues.append(f'HARD [{name}]: глиф U+{ord(g):04X} рендерится квадратом, используй → ✓ или цифры')
        if any(0xE000 <= ord(ch) <= 0xF8FF for ch in text):
            issues.append(f'HARD [{name}]: символ из private use area, в шрифте будет квадрат')
        for w in ban_words:
            if re.search(r'(?<!\w)' + re.escape(w.lower()) + r'(?!\w)', low):
                issues.append(f'HARD [{name}]: запрещённое слово «{w}»')
        num = (c.get('num') or '').replace(' ', '')
        if num:
            m = re.fullmatch(r'(\d+)/(\d+)', num)
            if not m:
                issues.append(f'HARD [{name}]: номер «{c.get("num")}» не в формате «N / M»')
            else:
                a, b = int(m.group(1)), int(m.group(2))
                if (a, b) != (i, total):
                    issues.append(f'HARD [{name}]: номер «{c.get("num")}» не совпадает, ожидалось {i} / {total}')
                if a == b and total == 1:
                    issues.append(f'SOFT [{name}]: номер «{c.get("num")}» двусмысленный, похож на дату или счёт')
    if not cards[-1].get('last'):
        issues.append('HARD: последняя карточка не помечена "last": true')
    for i, c in enumerate(cards[:-1], 1):
        if c.get('last'):
            issues.append(f'HARD [{c.get("name") or i}]: "last": true стоит не на последней карточке')
    issues += name_collisions(cards)
    return issues


def hard(issues):
    return [s for s in issues if not s.startswith('SOFT')]


def load_theme(theme):
    p = Path(theme)
    if not p.suffix:
        p = THEMES_DIR / f'{theme}.css'
    if not p.exists():
        avail = ', '.join(sorted(x.stem for x in THEMES_DIR.glob('*.css')))
        raise FileNotFoundError(f'нет темы {p}; есть: {avail}')
    return p.read_text(encoding='utf-8')


def card_html(c, footer, logo_uri, swipe):
    label = html.escape(c.get('label', ''))
    num = html.escape(c.get('num', ''))
    who = ''
    if logo_uri:
        who += f'<img class="logo" src="{logo_uri}">'
    if footer:
        who += f'<span>{html.escape(footer)}</span>'
    hint = '' if c.get('last') or not swipe else f'<span class="swipe">{html.escape(swipe)}</span>'
    foot = f'<div class="foot"><div class="who">{who}</div>{hint}</div>' if (who or hint) else ''
    return ('<section class="card"><div class="blob"></div><div class="blob2"></div><div class="inner">'
            f'<div class="toprow"><div class="label">{label}</div><div class="num">{num}</div></div>'
            f'<div class="content">{c.get("body", "")}</div>{foot}</div></section>')


def build_html(cards, theme_css, footer='', logo=None, swipe='листай →'):
    logo_uri = Path(logo).resolve().as_uri() if logo else ''
    # Склейка без .replace() на части строки: иначе @page может уехать (грабля в README).
    css = BASE_CSS + '\n' + theme_css
    body = ''.join(card_html(c, footer, logo_uri, swipe) for c in cards)
    return f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def pdf_page_sizes(pdf):
    """Размеры всех страниц PDF в pt через pdfinfo."""
    out = subprocess.run(['pdfinfo', '-f', '1', '-l', '9999', str(pdf)], capture_output=True, text=True, check=True).stdout
    sizes = [(float(a), float(b)) for a, b in re.findall(r'Page\s+\d+\s+size:\s+([\d.]+)\s+x\s+([\d.]+)', out)]
    if not sizes:
        m = re.search(r'Page size:\s+([\d.]+)\s+x\s+([\d.]+)', out)
        if m:
            sizes = [(float(m.group(1)), float(m.group(2)))]
    return sizes


def check_pdf_size(pdf, w_pt=W_PT, h_pt=H_PT, tol=1.0):
    bad = []
    for i, (w, h) in enumerate(pdf_page_sizes(pdf), 1):
        if abs(w - w_pt) > tol or abs(h - h_pt) > tol:
            bad.append(f'страница {i}: {w:g}×{h:g} pt, ожидалось {w_pt:g}×{h_pt:g}')
    return bad


def card_paths(out_dir, name, i):
    """(база для pdftoppm -singlefile, итоговый PNG). Имя чистится как в covers/cover.py: только
    буквы, цифры, точка, дефис; пустое или из одних точек → card-NN. Точка в имени не суффикс:
    pdftoppm пишет <база>.png, а with_suffix('.png') для card.v2 дал бы card.png."""
    safe = re.sub(r'[^\w.-]+', '-', str(name or '')).strip('.-') or f'card-{i:02d}'
    base = Path(out_dir) / safe
    return base, Path(str(base) + '.png')


def name_collisions(cards, out_dir='.'):
    """Карточки, чьи имена после чистки дают один и тот же PNG (result и result, a/b и a b, Card и card на
    регистронезависимой ФС macOS/Windows). Без проверки вторая молча перезаписала бы первую."""
    seen, issues = {}, []
    for i, c in enumerate(cards, 1):
        png = card_paths(out_dir, c.get('name'), i)[1]
        k = png.name.lower()
        if k in seen:
            j, first = seen[k]
            issues.append(f'HARD [{c.get("name")}]: карточки {j} («{first}») и {i} дают один файл {png.name}, '
                          'переименуй одну')
        else:
            seen[k] = (i, c.get('name'))
    return issues


class _FailedLoads(logging.Handler):
    """Собирает ошибки WeasyPrint «Failed to load image/stylesheet …»: сам он их только логирует и рисует дальше."""
    def __init__(self):
        super().__init__(logging.WARNING)
        self.failed = []

    def emit(self, record):
        msg = record.getMessage()
        if 'Failed to load' in msg:
            self.failed.append(msg)


def render(cards, out_dir, theme='paper', footer='', logo=None, swipe='листай →', keep_pdf=True, base_dir=None):
    """Рендер пака. Возвращает список PNG. Бросает RuntimeError при коллизии имён, неверном размере страницы или
    картинке/стилях, которые не загрузились. Относительные пути в body (assets/photo.png) считаются от base_dir:
    папки входного JSON (main передаёт её сам), по умолчанию от текущей папки, но не от папки утилиты."""
    clash = name_collisions(cards, out_dir)
    if clash:
        raise RuntimeError('; '.join(clash))
    from weasyprint import HTML  # импорт здесь: гейты работают и без WeasyPrint
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    doc = build_html(cards, load_theme(theme), footer, logo, swipe)
    pdf = out / 'pack.pdf'
    base = Path(base_dir or '.').resolve()
    rec, log = _FailedLoads(), logging.getLogger('weasyprint')
    log.addHandler(rec)
    try:
        HTML(string=doc, base_url=str(base) + os.sep).write_pdf(str(pdf))
    finally:
        log.removeHandler(rec)
    if rec.failed:
        raise RuntimeError(f'ресурсы не загрузились (пути считаются от {base.name or base}): ' + '; '.join(rec.failed))
    bad = check_pdf_size(pdf)
    if bad:
        raise RuntimeError('pdfinfo: ' + '; '.join(bad))
    pngs = []
    for i, c in enumerate(cards, 1):
        base, png = card_paths(out, c.get('name'), i)
        subprocess.run(['pdftoppm', '-png', '-r', '96', '-f', str(i), '-l', str(i), '-singlefile', str(pdf), str(base)],
                       check=True)
        pngs.append(png)
    if not keep_pdf:
        pdf.unlink()
    return pngs


def load_input(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, list):
        data = {'cards': data}
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description='Пак карточек 1080×1350 из JSON')
    ap.add_argument('input', help='JSON: {"footer", "swipe", "ban_words", "cards": [{name,label,num,body,last}]}')
    ap.add_argument('--theme', default=None, help='имя темы из themes/ или путь к CSS (по умолчанию из JSON или paper)')
    ap.add_argument('--out', default='out/cards', help='папка для PNG и pack.pdf')
    ap.add_argument('--logo', default=None, help='свой PNG для футера (необязательно)')
    ap.add_argument('--check-only', action='store_true', help='только гейты, без рендера')
    a = ap.parse_args(argv)

    data = load_input(a.input)
    cards = data.get('cards', [])
    issues = check_cards(cards, data.get('ban_words', []))
    for s in issues:
        print(s)
    if hard(issues):
        print(f'гейты: {len(hard(issues))} жёстких, рендер остановлен', file=sys.stderr)
        return 1
    print(f'гейты: ок ({len(cards)} карточек)')
    if a.check_only:
        return 0
    for tool in ('pdftoppm', 'pdfinfo'):
        if not shutil.which(tool):
            print(f'нет {tool}: поставь poppler (brew install poppler / apt install poppler-utils)', file=sys.stderr)
            return 3
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        print('нет weasyprint: pip install -r requirements.txt', file=sys.stderr)
        return 3
    try:
        pngs = render(cards, a.out, a.theme or data.get('theme', 'paper'), data.get('footer', ''),
                      a.logo, data.get('swipe', 'листай →'), base_dir=Path(a.input).resolve().parent)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2
    for p in pngs:
        print(p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
