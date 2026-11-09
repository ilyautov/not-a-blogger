"""predict_check: past-video loading, prompt files, verdict parsing; prompts stay in sync with prompts/script/."""
import re

from conftest import ROOT, load

pk = load('script', 'predict_check')


def test_prompts_match_prompt_files():
    for const, name in ((pk.PREDICT, 'prediction-test.md'), (pk.OVERLAP, 'overlap-check.md')):
        text = (ROOT / 'prompts' / 'script' / name).read_text(encoding='utf-8')
        block = re.search(r'```text\n(.*?)\n```', text, re.S).group(1)
        assert block == const, f'{name} drifted from tools/script/predict_check.py'


def test_load_past_csv_and_json(tmp_path):
    c = tmp_path / 'past.csv'
    c.write_text('id,title,logline,published\nv1,Passwords,An AI invents 50 passwords,yes\nv2,,,\n')
    rows = pk.load_past(c)
    assert len(rows) == 1 and rows[0]['id'] == 'v1'
    assert 'v1 | Passwords [published] | An AI invents 50 passwords' in pk.format_past(rows)
    j = tmp_path / 'past.json'
    j.write_text('{"videos": [{"logline": "A cat reviews code"}]}')
    assert pk.format_past(pk.load_past(j)).startswith('V1 |  | A cat reviews code')


def test_predict_and_overlap_write_prompts(tmp_path, capsys):
    out = tmp_path / 'research'
    assert pk.main(['predict', '--topic', 'a topic', '--out', str(out)]) == 0
    assert '"a topic"' in (out / 'predict.prompt.txt').read_text()
    cand = tmp_path / 'c.md'
    cand.write_text('1 | logline | frames | world | form | ending\n')
    assert pk.main(['overlap', '--topic', 'a topic', '--candidates', str(cand), '--out', str(out)]) == 1  # no predict.md
    (out / 'predict.md').write_text('P1 | obvious | a | list | moral\n')
    assert pk.main(['overlap', '--topic', 'a topic', '--candidates', str(cand), '--out', str(out)]) == 0
    assert 'P1 | obvious' in (out / 'overlap.prompt.txt').read_text()


def test_summary_parses_verdicts(tmp_path, capsys):
    (tmp_path / 'overlap.md').write_text('1 | CLEAR | -\n2 | OVERLAP | P1\n3 | shares | ending, v4\nnoise\n')
    assert pk.main(['summary', '--out', str(tmp_path)]) == 0
    assert 'keep: 1, 3' in capsys.readouterr().out
    assert pk.parse('2 | OVERLAP | P1') == [('2', 'OVERLAP', 'P1')]
