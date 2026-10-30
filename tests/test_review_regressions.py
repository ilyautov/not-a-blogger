# SPDX-License-Identifier: MIT
# Copyright (c) 2026 not-a-blogger contributors. См. LICENSE в корне репозитория.
"""Регрессии по ревью: язык в pick_take, папка вывода overlay, коллизии имён карточек, гейт чисел data-reel."""
import importlib.util
import json
import shutil
import subprocess
import sys

import pytest

from conftest import ROOT, TOOLS, load

HAS_N2W = importlib.util.find_spec('num2words') is not None


# ---------- voice/pick_take: нормализация без ASR ----------
pt = load('voice', 'pick_take')


def test_pick_take_empty_normalization_is_failure():
    # раньше английский текст давал '' с обеих сторон и ratio 1.0 = ложный успех
    assert pt.text_ratio('...', '...') == 0.0
    assert pt.text_ratio('Проверка', '') == 0.0
    assert pt.text_ratio('', 'проверка') == 0.0
    assert pt.choose([{'take': 'a', 'ratio': pt.text_ratio('—', '—'), 'dur': 1, 'bad': 0, 'ok': 0,
                       'clipped_end': False, 'gaps_gt_025': []}])['ratio'] < 0.9


def test_pick_take_english_normalizes_non_empty():
    assert pt.letters('Hello, world!', 'en') == 'helloworld'
    assert pt.text_ratio('Hello world', 'hello, world', 'en') == 1.0
    assert pt.text_ratio('Hello world', 'yellow word', 'en') < 1.0
    assert pt.letters('Привет, ёж', 'ru') == 'приветеж'           # русское поведение: ё → е
    assert pt.letters('при́вет') == 'привет'                  # знак ударения не буква


@pytest.mark.skipif(not HAS_N2W, reason='нет num2words')
def test_pick_take_numbers_follow_lang():
    assert pt.letters('5', 'ru') == 'пять' and pt.letters('5', 'en') == 'five'
    assert pt.letters('1 000', 'ru') == pt.letters('1000', 'ru') != '1000'    # пробел-разделитель тысяч


# ---------- covers/overlay: папки out/ ещё нет ----------
@pytest.mark.skipif(importlib.util.find_spec('PIL') is None, reason='нет Pillow')
def test_overlay_cli_creates_missing_out_dir(tmp_path):
    ov = load('covers', 'overlay')
    bg = tmp_path / 'new' / 'bg.png'
    assert ov.main(['--demo-bg', str(bg)]) == 0 and bg.exists()
    out = tmp_path / 'out' / 'deep' / 'cover.png'
    assert ov.main([str(bg), str(out), '--spec', str(TOOLS / 'covers/examples/coffee-cover.json')]) == 0
    assert out.exists()


# ---------- carousels/cards: два имени → один PNG ----------
cards = load('carousels', 'cards')


def deck(*names):
    return [{'name': n, 'label': 'Кофе', 'num': f'{i} / {len(names)}', 'body': 'текст', 'last': i == len(names)}
            for i, n in enumerate(names, 1)]


def test_card_name_collision_detected(tmp_path):
    for names in (('result', 'result'), ('a/b', 'a b'), ('Card', 'card'), ('card-02', None)):
        hard = cards.hard(cards.check_cards(deck(*names)))
        assert any('один файл' in s for s in hard), names
    assert not cards.name_collisions(deck('a', 'b', None, ''))
    p = tmp_path / 'clash.json'
    p.write_text(json.dumps({'cards': deck('result', 'result')}), encoding='utf-8')
    assert cards.main([str(p), '--check-only']) == 1
    with pytest.raises(RuntimeError, match='один файл'):
        cards.render(deck('result', 'result'), tmp_path / 'o')
    assert not (tmp_path / 'o').exists()                          # остановились до рендера


# ---------- templates/data-reel/check_numbers ----------
def data_reel(tmp_path):
    d = tmp_path / 'data-reel'
    shutil.copytree(ROOT / 'templates/data-reel', d, ignore=shutil.ignore_patterns('real-numbers.json', 'voice', 'reel.json', '__pycache__'))
    t = tmp_path / 'Target'
    (t / 'Videos').mkdir(parents=True); (t / 'Archives').mkdir()
    (t / 'Videos/clip.mp4').write_bytes(b'\0' * 3_000_000)
    (t / 'Archives/backup.zip').write_bytes(b'\0' * 2_000_000)
    for cmd in (['measure_folders.py', t], ['reel_from_numbers.py']):
        subprocess.run([sys.executable, *map(str, cmd)], cwd=d, check=True, capture_output=True)
    return d


def gate(d):
    return subprocess.run([sys.executable, 'check_numbers.py'], cwd=d, capture_output=True, text=True)


def test_check_numbers_catches_raw_value_with_same_label(tmp_path):
    d = data_reel(tmp_path)
    assert gate(d).returncode == 0
    reel = json.loads((d / 'reel.json').read_text())
    reel['n']['old_pct'] += 37                                   # подпись fmt.old_pct не тронута, сетка врёт
    (d / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False))
    r = gate(d)
    assert r.returncode == 1 and 'n.old_pct' in r.stdout


def test_check_numbers_catches_bar_gb(tmp_path):
    d = data_reel(tmp_path)
    reel = json.loads((d / 'reel.json').read_text())
    reel['n']['bars'][0]['gb'] = 99                              # длина полосы, подпись прежняя
    (d / 'reel.json').write_text(json.dumps(reel, ensure_ascii=False))
    r = gate(d)
    assert r.returncode == 1 and 'bar' in r.stdout


def test_check_numbers_checks_spoken_numbers(tmp_path):
    d = data_reel(tmp_path)
    ch = json.loads((d / 'voice/chunks.json').read_text())
    ok = [dict(c) for c in ch]
    ok[4]['text'] = 'Это замер, не догадка. Скрипт лежит в описании.'  # перефразировка без чисел проходит
    (d / 'voice/chunks.json').write_text(json.dumps(ok, ensure_ascii=False))
    assert gate(d).returncode == 0
    ch[3]['text'] = 'Ровно 73 процента не менялось больше года.'     # голос врёт, субтитр верный
    (d / 'voice/chunks.json').write_text(json.dumps(ch, ensure_ascii=False))
    r = gate(d)
    assert r.returncode == 1 and 'chunks.json[3]' in r.stdout
    (d / 'voice/chunks.json').write_text(json.dumps(ch[:4], ensure_ascii=False))
    assert 'chunks for' in gate(d).stdout


@pytest.mark.skipif(not HAS_N2W, reason='нет num2words: числа в голосе цифрами')
def test_check_numbers_catches_extra_number_word(tmp_path):
    d = data_reel(tmp_path)
    ch = json.loads((d / 'voice/chunks.json').read_text())
    ch[4]['text'] = 'Это замер, а не догадка. Скрипт за двадцать секунд.'
    (d / 'voice/chunks.json').write_text(json.dumps(ch, ensure_ascii=False))
    r = gate(d)
    assert r.returncode == 1 and 'двадцать' in r.stdout
