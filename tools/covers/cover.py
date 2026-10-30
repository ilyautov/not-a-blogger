#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Векторная обложка без AI: иконка-метафора + одно число или фраза + 2–3 строки.

Обложка = функция от пяти полей: надзаголовок, иконка, герой (число с подписью или
фраза в две строки), подзаголовок, подпись. Пишется SVG, PNG делает cairosvg (без браузера).
Цвета приходят из CSS-темы (themes/*.css, переменные в :root), шрифт по имени: первый
установленный из Inter и Noto Sans, иначе системный sans-serif (--font-family меняет).

Грабля, из-за которой бейджи вынесены в параметр: иконка с зашитым текстом (например
«8x» на бейдже) переезжает в следующий пост и тащит туда чужое число. Поэтому текст на
иконке задаётся только полем "badge" конкретной обложки.

Вход JSON:
  {"theme": "paper", "size": [1080, 1350], "covers": [
     {"file": "coffee-01", "eyebrow": "КОФЕ ДОМА", "icon": "cup", "badge": "3",
      "hero": {"number": "3 мин", "tag": "на слабом огне"},      # или {"line1": "...", "line2": "..."}
      "sub": ["строка 1", "строка 2"], "footer": "Кофейные заметки"}]}

Запуск:
  python3 cover.py examples/coffee-covers.json --out out/covers
  python3 cover.py --list-icons

Без cairosvg пишется только SVG (его открывает любой браузер).
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fonts  # noqa: E402
from overlay import load_theme  # noqa: E402  общий разбор CSS-темы


def resolve_family(families=fonts.FAMILIES):
    """Одно имя семейства для SVG. cairosvg не разбирает список через запятую: с ним
    берёт шрифт по умолчанию и теряет жирность. Поэтому выбираем первое установленное."""
    for fam in families:
        if fonts.find_font((fam,)):
            return fam
    return 'sans-serif'


FONT = resolve_family()


def esc(s):
    return html.escape(str(s), quote=False)


def hexc(c):
    """Цвет темы → '#rrggbb' и прозрачность."""
    if isinstance(c, tuple):
        return '#%02x%02x%02x' % c[:3], c[3] / 255 if len(c) > 3 else 1.0
    return str(c), 1.0


def _badge(c, text, x=140, y=-112):
    if not text:
        return ''
    size = 58 if len(text) <= 2 else 40
    return (f'<g transform="translate({x},{y})"><circle r="46" fill="{c["b"]}"/>'
            f'<text x="0" y="{size * 0.35:.0f}" text-anchor="middle" font-family="{FONT}" font-size="{size}" '
            f'font-weight="bold" fill="#ffffff">{esc(text)}</text></g>')


def _check_badge(c, x=140, y=-112):
    return (f'<g transform="translate({x},{y})"><circle r="46" fill="{c["b"]}"/>'
            '<path d="M -20 2 L -5 17 L 22 -14" fill="none" stroke="#ffffff" stroke-width="11" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')


# Каждая иконка рисуется в системе координат с центром (0,0) в радиусе ~150 px.
# badge=None: без бейджа; badge="✓": галочка; иначе текст бейджа (1–3 символа).
def icon_cup(c, badge=None):
    """Чашка с паром."""
    return (f'<path d="M -110 -30 H 90 V 50 a 70 70 0 0 1 -70 70 H -40 a 70 70 0 0 1 -70 -70 Z" fill="{c["a"]}" '
            f'fill-opacity="0.10" stroke="{c["a"]}" stroke-width="12" stroke-linejoin="round"/>'
            f'<path d="M 90 -6 h 22 a 34 34 0 0 1 0 68 h -26" fill="none" stroke="{c["a"]}" stroke-width="12"/>'
            f'<line x1="-140" y1="140" x2="120" y2="140" stroke="{c["a"]}" stroke-width="12" stroke-linecap="round"/>'
            + ''.join(f'<path d="M {x} -60 q -18 -26 0 -52 q 18 -26 0 -52" fill="none" stroke="{c["b"]}" '
                      f'stroke-width="10" stroke-linecap="round"/>' for x in (-60, -10, 40))
            + _mark(c, badge))


def icon_clock(c, badge=None):
    """Часы: время, срок, длительность."""
    return (f'<circle r="120" fill="{c["a"]}" fill-opacity="0.08" stroke="{c["a"]}" stroke-width="12"/>'
            f'<line x1="0" y1="0" x2="0" y2="-74" stroke="{c["a"]}" stroke-width="12" stroke-linecap="round"/>'
            f'<line x1="0" y1="0" x2="56" y2="30" stroke="{c["b"]}" stroke-width="12" stroke-linecap="round"/>'
            f'<circle r="12" fill="{c["ink"]}"/>' + _mark(c, badge))


def icon_eye(c, badge=None):
    """Глаз: видимость, прозрачность."""
    return (f'<path d="M -128 0 Q 0 -84 128 0 Q 0 84 -128 0 Z" fill="none" stroke="{c["a"]}" stroke-width="12" '
            f'stroke-linejoin="round"/><circle r="44" fill="{c["a"]}"/><circle r="20" fill="{c["ink"]}"/>'
            f'<circle cx="15" cy="-13" r="10" fill="#ffffff"/>' + _mark(c, badge))


def icon_bill(c, badge=None):
    """Чек с рваным низом: счёт, расходы."""
    teeth = ''.join(' l -23.5 18 l -23.5 -18' for _ in range(4))
    return (f'<path d="M -94 -104 Q -94 -122 -76 -122 H 76 Q 94 -122 94 -104 V 96{teeth} Z" fill="{c["a"]}" '
            f'fill-opacity="0.07" stroke="{c["a"]}" stroke-width="11" stroke-linejoin="round"/>'
            f'<g stroke="{c["a"]}" stroke-width="11" stroke-linecap="round"><line x1="-56" y1="-78" x2="56" y2="-78"/>'
            '<line x1="-56" y1="-40" x2="30" y2="-40"/><line x1="-56" y1="-2" x2="46" y2="-2"/></g>' + _mark(c, badge))


def icon_shield(c, badge=None):
    """Щит с замком: защита, права доступа."""
    return (f'<path d="M 0 -142 L 122 -102 V 18 Q 122 108 0 150 Q -122 108 -122 18 V -102 Z" fill="{c["a"]}" '
            f'fill-opacity="0.07" stroke="{c["a"]}" stroke-width="12" stroke-linejoin="round"/>'
            f'<rect x="-36" y="-10" width="72" height="62" rx="12" fill="{c["a"]}"/>'
            f'<path d="M -24 -10 V -32 a 24 24 0 0 1 48 0 V -10" fill="none" stroke="{c["a"]}" stroke-width="12"/>'
            f'<circle cx="0" cy="16" r="9" fill="{c["ink"]}"/>' + _mark(c, badge, 122, -104))


def icon_chart(c, badge=None):
    """Падающие столбики и стрелка вниз: метрика снижается."""
    bars = ''.join(f'<rect x="{x}" y="{y}" width="58" height="{120 - y}" rx="11" fill="{c["a"]}" fill-opacity="0.12" '
                   f'stroke="{c["a"]}" stroke-width="8"/>' for x, y in ((-132, -30), (-50, 26), (32, 62)))
    return (bars + f'<line x1="-150" y1="132" x2="150" y2="132" stroke="{c["a"]}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M -126 -78 L -16 -2 L 46 -28 L 150 52" fill="none" stroke="{c["b"]}" stroke-width="12" '
            f'stroke-linecap="round" stroke-linejoin="round"/><path d="M 150 52 L 112 50 M 150 52 L 148 14" fill="none" '
            f'stroke="{c["b"]}" stroke-width="12" stroke-linecap="round"/>' + _mark(c, badge))


def icon_search(c, badge=None):
    """Лупа: поиск, проверка."""
    return (f'<circle cx="-22" cy="-22" r="100" fill="{c["a"]}" fill-opacity="0.07" stroke="{c["a"]}" stroke-width="12"/>'
            f'<line x1="54" y1="54" x2="134" y2="134" stroke="{c["a"]}" stroke-width="22" stroke-linecap="round"/>'
            + _mark(c, badge))


def icon_route(c, badge=None):
    """Развилка: основной и запасной путь."""
    return (f'<circle cx="-120" cy="0" r="36" fill="{c["a"]}"/>'
            f'<path d="M -84 0 H -4" stroke="{c["a"]}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M -4 0 C 64 0 78 -78 150 -78" fill="none" stroke="{c["a"]}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M -4 0 C 64 0 78 78 150 78" fill="none" stroke="{c["b"]}" stroke-width="12" stroke-linecap="round" '
            f'stroke-dasharray="22 16"/><circle cx="150" cy="-78" r="34" fill="{c["a"]}" fill-opacity="0.14" '
            f'stroke="{c["a"]}" stroke-width="11"/><circle cx="150" cy="78" r="34" fill="{c["b"]}" fill-opacity="0.14" '
            f'stroke="{c["b"]}" stroke-width="11"/>' + _mark(c, badge, 40, -130))


def icon_power(c, badge=None):
    """Кнопка выключения: остановка, отказ."""
    return (f'<path d="M -78 -44 A 100 100 0 1 0 78 -44" fill="none" stroke="{c["a"]}" stroke-width="16" stroke-linecap="round"/>'
            f'<line x1="0" y1="-112" x2="0" y2="8" stroke="{c["a"]}" stroke-width="16" stroke-linecap="round"/>'
            + _mark(c, badge, 120, -112))


def icon_folder(c, badge=None):
    """Папка с листами: инструкция, набор, архив."""
    return (f'<path d="M -126 -72 H -34 l 22 28 H 126 a 16 16 0 0 1 16 16 V 78 a 16 16 0 0 1 -16 16 H -126 '
            f'a 16 16 0 0 1 -16 -16 V -56 a 16 16 0 0 1 16 -16 Z" fill="{c["a"]}" fill-opacity="0.08" '
            f'stroke="{c["a"]}" stroke-width="12" stroke-linejoin="round"/>'
            f'<g stroke="{c["a"]}" stroke-width="11" stroke-linecap="round"><line x1="-74" y1="6" x2="74" y2="6"/>'
            '<line x1="-74" y1="44" x2="40" y2="44"/></g>' + _mark(c, badge, 126, -98))


def _mark(c, badge, x=140, y=-112):
    if not badge:
        return ''
    return _check_badge(c, x, y) if badge == '✓' else _badge(c, badge, x, y)


ICONS = {k[5:]: v for k, v in globals().items() if k.startswith('icon_')}


def hero_number(c, num, tag, y=820):
    size = 300 if len(num) <= 3 else 220 if len(num) <= 5 else 160
    return (f'<text x="80" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="bold" letter-spacing="-6" '
            f'fill="{c["a"]}">{esc(num)}</text><text x="92" y="{y + 72}" font-family="{FONT}" font-size="34" '
            f'font-weight="bold" fill="{c["sub"]}">{esc(tag)}</text>')


def hero_phrase(c, l1, l2, y=720):
    return (f'<text x="86" y="{y}" font-family="{FONT}" font-size="92" font-weight="bold" letter-spacing="-2" '
            f'fill="{c["ink"]}">{esc(l1)}</text><text x="86" y="{y + 100}" font-family="{FONT}" font-size="92" '
            f'font-weight="bold" letter-spacing="-2" fill="{c["a"]}">{esc(l2)}</text>')


def colors(theme):
    th = load_theme(theme)
    c = {}
    for key, var, default in (('a', 'accent', '#1d6b78'), ('b', 'accent2', '#7b4a7a'), ('ink', 'ink', '#22262b'),
                              ('sub', 'sub', '#585d63'), ('bg', 'bg', '#f3eee4'), ('panel', 'panel', '#fbf8f2'),
                              ('line', 'line', '#cccccc'), ('eyebrow', 'eyebrow', None)):
        v = th.get(var)
        c[key], c[key + '_op'] = hexc(v) if v is not None else (default or c['a'], 1.0)
    return c


def check_text(cv):
    hero = cv.get('hero', {})
    text = ' '.join(str(x) for x in [cv.get('eyebrow', ''), cv.get('footer', ''), cv.get('badge') or '',
                                     *hero.values(), *cv.get('sub', [])])
    issues = []
    if '—' in text:
        issues.append(f'[{cv.get("file")}] длинное тире «—»')
    if cv.get('icon') and cv['icon'] not in ICONS:
        issues.append(f'[{cv.get("file")}] нет иконки «{cv["icon"]}», есть: {", ".join(sorted(ICONS))}')
    if cv.get('badge') and len(str(cv['badge'])) > 3:
        issues.append(f'[{cv.get("file")}] бейдж длиннее 3 символов не влезет в круг')
    return issues


def build_svg(cv, theme='paper', size=(1080, 1350)):
    c = colors(theme)
    W, H = size
    hero = cv.get('hero', {})
    if 'number' in hero:
        hero_svg = hero_number(c, hero['number'], hero.get('tag', ''))
    else:
        hero_svg = hero_phrase(c, hero.get('line1', ''), hero.get('line2', ''))
    sub = ''.join(f'<text x="88" y="{1000 + i * 52}" font-family="{FONT}" font-size="38" font-weight="400" '
                  f'fill="{c["sub"]}">{esc(ln)}</text>' for i, ln in enumerate(cv.get('sub', [])[:3]))
    icon = ICONS[cv['icon']](c, cv.get('badge')) if cv.get('icon') else ''
    footer = ''
    if cv.get('footer'):
        footer = (f'<line x1="88" y1="1170" x2="992" y2="1170" stroke="{c["line"]}" stroke-opacity="{c["line_op"]:.2f}" '
                  f'stroke-width="2"/><text x="88" y="1240" font-family="{FONT}" font-size="36" font-weight="bold" '
                  f'fill="{c["ink"]}">{esc(cv["footer"])}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 1080 1350" '
            f'preserveAspectRatio="xMidYMid slice">'
            f'<rect width="1080" height="1350" fill="{c["bg"]}"/>'
            f'<circle cx="540" cy="360" r="190" fill="{c["panel"]}" stroke="{c["a"]}" stroke-opacity="0.2" stroke-width="2"/>'
            f'<g transform="translate(540,360)">{icon}</g>'
            f'<text x="88" y="150" font-family="{FONT}" font-size="30" font-weight="bold" letter-spacing="7" '
            f'fill="{c["eyebrow"]}">{esc(str(cv.get("eyebrow", "")).upper())}</text>'
            f'{hero_svg}{sub}{footer}</svg>')


def cover_name(cv):
    """Имя файла обложки без расширения: всё, кроме букв, цифр, точки и дефиса, — в дефис."""
    return re.sub(r'[^\w.-]+', '-', cv.get('file', 'cover'))


def name_collisions(covers):
    """Обложки, чьи имена после чистки дают один файл (a/b и a b, Cover и cover на регистронезависимой ФС
    macOS/Windows, две без "file"). Без проверки вторая молча перезаписала бы первую."""
    seen, issues = {}, []
    for i, cv in enumerate(covers, 1):
        name = cover_name(cv)
        k = name.lower()
        if k in seen:
            j, first = seen[k]
            issues.append(f'обложки {j} («{first}») и {i} («{cv.get("file", "")}») дают один файл {name}.svg/.png, '
                          'переименуй одну')
        else:
            seen[k] = (i, cv.get('file', ''))
    return issues


def main(argv=None):
    ap = argparse.ArgumentParser(description='SVG/PNG-обложки из JSON')
    ap.add_argument('input', nargs='?')
    ap.add_argument('--out', default='out/covers')
    ap.add_argument('--theme', default=None, help='тема из themes/ или путь к CSS (по умолчанию из JSON)')
    ap.add_argument('--font-family', default=None, help='имя установленного OFL-шрифта (по умолчанию Inter, Noto Sans)')
    ap.add_argument('--list-icons', action='store_true')
    a = ap.parse_args(argv)
    global FONT
    if a.font_family:
        FONT = a.font_family
    if a.list_icons:
        for k, f in sorted(ICONS.items()):
            print(f'{k:8s} {f.__doc__}')
        return 0
    if not a.input:
        ap.error('нужен JSON')
    data = json.loads(Path(a.input).read_text(encoding='utf-8'))
    theme = a.theme or data.get('theme', 'paper')
    size = tuple(data.get('size', (1080, 1350)))
    issues = [s for cv in data['covers'] for s in check_text(cv)] + name_collisions(data['covers'])
    for s in issues:
        print(s, file=sys.stderr)
    if issues:
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        import cairosvg
    except (ImportError, OSError):
        cairosvg = None
        print('cairosvg не установлен: пишу только SVG', file=sys.stderr)
    for cv in data['covers']:
        name = cover_name(cv)
        svg = build_svg(cv, theme, size)
        (out / f'{name}.svg').write_text(svg, encoding='utf-8')
        if cairosvg:
            cairosvg.svg2png(bytestring=svg.encode('utf-8'), write_to=str(out / f'{name}.png'),
                             output_width=size[0], output_height=size[1])
        print(out / f'{name}.png' if cairosvg else out / f'{name}.svg')
    return 0


if __name__ == '__main__':
    sys.exit(main())
