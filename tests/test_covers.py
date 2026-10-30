# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""tools/covers: текст поверх фона и векторные обложки."""
import importlib.util
import json

import pytest

from conftest import TOOLS, load

EX = TOOLS / 'covers' / 'examples'
needs_pil = pytest.mark.skipif(importlib.util.find_spec('PIL') is None, reason='нет Pillow')


@needs_pil
def test_overlay_sizes(tmp_path):
    from PIL import Image
    ov = load('covers', 'overlay')
    bg = ov.demo_bg(tmp_path / 'bg.png', (800, 800))
    spec = json.loads((EX / 'coffee-cover.json').read_text(encoding='utf-8'))
    im = ov.compose(Image.open(bg), spec)
    assert im.size == (1080, 1350)
    im2 = ov.compose(Image.open(bg), dict(spec, size=[1200, 630], pos='bottom', theme='paper'))
    assert im2.size == (1200, 630)
    # скрим сверху затемнил кадр у верхнего края сильнее, чем в середине
    assert sum(im.getpixel((540, 5))) < sum(Image.open(bg).convert('RGB').resize((1080, 1350)).getpixel((540, 5)))


def test_overlay_rejects_em_dash():
    ov = load('covers', 'overlay')
    assert ov.check_text({'h1': 'Кофе — это'})
    assert ov.check_text({'h1': 'Кофе в турке', 'sub': ['за три минуты']}) == []


def test_cover_svg_from_example():
    cv = load('covers', 'cover')
    data = json.loads((EX / 'coffee-covers.json').read_text(encoding='utf-8'))
    for c in data['covers']:
        assert cv.check_text(c) == []
        svg = cv.build_svg(c, data['theme'])
        assert svg.startswith('<svg') and 'Кофейные заметки' in svg
    # цвета пришли из темы, а не зашиты
    assert '#1d6b78' in cv.build_svg(data['covers'][0], 'paper')
    assert '#f0b23a' in cv.build_svg(data['covers'][0], 'dark')


def test_cover_gates():
    cv = load('covers', 'cover')
    assert cv.check_text({'file': 'x', 'icon': 'нет-такой'})
    assert cv.check_text({'file': 'x', 'badge': '1234'})
    assert cv.check_text({'file': 'x', 'hero': {'line1': 'Кофе — это'}})


def test_cover_badge_is_parameter():
    cv = load('covers', 'cover')
    c = cv.colors('paper')
    assert '>8x<' not in cv.icon_cup(c)
    assert '>8x<' in cv.icon_cup(c, '8x')


def test_cover_svg_escapes_markup_in_every_field():
    from xml.dom import minidom
    cv = load('covers', 'cover')
    c = {'file': 'x', 'eyebrow': 'R&D <dev>', 'icon': 'cup', 'badge': '<&',
         'hero': {'line1': 'A & B', 'line2': '<x>'}, 'sub': ['a & b'], 'footer': 'c <& d'}
    svg = cv.build_svg(c, 'paper')
    minidom.parseString(svg)                      # &AMP; из esc(...).upper() ломал XML
    assert 'R&amp;D &lt;DEV&gt;' in svg
    svg2 = cv.build_svg({'file': 'x', 'hero': {'number': '<7', 'tag': '& t'}}, 'dark')
    minidom.parseString(svg2)


def test_cover_name_collisions_refused(tmp_path, capsys):
    cv = load('covers', 'cover')
    data = json.loads((EX / 'coffee-covers.json').read_text(encoding='utf-8'))
    base = data['covers'][0]
    for names in (['a/b', 'a b'], ['Cover', 'cover'], [None, None]):
        covers = [{k: v for k, v in base.items() if k != 'file'} | ({'file': n} if n else {}) for n in names]
        p = tmp_path / 'in.json'
        p.write_text(json.dumps(dict(data, covers=covers)), encoding='utf-8')
        out = tmp_path / 'out'
        assert cv.main([str(p), '--out', str(out)]) == 1
        assert 'один файл' in capsys.readouterr().err
        assert not out.exists() or not any(out.iterdir())                # ничего не записано
    assert cv.name_collisions([dict(base, file='a'), dict(base, file='b')]) == []
