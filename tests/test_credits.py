"""credits: нормализация лицензий, блок атрибуции, провал на неизвестной и NC с --commercial."""
import json

from conftest import load

cr = load('publish-prep', 'credits')

GOOD = [
    {'file': 'music/track.mp3', 'title': 'Track', 'author': 'Artist', 'source_url': 'https://example.org/track',
     'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/'},
    {'file': 'img/photo.jpg', 'author': 'Someone', 'license': 'Public domain'},
    {'file': 'img/icon.svg', 'license': 'CC0'},
]


def test_normalize_vocabulary():
    n = cr.normalize
    assert n('CC BY 4.0')['label'] == 'CC BY 4.0'
    assert n('cc-by-sa-3.0')['id'] == 'CC BY-SA'
    assert n('CC BY-NC-SA 4.0')['nc'] is True
    assert n('CC BY-ND 4.0')['nd'] is True
    assert n('Public Domain')['id'] == 'PD' and n('PD')['id'] == 'PD'
    assert n('Pixabay License')['id'] == 'PIXABAY' and n('MIT')['id'] == 'MIT'
    assert n('', 'https://creativecommons.org/licenses/by-nc/4.0/')['id'] == 'CC BY-NC'
    assert n('', 'https://creativecommons.org/publicdomain/zero/1.0/')['id'] == 'CC0'
    assert n('All rights reserved') is None and n('') is None


def test_cc_url_needs_exact_host_and_path(tmp_path):
    n = cr.normalize
    assert n('', 'https://notcreativecommons.org/publicdomain/zero/1.0/') is None
    assert n('', 'https://creativecommons.org.evil.example/licenses/by/4.0/') is None
    assert n('', 'https://example.com/?u=https://creativecommons.org/publicdomain/zero/1.0/') is None
    assert n('', 'https://example.com/creativecommons.org/licenses/by/4.0/') is None
    assert n('', 'ftp://creativecommons.org/licenses/by/4.0/') is None
    assert n('', 'https://creativecommons.org/about/licenses/by/4.0/') is None
    assert n('', 'https://www.creativecommons.org/licenses/by-sa/4.0/deed.ru')['id'] == 'CC BY-SA'
    assert n('', 'http://creativecommons.org/licenses/by/4.0/legalcode')['id'] == 'CC BY'
    assert n('', 'https://creativecommons.org/publicdomain/mark/1.0/')['id'] == 'PD'
    bad = [{'file': 'x.mp3', 'license_url': 'https://notcreativecommons.org/publicdomain/zero/1.0/'}]
    assert _run(tmp_path, bad, '--commercial') == 1

def _run(tmp_path, assets, *args):
    p = tmp_path / 'assets.json'
    p.write_text(json.dumps(assets))
    return cr.main([str(p), *args])


def test_all_open_passes_and_prints_block(tmp_path, capsys):
    assert _run(tmp_path, GOOD) == 0
    out = capsys.readouterr().out
    assert out.startswith('Credits:\nTrack — Artist, CC BY 4.0, https://example.org/track')
    assert 'photo — Someone, Public Domain' in out


def test_markdown_format(tmp_path, capsys):
    assert _run(tmp_path, {'assets': GOOD}, '--format', 'md') == 0
    out = capsys.readouterr().out
    assert out.startswith('## Credits\n- [Track](https://example.org/track) — Artist, '
                          '[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)')


def test_missing_and_unknown_license_fail(tmp_path, capsys):
    bad = GOOD + [{'file': 'img/nolicense.jpg'}, {'file': 'img/stock.jpg', 'license': 'Editorial use only'}]
    assert _run(tmp_path, bad) == 1
    err = capsys.readouterr().err
    assert 'img/nolicense.jpg: нет лицензии' in err
    assert 'img/stock.jpg' in err and 'не из списка' in err
    assert 'track.mp3' not in err


def test_cc_by_without_author_fails(tmp_path, capsys):
    assert _run(tmp_path, [{'file': 'a.mp3', 'license': 'CC BY-SA 4.0'}]) == 1
    assert 'author' in capsys.readouterr().err


def test_nc_warns_but_fails_with_commercial(tmp_path, capsys):
    nc = [{'file': 'm.mp3', 'author': 'X', 'license': 'CC BY-NC 4.0'}]
    assert _run(tmp_path, nc) == 0
    assert 'ПРЕДУПРЕЖДЕНИЕ' in capsys.readouterr().err
    assert _run(tmp_path, nc, '--commercial') == 1
    assert 'ОШИБКА' in capsys.readouterr().err


def test_json_report(tmp_path, capsys):
    assert _run(tmp_path, GOOD + [{'file': 'x.png'}], '--json') == 1
    rep = json.loads(capsys.readouterr().out)
    assert rep['pass'] is False and rep['assets'] == 4 and len(rep['errors']) == 1
    assert rep['credits'].startswith('Credits:')
