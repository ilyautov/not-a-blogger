"""Каждая утилита из tools/ отвечает на --help, включая библиотечные модули."""
import pytest

from conftest import load


@pytest.mark.parametrize('group,name', [('carousels', 'infographics'), ('covers', 'fonts'),
                                        ('captions', 'to_srt'), ('publish-prep', 'credits'), ('qa', 'loudness')])
def test_library_modules_answer_help(group, name, capsys):
    mod = load(group, name)
    with pytest.raises(SystemExit) as e:
        mod.main(['--help'])
    assert e.value.code == 0
    assert 'usage' in capsys.readouterr().out
