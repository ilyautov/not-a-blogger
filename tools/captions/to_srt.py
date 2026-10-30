#!/usr/bin/env python3
"""Тайминги слов → субтитры SRT и VTT: по N слов на титр, с потолком длительности.

Что делает: читает JSON с таймингами слов, режет слова на титры и пишет SRT (00:00:01,250) и/или
WebVTT (00:00:01.250). Новый титр начинается, когда набралось --words слов (3), когда титр стал бы
длиннее --max-duration секунд (3,0), когда пауза между словами больше --max-gap (0,8 с), когда
сменилась реплика или предыдущее слово кончилось на . ! ? или …  Слово длиннее потолка стоит
одно. Конец титра не заходит на начало следующего.

Вход (любой из форматов):
  • voice-track.json стартера: {"words": [{"text": "...", "start": 0.4, "end": 0.7, "line": 0}, ...]};
  • слова ASR (faster-whisper, qa/asr-track.json): {"words": [["слово", 0.4, 0.7], ...]} или просто список троек;
  • timeline.json шаблона skit: {"lines": [{"words": [["слово", 0.4, 0.7], ...]}, ...]};
  • JSON Whisper: {"segments": [{"text": "...", "start": .., "end": .., "words": [{"word": ..}]}]};
  • простой список сегментов [{"text": "две фразы", "start": 0.0, "end": 1.2}, ...]: сегмент из
    нескольких слов делится на слова пропорционально числу букв.
Выход: без --srt/--vtt SRT печатается в stdout; с ними файлы пишутся, а в stdout идёт JSON-сводка
(титров, слов, пути). Код возврата: 0; 1, если слов не нашлось (пустые файлы всё равно пишутся).

Пример:
  python3 tools/captions/to_srt.py starter/voice-track.json --srt output/final.srt --vtt output/final.vtt
  python3 tools/captions/to_srt.py qa/asr-track.json --words 2 --max-duration 2.0 > final.srt
"""
import argparse
import json
import re
import sys
from pathlib import Path

SENTENCE_END = re.compile(r'[.!?…]["»”)]*$')


def _word(text, start, end, line=None):
    return {'text': str(text).strip(), 'start': float(start), 'end': float(end), 'line': line}


def _split_segment(text, start, end, line=None):
    """Сегмент из нескольких слов → слова, время делится пропорционально длине слов."""
    parts = str(text).split()
    if len(parts) <= 1:
        return [_word(text, start, end, line)] if parts else []
    total = sum(len(p) for p in parts)
    out, t = [], float(start)
    for p in parts:
        d = (float(end) - float(start)) * len(p) / total
        out.append(_word(p, t, t + d, line))
        t += d
    out[-1]['end'] = float(end)
    return out


def _from_items(items, line=None):
    words = []
    for it in items:
        if isinstance(it, (list, tuple)):
            words.append(_word(it[0], it[1], it[2], line))
        elif isinstance(it, dict):
            text = it.get('text', it.get('word', ''))
            ln = it.get('line', line)
            if it.get('words'):                      # сегмент со своими словами (Whisper)
                words += _from_items(it['words'], ln)
            else:
                words += _split_segment(text, it['start'], it['end'], ln)
        else:
            raise ValueError(f'не понимаю элемент: {it!r}')
    return words


def load_words(data):
    """Любой из поддерживаемых форматов → список слов {text, start, end, line}, по времени."""
    if isinstance(data, dict):
        if 'words' in data:
            words = _from_items(data['words'])
        elif 'lines' in data:
            words = []
            for i, ln in enumerate(data['lines']):
                words += _from_items(ln['words'], i) if ln.get('words') else _from_items([ln], i)
        elif 'segments' in data:
            words = []
            for i, seg in enumerate(data['segments']):
                words += _from_items([{**seg, 'line': i}])
        else:
            raise ValueError('ожидал ключ "words", "lines" или "segments"')
    elif isinstance(data, list):
        words = _from_items(data)
    else:
        raise ValueError('ожидал JSON-список или объект')
    words = [w for w in words if w['text']]
    for w in words:
        if w['end'] < w['start']:
            raise ValueError(f'конец раньше начала у слова {w["text"]!r}')
    return sorted(words, key=lambda w: w['start'])


def group_words(words, n=3, max_duration=3.0, max_gap=0.8):
    """Слова → титры {start, end, text}."""
    if n < 1:
        raise ValueError('--words должно быть ≥ 1')
    caps, cur = [], []
    for w in words:
        if cur:
            prev = cur[-1]
            if (len(cur) >= n or w['end'] - cur[0]['start'] > max_duration
                    or w['start'] - prev['end'] > max_gap or w['line'] != prev['line']
                    or SENTENCE_END.search(prev['text'])):
                caps.append(cur)
                cur = []
        cur.append(w)
    if cur:
        caps.append(cur)
    out = [{'start': c[0]['start'], 'end': c[-1]['end'], 'text': ' '.join(w['text'] for w in c)} for c in caps]
    for a, b in zip(out, out[1:]):
        a['end'] = min(a['end'], b['start'])
    return out


def fmt_time(t, sep=','):
    """Секунды → 'HH:MM:SS,mmm' (SRT) или 'HH:MM:SS.mmm' (VTT, sep='.')."""
    ms = max(0, int(round(t * 1000)))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}'


def to_srt(caps):
    return ''.join(f'{i}\n{fmt_time(c["start"])} --> {fmt_time(c["end"])}\n{c["text"]}\n\n'
                   for i, c in enumerate(caps, 1))


def to_vtt(caps):
    return 'WEBVTT\n\n' + ''.join(f'{fmt_time(c["start"], ".")} --> {fmt_time(c["end"], ".")}\n{c["text"]}\n\n'
                                  for c in caps)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Тайминги слов (JSON) → субтитры SRT и VTT по N слов на титр.')
    ap.add_argument('input', help='JSON с таймингами слов или сегментов')
    ap.add_argument('--words', type=int, default=3, help='слов на титр, максимум (3)')
    ap.add_argument('--max-duration', type=float, default=3.0, help='потолок длительности титра, с (3,0)')
    ap.add_argument('--max-gap', type=float, default=0.8, help='пауза между словами, после которой новый титр, с (0,8)')
    ap.add_argument('--srt', help='куда записать SRT')
    ap.add_argument('--vtt', help='куда записать WebVTT')
    a = ap.parse_args(argv)
    words = load_words(json.loads(Path(a.input).read_text(encoding='utf-8')))
    caps = group_words(words, a.words, a.max_duration, a.max_gap)
    if not words:
        print(f'{a.input}: слов не нашлось', file=sys.stderr)
    if not a.srt and not a.vtt:
        sys.stdout.write(to_srt(caps))
        return 0 if words else 1
    for path, text in ((a.srt, to_srt(caps)), (a.vtt, to_vtt(caps))):
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(text, encoding='utf-8')
    print(json.dumps({'file': Path(a.input).name, 'words': len(words), 'captions': len(caps),
                      'srt': a.srt, 'vtt': a.vtt, 'pass': bool(words)}, ensure_ascii=False))
    return 0 if words else 1


if __name__ == '__main__':
    sys.exit(main())
