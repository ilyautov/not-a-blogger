#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Обложка «AI рисует фон, текст кладёт код».

Генератор картинок рисует только фон: в промпте прямо просим без текста, цифр и логотипов.
Буквы модель корёжит, поэтому весь текст (надзаголовок, заголовок, подзаголовок, подпись)
кладётся этим скриптом поверх. Под текстовые зоны добавляется скрим (плавное затемнение
или осветление), чтобы текст читался на любом арте.

Вход: картинка-фон и JSON со строками (или те же поля флагами). Арт кадрируется по центру
под нужный размер: 1080×1350 для карусели, 1200×630 для превью ссылки и т.п.

Запуск:
  python3 overlay.py art.png out.png --spec examples/coffee-cover.json
  python3 overlay.py art.png out.png --h1 "Кофе в турке" --h2 "за три минуты" --theme paper
  python3 overlay.py --demo-bg demo.png      # заглушка-градиент, если арта пока нет

Поля JSON: eyebrow, h1, h2 (акцентом), sub (список строк), footer, pos (top|bottom),
theme (dark|paper или путь к CSS), size ([w, h]).
Код возврата 1, если в тексте есть длинное тире: на обложке оно палит машинный текст.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fonts  # noqa: E402

THEMES_DIR = HERE / 'themes'


def parse_color(v):
    v = v.strip()
    if v.startswith('#'):
        h = v[1:]
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    m = re.match(r'rgba?\(([^)]+)\)', v)
    if m:
        parts = [p.strip() for p in m.group(1).split(',')]
        rgb = tuple(int(float(p)) for p in parts[:3])
        a = round(float(parts[3]) * 255) if len(parts) > 3 else 255
        return rgb + (a,)
    raise ValueError(f'не понимаю цвет {v}')


def load_theme(theme):
    """CSS-тема → словарь цветов из :root (--ink, --sub, --accent, --eyebrow, --scrim)."""
    p = Path(theme)
    if not p.suffix:
        p = THEMES_DIR / f'{theme}.css'
    css = p.read_text(encoding='utf-8')
    root = re.search(r':root\s*\{(.*?)\}', css, re.S)
    raw = dict(re.findall(r'--([\w-]+)\s*:\s*([^;]+);', root.group(1))) if root else {}
    out = {}
    for k, v in raw.items():
        try:
            out[k] = parse_color(v)
        except ValueError:
            out[k] = v.strip()
    return out


def crop_to(im, size):
    from PIL import Image
    W, H = size
    w, h = im.size
    if w / h > W / H:
        nw = round(h * W / H)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w * H / W)
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im.resize((W, H), Image.LANCZOS)


def scrim(im, where, color, frac=0.4, strength=210):
    """Градиент цвета color от края where (top|bottom) к середине."""
    from PIL import Image
    W, H = im.size
    lut = Image.new('L', (1, H), 0)
    px = lut.load()
    span = max(1, int(H * frac))
    for y in range(H):
        a = 0
        if where == 'top' and y < span:
            a = int(strength * (1 - y / span))
        if where == 'bottom' and y > H - span:
            a = int(strength * ((y - (H - span)) / span))
        px[0, y] = a
    layer = Image.new('RGBA', (W, H), color[:3] + (255,))
    layer.putalpha(lut.resize((W, H)))
    return Image.alpha_composite(im, layer)


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = f'{cur} {w}'.strip()
        if draw.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(d, x, y, text, fnt, fill, track):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + track
    return cx


def check_text(spec):
    text = ' '.join([spec.get('eyebrow', ''), spec.get('h1', ''), spec.get('h2', ''), spec.get('footer', '')]
                    + list(spec.get('sub', [])))
    issues = []
    if '—' in text:
        issues.append('длинное тире «—» в тексте обложки')
    if re.search(r'не\s+просто\s+[^,.!?]+,\s*а\b', text.lower()):
        issues.append('конструкция «не просто X, а Y»')
    return issues


def compose(bg, spec, font_path=None):
    """bg: PIL.Image. spec: dict полей. Возвращает RGB-картинку нужного размера."""
    from PIL import ImageDraw
    size = tuple(spec.get('size') or (1080, 1350))
    th = load_theme(spec.get('theme', 'dark'))
    ink, sub, acc = th['ink'], th['sub'], th['accent']
    eb = th.get('eyebrow', acc)
    im = crop_to(bg.convert('RGBA'), size)
    W, H = im.size
    s = min(W / 1080, H / 700)  # кегль от ширины, но горизонтальные превью не переполняем
    pos = spec.get('pos', 'top')
    d = ImageDraw.Draw(im)
    M = int(72 * s)
    f_eb, f_h, f_sub, f_ft = (fonts.load(int(28 * s), True, font_path), fonts.load(int(84 * s), True, font_path),
                              fonts.load(int(36 * s), False, font_path), fonts.load(int(32 * s), True, font_path))
    heights = {'eb': int(56 * s), 'h1': int(96 * s), 'h2': int(96 * s), 'sub': int(48 * s), 'gap': int(20 * s)}
    block = []
    if spec.get('eyebrow'):
        block.append(('eb', spec['eyebrow'].upper()))
    for key in ('h1', 'h2'):
        block += [(key, ln) for ln in wrap(d, spec.get(key, ''), f_h, W - 2 * M)]
    if spec.get('sub'):
        block.append(('gap', ''))
        for para in spec['sub']:
            block += [('sub', ln) for ln in wrap(d, para, f_sub, W - 2 * M)]
    total = sum(heights[k] for k, _ in block)
    foot_h = int(150 * s) if spec.get('footer') else int(72 * s)
    top = int(80 * s) if pos == 'top' else H - foot_h - total
    # скрим ровно под текстовый блок с запасом, а не фиксированной долей кадра
    cover = (top + total) / H if pos == 'top' else (H - top) / H
    im = scrim(im, pos, th['scrim'], frac=min(1.0, cover + 0.12))
    if spec.get('footer') and pos == 'top':
        im = scrim(im, 'bottom', th['scrim'], frac=0.2, strength=180)
    d = ImageDraw.Draw(im)
    y = top
    for kind, ln in block:
        if kind == 'eb':
            tracked(d, M, y, ln, f_eb, eb, int(6 * s))
        elif kind == 'sub':
            d.text((M, y), ln, font=f_sub, fill=sub)
        elif kind in ('h1', 'h2'):
            d.text((M, y), ln, font=f_h, fill=ink if kind == 'h1' else acc)
        y += heights[kind]
    if spec.get('footer'):
        d.text((M, H - int(100 * s)), spec['footer'], font=f_ft, fill=ink)
    return im.convert('RGB')


def demo_bg(path, size=(1080, 1350)):
    """Заглушка вместо AI-арта: мягкий диагональный градиент."""
    from PIL import Image
    v = Image.linear_gradient('L').resize(size)
    g = Image.blend(v, v.transpose(Image.ROTATE_90).resize(size), 0.5)
    im = Image.merge('RGB', [g.point(lambda v, a=a, b=b: int(a + b * v / 255)) for a, b in ((70, 90), (52, 60), (40, 30))])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description='Текст поверх AI-фона')
    ap.add_argument('src', nargs='?')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--spec', help='JSON с полями обложки')
    ap.add_argument('--eyebrow'); ap.add_argument('--h1'); ap.add_argument('--h2')
    ap.add_argument('--sub', help='строки через |')
    ap.add_argument('--footer')
    ap.add_argument('--pos', choices=['top', 'bottom'])
    ap.add_argument('--theme', help='dark | paper | путь к CSS')
    ap.add_argument('--size', help='ШxВ, например 1080x1350 или 1200x630')
    ap.add_argument('--font', help='путь к своему OFL-шрифту, если Inter/Noto Sans не установлены')
    ap.add_argument('--demo-bg', metavar='PNG', help='сделать заглушку фона и выйти')
    a = ap.parse_args(argv)
    if a.demo_bg:
        print(demo_bg(a.demo_bg))
        return 0
    if not (a.src and a.out):
        ap.error('нужны src и out')
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8')) if a.spec else {}
    for k in ('eyebrow', 'h1', 'h2', 'footer', 'pos', 'theme'):
        if getattr(a, k):
            spec[k] = getattr(a, k)
    if a.sub:
        spec['sub'] = [x for x in a.sub.split('|') if x]
    if a.size:
        spec['size'] = [int(x) for x in a.size.lower().split('x')]
    issues = check_text(spec)
    if issues:
        print('; '.join(issues), file=sys.stderr)
        return 1
    from PIL import Image
    im = compose(Image.open(a.src), spec, a.font)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)     # out/cover.png из README: папки out/ ещё нет
    im.save(a.out, quality=92)
    print(a.out, im.size)
    return 0


if __name__ == '__main__':
    sys.exit(main())
