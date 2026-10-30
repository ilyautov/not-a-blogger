"""to_srt: группировка слов, формат времени SRT/VTT, форматы входа, пустой вход."""
import json

import pytest

from conftest import load

ts = load('captions', 'to_srt')


def _words(n, step=0.4, dur=0.3, line=None):
    return [{'text': f'w{i}', 'start': round(i * step, 3), 'end': round(i * step + dur, 3), 'line': line}
            for i in range(n)]


def test_groups_by_n_words():
    caps = ts.group_words(_words(7), n=3)
    assert [c['text'] for c in caps] == ['w0 w1 w2', 'w3 w4 w5', 'w6']
    assert caps[0]['start'] == 0.0 and caps[0]['end'] == pytest.approx(1.1)


def test_max_duration_gap_line_and_sentence_break():
    long = ts.group_words(_words(4, step=1.0, dur=0.9), n=10, max_duration=2.0, max_gap=5)
    assert [c['text'] for c in long] == ['w0 w1', 'w2 w3']
    gap = _words(3)
    gap[2]['start'], gap[2]['end'] = 3.0, 3.3
    assert [c['text'] for c in ts.group_words(gap, n=5)] == ['w0 w1', 'w2']
    lines = _words(2, line=0) + [{'text': 'x', 'start': 0.8, 'end': 1.0, 'line': 1}]
    assert len(ts.group_words(lines, n=5)) == 2
    sent = _words(3)
    sent[0]['text'] = 'Готово.'
    assert [c['text'] for c in ts.group_words(sent, n=5)] == ['Готово.', 'w1 w2']


def test_caption_end_never_overlaps_next():
    w = [{'text': 'a', 'start': 0.0, 'end': 1.0, 'line': None}, {'text': 'b', 'start': 0.9, 'end': 1.5, 'line': None}]
    caps = ts.group_words(w, n=1)
    assert caps[0]['end'] == 0.9


def test_timestamp_formats():
    assert ts.fmt_time(1.25) == '00:00:01,250'
    assert ts.fmt_time(1.25, '.') == '00:00:01.250'
    assert ts.fmt_time(3723.0016) == '01:02:03,002'
    caps = [{'start': 1.25, 'end': 2.0, 'text': 'привет мир'}]
    assert ts.to_srt(caps) == '1\n00:00:01,250 --> 00:00:02,000\nпривет мир\n\n'
    assert ts.to_vtt(caps) == 'WEBVTT\n\n00:00:01.250 --> 00:00:02.000\nпривет мир\n\n'


def test_input_formats():
    starter = {'words': [{'line': 0, 'text': 'Раз', 'say': 'раз', 'start': 0.4, 'end': 0.7}], 'cues': []}
    assert ts.load_words(starter)[0]['text'] == 'Раз'
    asr = {'words': [['раз', 0.4, 0.7], ['два', 0.8, 1.0]]}
    assert [w['text'] for w in ts.load_words(asr)] == ['раз', 'два']
    skit = {'lines': [{'who': 'a', 'words': [['раз', 0.1, 0.3]]}, {'who': 'b', 'words': [['два', 0.4, 0.6]]}]}
    assert [w['line'] for w in ts.load_words(skit)] == [0, 1]
    whisper = {'segments': [{'text': ' раз два', 'start': 0, 'end': 1,
                             'words': [{'word': ' раз', 'start': 0, 'end': 0.4}, {'word': ' два', 'start': 0.5, 'end': 1}]}]}
    assert [w['text'] for w in ts.load_words(whisper)] == ['раз', 'два']
    seg = ts.load_words([{'text': 'аа бббб', 'start': 0.0, 'end': 1.2}])
    assert [w['text'] for w in seg] == ['аа', 'бббб']
    assert seg[0]['end'] == pytest.approx(0.4) and seg[1]['end'] == 1.2


def test_empty_input(tmp_path, capsys):
    assert ts.group_words([]) == []
    assert ts.to_srt([]) == '' and ts.to_vtt([]) == 'WEBVTT\n\n'
    p = tmp_path / 'empty.json'
    p.write_text('[]')
    assert ts.main([str(p)]) == 1
    assert ts.main([str(p), '--srt', str(tmp_path / 'e.srt')]) == 1
    assert (tmp_path / 'e.srt').read_text() == ''


def test_main_writes_both(tmp_path, capsys):
    p = tmp_path / 'w.json'
    p.write_text(json.dumps({'words': _words(5)}))
    assert ts.main([str(p), '--words', '2', '--srt', str(tmp_path / 'a.srt'), '--vtt', str(tmp_path / 'a.vtt')]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep['captions'] == 3 and rep['pass'] is True
    assert (tmp_path / 'a.srt').read_text().startswith('1\n00:00:00,000 --> 00:00:00,700\nw0 w1\n')
    assert (tmp_path / 'a.vtt').read_text().startswith('WEBVTT\n\n00:00:00.000 --> 00:00:00.700\nw0 w1\n')
