# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Инфографика-выноски в SVG, которые WeasyPrint рисует без потерь.

Правило: только rect, circle, path, line, polygon, text и линейные/радиальные градиенты.
Никаких filter, mask, foreignObject, CSS-переменных внутри SVG: WeasyPrint их пропускает
или рисует пустоту. Цвета приходят словарём palette (обычно из токенов темы).

Готовые схемы:
  flow(steps)              шаги слева направо со стрелками;
  bars(items)              горизонтальные столбики «подпись | число»;
  numbers(items)           крупные числа с подписями в карточках.
Помощники _wrap, _card, _t, _arrow годятся для своих схем.
"""
import argparse
import html
import math
import sys

DEFAULT_PALETTE = {
    'ink': '#22262b', 'sub': '#585d63', 'accent': '#1d6b78', 'accent2': '#7b4a7a',
    'panel': '#fbf8f2', 'line': '#e2dacb', 'font': 'Inter, Noto Sans, sans-serif',
}


def _pal(palette):
    p = dict(DEFAULT_PALETTE)
    p.update(palette or {})
    return p


def _wrap(vb, inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb}" width="100%">{inner}</svg>'


def _card(x, y, w, h, stroke, fill, sw=1.8, r=13):
    # «тень» вторым прямоугольником со сдвигом: filter drop-shadow WeasyPrint не рисует
    return (f'<rect x="{x + 5}" y="{y + 5}" width="{w}" height="{h}" rx="{r}" fill="{stroke}" opacity="0.12"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def _t(x, y, s, size=15, col='#222', w='700', anchor='middle', font='sans-serif'):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{w}" '
            f'fill="{col}" text-anchor="{anchor}">{html.escape(str(s))}</text>')


def _arrow(x1, y1, x2, y2, col='#222', sw=2.6):
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 9 * math.cos(a), y2 - 9 * math.sin(a)
    p1 = (hx - 8 * math.cos(a - 1.57), hy - 8 * math.sin(a - 1.57))
    p2 = (hx - 8 * math.cos(a + 1.57), hy - 8 * math.sin(a + 1.57))
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}"/>'
            f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')


def flow(steps, palette=None):
    """Шаги в ряд: номер в круге, подпись под ним, стрелки между."""
    p = _pal(palette)
    n = max(1, len(steps))
    W, H = 900, 200
    step_w = W / n
    e = []
    for i, s in enumerate(steps):
        cx = step_w * i + step_w / 2
        e.append(f'<circle cx="{cx:.0f}" cy="70" r="34" fill="{p["accent"]}"/>')
        e.append(_t(cx, 82, i + 1, 32, '#ffffff', font=p['font']))
        e.append(_t(cx, 145, s, 19, p['ink'], font=p['font']))
        if i < n - 1:
            e.append(_arrow(cx + 44, 70, cx + step_w - 46, 70, p['sub'], 2.4))
    return f'<div class="fig">{_wrap(f"{W} {H}", "".join(e))}</div>'


def bars(items, palette=None):
    """items: [(подпись, число)]. Длина столбика пропорциональна числу."""
    p = _pal(palette)
    items = [(str(a), float(b)) for a, b in items]
    vmax = max([v for _, v in items] + [1e-9])
    row, W = 54, 900
    H = row * len(items) + 20
    e = []
    for i, (label, v) in enumerate(items):
        y = 10 + i * row
        bw = 520 * v / vmax
        e.append(_t(250, y + 30, label, 18, p['ink'], w='600', anchor='end', font=p['font']))
        e.append(f'<rect x="270" y="{y + 8}" width="{bw:.1f}" height="30" rx="8" fill="{p["accent"]}"/>')
        e.append(_t(280 + bw, y + 30, f'{v:g}', 18, p['sub'], anchor='start', font=p['font']))
    return f'<div class="fig">{_wrap(f"{W} {H}", "".join(e))}</div>'


def numbers(items, palette=None):
    """items: [(число, подпись)] в карточках по ширине."""
    p = _pal(palette)
    n = max(1, len(items))
    W, H, gap = 900, 170, 20
    cw = (W - gap * (n - 1)) / n
    e = []
    for i, (val, cap) in enumerate(items):
        x = i * (cw + gap)
        e.append(_card(x, 10, cw - 6, 140, p['line'], p['panel']))
        e.append(_t(x + cw / 2, 80, val, 44, p['accent'], font=p['font']))
        e.append(_t(x + cw / 2, 120, cap, 16, p['sub'], w='500', font=p['font']))
    return f'<div class="fig">{_wrap(f"{W} {H}", "".join(e))}</div>'


def main(argv=None):
    ap = argparse.ArgumentParser(description='SVG-схемы для WeasyPrint (библиотечный модуль, его импортирует longread.py).')
    ap.add_argument('--demo', choices=['flow', 'bars', 'numbers'], help='напечатать пример схемы в SVG')
    a = ap.parse_args(argv)
    if a.demo == 'flow':
        print(flow(['Смолоть', 'Залить', 'Снять с огня']))
    elif a.demo == 'bars':
        print(bars([('Турка', 4), ('Френч-пресс', 7), ('Эспрессо', 1)]))
    elif a.demo == 'numbers':
        print(numbers([('7 г', 'кофе'), ('90 °C', 'вода'), ('3 мин', 'время')]))
    else:
        ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
