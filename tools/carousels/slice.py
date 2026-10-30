#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Нарезка PDF в карусель 1080×1350 (4:5): один источник, два формата.

Каждая страница PDF растеризуется (pdftoppm), вписывается в холст 1080×1350 и ставится
по центру. Поля холста красятся в цвет фона страницы, поэтому сливаются с ней. Цвет фона
берётся из угла страницы (пиксель (6, 6)) или задаётся --bg.

Первым слайдом можно поставить отдельную обложку 4:5 (--cover): картинка кадрируется
по центру под 1080×1350. Так обложка PDF формата A4 не превращается в мелкую марку
посреди пустого холста.

Запуск:
  python3 slice.py out/longread/coffee.pdf --out out/slides
  python3 slice.py doc.pdf --out out/slides --cover art.png --skip-first --bg "#f3eee4"

Нужны: Pillow, pdftoppm (poppler).
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CW, CH = 1080, 1350


def parse_color(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def fit_page(im, bg=None, size=(CW, CH)):
    """Вписать страницу в холст size, поля цвета bg (по умолчанию цвет угла страницы)."""
    from PIL import Image
    cw, ch = size
    im = im.convert('RGB')
    if bg is None:
        bg = im.getpixel((min(6, im.width - 1), min(6, im.height - 1)))
    w, h = im.size
    scale = min(cw / w, ch / h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    canvas = Image.new('RGB', (cw, ch), bg)
    canvas.paste(im.resize((nw, nh), Image.LANCZOS), ((cw - nw) // 2, (ch - nh) // 2))
    return canvas


def crop_cover(im, size=(CW, CH)):
    """Кадрировать картинку по центру под пропорцию size и привести к size."""
    from PIL import Image
    cw, ch = size
    im = im.convert('RGB')
    w, h = im.size
    target = cw / ch
    if w / h > target:
        nw = round(h * target)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w / target)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im.resize((cw, ch), Image.LANCZOS)


def slice_pdf(pdf, out_dir, dpi=200, bg=None, cover=None, skip_first=False):
    from PIL import Image
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(pdf), str(Path(tmp) / 'p')], check=True)
        # pdftoppm добивает номер нулями по числу страниц (p-1 или p-01), сортируем по числу
        pages = sorted(Path(tmp).glob('p-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
        if skip_first:
            pages = pages[1:]
        slides = []
        if cover:
            slides.append(crop_cover(Image.open(cover)))
        slides += [fit_page(Image.open(p), bg) for p in pages]
    paths = []
    for i, im in enumerate(slides, 1):
        p = out / f'slide-{i:02d}.png'
        im.save(p)
        paths.append(p)
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description='PDF → карусель 1080×1350')
    ap.add_argument('pdf')
    ap.add_argument('--out', default='out/slides')
    ap.add_argument('--dpi', type=int, default=200)
    ap.add_argument('--bg', default=None, help='цвет полей, например "#f3eee4"; по умолчанию угол страницы')
    ap.add_argument('--cover', default=None, help='картинка-обложка для слайда 1 (кадрируется в 4:5)')
    ap.add_argument('--skip-first', action='store_true', help='не брать первую страницу PDF (если её заменяет --cover)')
    a = ap.parse_args(argv)
    if not shutil.which('pdftoppm'):
        print('нет pdftoppm: поставь poppler', file=sys.stderr)
        return 3
    paths = slice_pdf(a.pdf, a.out, a.dpi, parse_color(a.bg) if a.bg else None, a.cover, a.skip_first)
    print(f'слайдов: {len(paths)} → {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
