# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""tools/carousels: гейты карточек, рендер одной карточки 1080×1350, нарезка PDF, лонгрид."""
import importlib.util
import json
import shutil

import pytest

from conftest import TOOLS, load

cards = load('carousels', 'cards')
EX = TOOLS / 'carousels' / 'examples'
HAS_WEASY = importlib.util.find_spec('weasyprint') is not None
HAS_PIL = importlib.util.find_spec('PIL') is not None
HAS_POPPLER = bool(shutil.which('pdftoppm') and shutil.which('pdfinfo'))
needs_render = pytest.mark.skipif(not (HAS_WEASY and HAS_POPPLER), reason='нет weasyprint или poppler')


def pack(*bodies, nums=None):
    n = len(bodies)
    return [{'name': f'c{i}', 'label': 'Тест', 'num': (nums or [f'{i} / {n}' for i in range(1, n + 1)])[i - 1],
             'body': b, 'last': i == n} for i, b in enumerate(bodies, 1)]


def example():
    return json.loads((EX / 'coffee-turka.json').read_text(encoding='utf-8'))


def test_example_passes_gates():
    data = example()
    assert cards.hard(cards.check_cards(data['cards'], data['ban_words'])) == []


def test_gate_em_dash():
    assert any('тире' in s for s in cards.hard(cards.check_cards(pack('Кофе — это просто'))))
    assert any('тире' in s for s in cards.hard(cards.check_cards(pack('Кофе &mdash; это'))))


def test_gate_numbering():
    bad = cards.hard(cards.check_cards(pack('a', 'b', 'c', nums=['1 / 3', '3 / 3', '3 / 3'])))
    assert any('не совпадает' in s for s in bad)
    bad = cards.hard(cards.check_cards(pack('a', 'b', nums=['1 / 3', '2 / 3'])))
    assert len([s for s in bad if 'не совпадает' in s]) == 2
    assert cards.hard(cards.check_cards(pack('a', 'b', nums=['1/2', '2 / 2']))) == []


def test_gate_negative_parallelism():
    assert any('не просто' in s for s in cards.hard(cards.check_cards(pack('Турка не просто посуда, а ритуал'))))
    assert any('не только' in s for s in cards.hard(cards.check_cards(pack('Не только вкус, но и запах'))))
    assert cards.hard(cards.check_cards(pack('Турка простая посуда'))) == []


def test_gate_tofu_glyphs():
    assert any('квадрат' in s for s in cards.hard(cards.check_cards(pack('Шаг ⏵ дальше'))))
    assert any('private use' in s for s in cards.hard(cards.check_cards(pack('Иконка '))))


def test_gate_last_flag_and_ban_words():
    c = pack('a', 'b')
    c[-1]['last'] = False
    assert any('last' in s for s in cards.hard(cards.check_cards(c)))
    assert any('лайфхак' in s for s in cards.hard(cards.check_cards(pack('Мой лайфхак'), ['лайфхак'])))


def test_cli_check_only_fails_on_bad_text(tmp_path):
    p = tmp_path / 'bad.json'
    p.write_text(json.dumps({'cards': pack('Кофе — напиток')}), encoding='utf-8')
    assert cards.main([str(p), '--check-only']) == 1
    assert cards.main([str(EX / 'coffee-turka.json'), '--check-only']) == 0


def test_pdf_size_parser(monkeypatch):
    monkeypatch.setattr(cards, 'pdf_page_sizes', lambda pdf: [(810.0, 1012.5), (595.28, 841.89)])
    bad = cards.check_pdf_size('x.pdf')
    assert len(bad) == 1 and 'страница 2' in bad[0]


def test_card_paths_keep_dots_and_stay_inside_out_dir(tmp_path):
    base, png = cards.card_paths(tmp_path, 'card.v2', 1)
    assert png == tmp_path / 'card.v2.png' and base == tmp_path / 'card.v2'   # pdftoppm пишет <base>.png
    base, png = cards.card_paths(tmp_path, '../../escape', 2)
    assert png.parent == tmp_path and '..' not in png.name
    base, png = cards.card_paths(tmp_path, '/etc/passwd', 3)
    assert png.parent == tmp_path
    assert cards.card_paths(tmp_path, '', 4)[1] == tmp_path / 'card-04.png'
    assert cards.card_paths(tmp_path, None, 5)[1] == tmp_path / 'card-05.png'


@needs_render
@pytest.mark.skipif(not HAS_PIL, reason='нет Pillow')
def test_render_name_with_dot_and_slash(tmp_path):
    ex = example()['cards'][0]
    one = [dict(ex, name='card.v2', num='1 / 2', last=False), dict(ex, name='../out.side', num='2 / 2', last=True)]
    pngs = cards.render(one, tmp_path / 'o', theme='paper', footer='Тест')
    assert [p.name for p in pngs] == ['card.v2.png', 'out.side.png']
    assert all(p.exists() and p.parent == tmp_path / 'o' for p in pngs)


@needs_render
@pytest.mark.skipif(not HAS_PIL, reason='нет Pillow')
def test_render_one_card_png_1080x1350(tmp_path):
    from PIL import Image
    one = [dict(example()['cards'][0], num='1 / 1', last=True)]
    pngs = cards.render(one, tmp_path, theme='paper', footer='Тест')
    assert len(pngs) == 1
    # pdftoppm -r 96: WeasyPrint пишет 1 px как 0,75 pt; с -r 72 вышло бы 810×1013
    # (recipes/carousels/carousels-pdftoppm-96dpi.md)
    assert Image.open(pngs[0]).size == (1080, 1350)
    assert cards.check_pdf_size(tmp_path / 'pack.pdf') == []


@needs_render
@pytest.mark.skipif(not HAS_PIL, reason='нет Pillow')
def test_slice_pdf_to_carousel(tmp_path):
    from PIL import Image
    from weasyprint import HTML
    slicer = load('carousels', 'slice')
    pdf = tmp_path / 'a4.pdf'
    HTML(string='<style>@page{size:A4;background:#f3eee4}</style><h1>Раз</h1>'
                '<h1 style="break-before:page">Два</h1>').write_pdf(str(pdf))
    paths = slicer.slice_pdf(pdf, tmp_path / 'slides', dpi=60)
    assert len(paths) == 2
    im = Image.open(paths[0])
    assert im.size == (1080, 1350)
    assert im.getpixel((3, 3)) == im.getpixel((540, 1340))  # поля слились с фоном страницы


@needs_render
@pytest.mark.skipif(importlib.util.find_spec('markdown') is None, reason='нет markdown')
def test_longread_example_is_a4_without_dashes(tmp_path):
    lr = load('carousels', 'longread')
    assert lr.main([str(EX / 'coffee-turka.md'), '--out', str(tmp_path)]) == 0
    pdf = tmp_path / 'coffee-turka.pdf'
    assert lr.pdf_gates(pdf) == []


def test_longread_text_gate_catches_dash():
    lr = load('carousels', 'longread')
    assert lr.text_gates('---\ntitle: x\n---\nКофе — напиток')


@needs_render
@pytest.mark.skipif(not HAS_PIL, reason='нет Pillow')
def test_cards_images_resolve_from_input_folder(tmp_path, monkeypatch):
    """Проект вне репозитория: assets/photo.png ищется рядом с JSON, а не в tools/carousels/."""
    from PIL import Image
    proj = tmp_path / 'my-project'
    (proj / 'assets').mkdir(parents=True)
    Image.new('RGB', (40, 40), (200, 30, 30)).save(proj / 'assets/photo.png')
    one = [dict(example()['cards'][0], num='1 / 1', last=True, body='<img src="assets/photo.png" style="width:300px">')]
    (proj / 'pack.json').write_text(json.dumps({'cards': one}), encoding='utf-8')
    elsewhere = tmp_path / 'cwd'; elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert cards.main([str(proj / 'pack.json'), '--out', str(tmp_path / 'o')]) == 0
    import numpy as np
    px = np.asarray(Image.open(next((tmp_path / 'o').glob('*.png'))).convert('RGB')).reshape(-1, 3)
    assert ((px[:, 0] > 180) & (px[:, 1] < 80)).any()                   # красная картинка реально отрисована
    (proj / 'assets/photo.png').unlink()                                 # пропавшая картинка = ошибка, не пустое место
    assert cards.main([str(proj / 'pack.json'), '--out', str(tmp_path / 'o2')]) == 2
    with pytest.raises(RuntimeError, match='не загрузились'):
        cards.render(one, tmp_path / 'o3', base_dir=proj)
