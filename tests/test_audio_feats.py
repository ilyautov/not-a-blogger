"""audio_feats: pure helpers without librosa, and a synthetic click track (no music download)."""
import importlib.util
import json

import numpy as np
import pytest

from conftest import load

af = load('audio', 'audio_feats')
needs_librosa = pytest.mark.skipif(importlib.util.find_spec('librosa') is None, reason='no librosa')


def test_cut_before_word_snaps_and_refuses_far_beats():
    grid = [0.0, 0.5, 1.0, 1.5]
    assert af.cut_before_word(grid, 1.2) == (1.0, True)
    assert af.cut_before_word(grid, 1.51) == (1.5, True)          # within tol after the beat
    assert af.cut_before_word([0.0], 2.0) == (2.0, False)         # nearest beat further than max_lead


def test_to_video_shifts_by_offset():
    doc = {'track': 't', 'bpm': 120, 'beats': [9.5, 10.0, 10.5, 30.0], 'downbeats': [10.0],
           'sections': [{'name': 's0', 'start': 0, 'end': 40, 'energy': 'mid'}],
           'env': {'rms': [0.1] * 4000}, 'onsets': {'kick': [[10.0, 1.0], [25.0, 0.5]]},
           'quality': {'beat_confidence': 2.0, 'downbeat_margin': 0.3}}
    v = af.to_video(doc, offset=10.0, duration=5.0)
    assert v['beats'] == [-0.5, 0.0, 0.5] and v['onsets']['kick'] == [[0.0, 1.0]]
    assert v['sections'][0]['start'] == 0 and v['sections'][0]['end'] == 5.0


def test_phrase_starts_formats():
    whisper = {'segments': [{'start': 1.0, 'text': ' Hello there', 'words': [{'word': ' Hello', 'start': 1.1}]}]}
    assert af.phrase_starts(whisper) == [(0, 'Hello', 1.1)]
    assert af.phrase_starts([['one', 0.4, 0.6]]) == [(0, 'one', 0.4)]
    assert af.phrase_starts([{'text': 'two words', 'start': 2.0}]) == [(0, 'two', 2.0)]


def click_track(bpm=120, seconds=12, sr=44100):
    """Low thumps on every beat: 60 Hz decaying sine, 80 ms long."""
    x = np.zeros(int(seconds * sr), np.float32)
    n = int(0.08 * sr)
    t = np.arange(n) / sr
    thump = (np.sin(2 * np.pi * 60 * t) * np.exp(-t * 40)).astype(np.float32) * 0.8
    for b in np.arange(0, seconds - 0.1, 60 / bpm):
        i = int(b * sr)
        x[i:i + n] += thump[:len(x) - i]
    return x


@needs_librosa
def test_click_track_gives_tempo_and_kicks():
    d = af.analyze_signal(click_track())
    assert abs(d['bpm'] - 120) < 3 or abs(d['bpm'] - 240) < 6 or abs(d['bpm'] - 60) < 2
    gaps = np.diff(d['beats'])
    med = float(np.median(gaps))
    assert len(gaps) > 8 and min(abs(med - 0.5), abs(med - 0.25), abs(med - 1.0)) < 0.03
    kicks = [t for t, _ in d['onsets']['kick']]
    assert len(kicks) >= 20                                 # 24 thumps in 12 s
    assert all(min(abs(k - b) for b in np.arange(0, 12, 0.5)) < 0.03 for k in kicks)
    v = af.to_video(d, 2.0, 6.0)
    cuts = af.propose_cuts(v, [(0, 'word', 1.2)])
    assert cuts['applied'] is False and cuts['cuts'][0]['lead'] <= 0.6


def test_help_and_bad_track(tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        af.main(['--help'])
    assert e.value.code == 0
    assert af.main(['show', str(tmp_path / 'missing.mp3')]) == 1


def test_cuts_cli_from_feats_json(tmp_path):
    feats = tmp_path / 'track.feats.json'
    feats.write_text(json.dumps({'track': 't', 'duration': 20, 'bpm': 120, 'beats': [i * 0.5 for i in range(40)],
                                 'downbeats': [i * 2.0 for i in range(10)], 'sections': [], 'env': {'rms': [0] * 2000},
                                 'onsets': {'kick': [], 'snare': [], 'hat': []},
                                 'quality': {'beat_confidence': 2.0, 'downbeat_margin': 0.3}}))
    words = tmp_path / 'w.json'
    words.write_text(json.dumps([['first', 1.3, 1.5], ['second', 3.9, 4.2]]))
    out = tmp_path / 'cuts.json'
    assert af.main(['cuts', str(feats), '--offset', '1', '--words', str(words), '--out', str(out)]) == 0
    rows = json.loads(out.read_text())['cuts']
    assert [r['cut'] for r in rows] == [1.0, 3.5]
