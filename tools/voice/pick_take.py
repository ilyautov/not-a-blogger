#!/usr/bin/env python3
"""Выбор лучшего дубля TTS из нескольких кандидатов одной реплики.

Что делает для каждого дубля:
  • ASR faster-whisper с пословными таймкодами (язык --lang, по умолчанию ru); совпадение с текстом реплики
    по буквам любого алфавита (числа переводятся в слова через num2words, если он знает язык), ratio 0..1;
    пустой текст после нормализации или пустой ASR = ratio 0, а не «совпало»;
  • растяжка: длительность каждого слова против медианы того же слова по всем дублям;
    больше 1,3× = «тянет» (слово протянуто, звучит неестественно);
  • паузы между словами длиннее 0,25 с и обрыв конца (последние 30 мс громче пик − 30 дБ);
  • ударение (необязательно, --stress): в границах слова ищутся слоговые ядра (пики огибающей),
    вес ядра = длительность выше пик − 6 дБ × громкость × (1 + отклонение высоты тона от медианы).
    Ударным считается ядро с наибольшим весом: ok / X<номер> / ?<ядер>/<гласных>.
    Это ЭВРИСТИКА, а не слух: она помогает отсеять явные промахи, но не заменяет прослушивание.
    Только для русских слов (словарь и гласные кириллические).
  • темп: слоги (гласные текста реплики) на секунду речи от первого до последнего слова ASR;
    выше --max-rate (6,3 слога/с) = скомкано. Гласные: кириллица для ru, кириллица и латиница aeiouy
    для остальных языков; в других алфавитах темп = 0, то есть не меряется;
  • высота (необязательно, --max-f0 250): медиана F0 дубля; выше = фальцет.
Выбор: сначала дубли с ratio ≥ --min-ratio (0,9); из них отсеиваются дубли быстрее --max-rate и
выше --max-f0 (если отсеялись все, остаются все прошедшие ratio); среди оставшихся меньше «тянет» и X,
больше ok, без обрыва, меньше длинных пауз, выше ratio (до сотых), и последним — ближе к медиане
длительности всех дублей реплики. Не «короче»: выбор самого короткого дубля на каждой реплике
ускорил два ролика на 15 % против эталонов (аудит озвучки, docs/QA-THRESHOLDS.md).
0,9 — нижняя граница, не пропуск: реальные дефекты давали 0,975 и 0,988, ищите пропущенные слова.

Вход: текст реплики (--text) и пути к WAV-дублям. Словарь ударений (--stress) — JSON
{"слово": номер_ударной_гласной_с_нуля}, например {"проверка": 1}.
Выход: таблица в stdout, полный отчёт (--report JSON), копия лучшего дубля (--copy-to).
Код возврата: 0, если лучший дубль прошёл --min-ratio; иначе 1 (пустой ASR или реплика без букв = ratio 0).
Языки: пороги и эвристики подобраны на русском. --lang en (de, es…) включает ASR и числа словами на этом
языке и честное сравнение букв; ударение и темп для них приблизительны или выключены (см. выше).
Зависимости: faster-whisper, numpy, soundfile, scipy, num2words; librosa — только для --stress и --max-f0.

Пример:
  python3 tools/voice/pick_take.py --text "Проверка заняла минуту." voice/cand/0-*.wav \\
      --copy-to voice/raw-0.wav --report qa/pick-0.json
  python3 tools/voice/pick_take.py --text "..." take*.wav --model small --stress stress.json
  python3 tools/voice/pick_take.py --text "..." take*.wav --max-f0 250
"""
import argparse
import difflib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import numpy as np

VOWELS = set('аеёиоуыэюя')
LATIN_VOWELS = set('aeiouy')
STRESS_MARKS = {'\u0300', '\u0301'}       # знаки ударения в тексте реплики не буквы


def n_vowels(w, lang='ru'):
    vs = VOWELS if lang == 'ru' else VOWELS | LATIN_VOWELS
    return sum(ch in vs for ch in w)


def norm(w):
    return re.sub(r'[^а-яё]', '', w.lower()).replace('ё', 'е')


def say_int(m, lang):
    """Число словами через num2words; язык, которого он не знает, оставляет цифры."""
    try:
        from num2words import num2words
        return num2words(int(m.group()), lang=lang)
    except (ImportError, NotImplementedError, OverflowError):
        return m.group()


def letters(s, lang='ru'):
    """Текст → только буквы (любой алфавит) и цифры без слов, числа словами. Для сравнения ASR с репликой."""
    s = unicodedata.normalize('NFC', s).lower()
    if lang == 'ru':
        s = s.replace('ё', 'е')
    s = re.sub(r'(\d)[\s ](?=\d{3}\b)', r'\1', s)
    s = re.sub(r'\d+', lambda m: say_int(m, lang), s)
    return ''.join(ch for ch in s if ch.isdigit() or unicodedata.category(ch)[0] == 'L'
                   or (unicodedata.category(ch)[0] == 'M' and ch not in STRESS_MARKS))


def text_ratio(expected, heard, lang='ru'):
    """0..1; пустая сторона после нормализации = 0: сравнивать нечего, это не успех."""
    a, b = letters(expected, lang), letters(heard, lang)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def speech_rate(text, words, dur, lang='ru'):
    """Слогов в секунду: гласные текста реплики на длительность речи (первое–последнее слово ASR, иначе весь дубль)."""
    span = words[-1][2] - words[0][1] if words else dur
    return round(n_vowels(letters(text, lang), lang) / max(span, .1), 2)


def median_f0(path):
    """Медиана F0 по громким кадрам дубля, Гц (librosa.yin, 60–500 Гц)."""
    import librosa
    import soundfile as sf
    x, sr = sf.read(path)
    x = (x if x.ndim == 1 else x.mean(1)).astype(np.float32)
    f = librosa.yin(x, fmin=60, fmax=500, sr=sr, frame_length=2048)
    e = librosa.feature.rms(y=x, frame_length=2048, hop_length=512)[0]
    n = min(len(f), len(e))
    v = f[:n][e[:n] > e.max() * .2]
    return round(float(np.median(v))) if len(v) else 0


def envelope_db(x, sr):
    hop = int(.01 * sr)
    env = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2)) + 1e-9 for k in range(0, len(x) - hop, hop)])
    return 20 * np.log10(np.convolve(env, np.ones(3) / 3, 'same')), hop


def stress_marks(x, sr, words, expected, db, hop):
    """Эвристика ударения для слов из словаря expected. words: [(слово, начало, конец)]."""
    import librosa
    from scipy.signal import find_peaks
    f0, _, _ = librosa.pyin(x, fmin=70, fmax=500, sr=sr, frame_length=1024, hop_length=hop)
    marks = {}
    for w, a, b in words:
        k = norm(w)
        if k not in expected:
            continue
        i0, i1 = int(max(0, a - .03) / .01), int(min(len(db), (b + .03) / .01))
        seg = db[i0:i1]
        if len(seg) < 5:
            marks[k] = '?'; continue
        pks, _ = find_peaks(seg, distance=5, prominence=3)
        if len(pks) != n_vowels(k):
            marks[k] = f'?{len(pks)}/{n_vowels(k)}'; continue
        wts = []
        for p in pks:
            thr = seg[p] - 6; lo = hi = p
            while lo > 0 and seg[lo - 1] > thr: lo -= 1
            while hi < len(seg) - 1 and seg[hi + 1] > thr: hi += 1
            fp = f0[i0 + lo:i0 + hi + 1]; fp = fp[~np.isnan(fp)]
            wts.append(((hi - lo + 1) * .01, seg[p], np.median(fp) if len(fp) else np.nan))
        pm = np.nan if all(np.isnan(t[2]) for t in wts) else np.nanmedian([t[2] for t in wts])
        sc = [d * 10 ** (L / 20) * (1 + (0 if np.isnan(pm) or np.isnan(pt) else (pt - pm) / pm)) for d, L, pt in wts]
        s = int(np.argmax(sc))
        marks[k] = 'ok' if s == expected[k] else f'X{s}'
    return marks


def measure(path, text, asr, expected=None, lang='ru'):
    """ASR и замеры одного дубля → словарь-строка отчёта."""
    import soundfile as sf
    x, sr = sf.read(path)
    x = (x if x.ndim == 1 else x.mean(1)).astype(np.float32)
    dur = round(len(x) / sr, 2)
    if len(x) < int(.01 * sr) * 3:          # короче 30 мс: ни огибающей, ни ASR не из чего строить
        return {'take': Path(path).name, 'asr': '', 'ratio': 0.0, 'dur': dur, 'stress': {}, 'ok': 0, 'bad': 0,
                'gaps_gt_025': [], 'clipped_end': True, 'words': [], 'error': f'дубль короче 30 мс ({dur} с)'}
    segs, _ = asr.transcribe(str(path), language=lang, word_timestamps=True, beam_size=5)
    words = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    heard = ' '.join(w[0] for w in words)
    db, hop = envelope_db(x, sr)
    stress = stress_marks(x, sr, words, expected, db, hop) if expected else {}
    gaps = [round(words[j + 1][1] - words[j][2], 2) for j in range(len(words) - 1) if words[j + 1][1] - words[j][2] > .25]
    return {'take': Path(path).name, 'asr': heard, 'ratio': round(text_ratio(text, heard, lang), 3), 'dur': dur,
            'rate': speech_rate(text, words, dur, lang),
            'stress': stress, 'ok': sum(v == 'ok' for v in stress.values()),
            'bad': sum(v.startswith('X') for v in stress.values()), 'gaps_gt_025': gaps,
            'clipped_end': bool(len(db) >= 3 and db[-3:].max() > db.max() - 30),
            # ключ слова для растяжки — та же Unicode-нормализация, что и для сравнения с репликой: norm() знает
            # только кириллицу и превращала английские слова в пустую строку (растяжка не проверялась)
            'words': [(letters(w, lang), round(b - a, 3)) for w, a, b in words]}


def add_stretch(rows, limit=1.3):
    """Растяжка слов против медианы того же слова по всем дублям. Меняет rows на месте."""
    med = {}
    for r in rows:
        for w, d in r['words']:
            if w:
                med.setdefault(w, []).append(d)
    med = {w: float(np.median(v)) for w, v in med.items()}
    for r in rows:
        sw = max(((d / med[w], w) for w, d in r['words'] if w and med.get(w)), default=(1.0, ''))
        r['stretch_ratio'] = (round(sw[0], 2), sw[1])
        r['stretch'] = bool(sw[0] > limit)
    return rows


def choose(rows, min_ratio=0.9, max_rate=6.3, max_f0=None):
    """Лучший дубль по правилам из докстринга модуля."""
    good = [r for r in rows if r['ratio'] >= min_ratio] or rows
    sane = [r for r in good if r.get('rate', 0) <= max_rate and (max_f0 is None or r.get('f0', 0) <= max_f0)]
    good = sane or good
    med = float(np.median([r['dur'] for r in rows]))
    return max(good, key=lambda r: (-r.get('stretch', False), -r['bad'], r['ok'], not r['clipped_end'],
                                    -len(r['gaps_gt_025']), round(r['ratio'], 2), -abs(r['dur'] - med)))


def main(argv=None):
    ap = argparse.ArgumentParser(description='Выбор лучшего дубля TTS по ASR, растяжке и паузам.')
    ap.add_argument('takes', nargs='+', type=Path, help='WAV-дубли одной реплики')
    ap.add_argument('--text', required=True, help='текст реплики')
    ap.add_argument('--lang', default='ru', help='язык реплики: код Whisper и num2words (ru, en, de…)')
    ap.add_argument('--model', default='large-v3', help='модель faster-whisper (large-v3)')
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--compute-type', default='int8')
    ap.add_argument('--min-ratio', type=float, default=0.9)
    ap.add_argument('--max-rate', type=float, default=6.3, help='потолок темпа, слогов/с (6,3)')
    ap.add_argument('--max-f0', type=float, help='потолок медианы F0, Гц (например 250); без флага не меряется')
    ap.add_argument('--stress', type=Path, help='JSON {"слово": номер ударной гласной с нуля}')
    ap.add_argument('--report', type=Path, help='куда записать отчёт JSON')
    ap.add_argument('--copy-to', type=Path, help='куда скопировать лучший дубль')
    a = ap.parse_args(argv)
    if not letters(a.text, a.lang):
        ap.error('в --text нет ни одной буквы: сравнивать ASR не с чем')
    from faster_whisper import WhisperModel
    asr = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)
    expected = {norm(k): int(v) for k, v in json.loads(a.stress.read_text()).items()} if a.stress else None
    kw = {} if a.lang == 'ru' else {'lang': a.lang}     # ru по умолчанию: старый вызов measure(p, text, asr, expected)
    rows = add_stretch([measure(p, a.text, asr, expected, **kw) for p in a.takes])
    if a.max_f0:
        for p, r in zip(a.takes, rows):
            r['f0'] = median_f0(p)
    for r in rows:
        flags = ' '.join(f for f in ['ТЯНЕТ' + str(r['stretch_ratio']) if r['stretch'] else '',
                                     'ОБРЫВ' if r['clipped_end'] else '',
                                     f"паузы {r['gaps_gt_025']}" if r['gaps_gt_025'] else '',
                                     f"ТЕМП {r['rate']}" if r.get('rate', 0) > a.max_rate else '',
                                     f"F0 {r['f0']}" if a.max_f0 and r.get('f0', 0) > a.max_f0 else ''] if f)
        print(f"{r['take']}  ratio {r['ratio']}  ok{r['ok']} X{r['bad']}  {flags} | {r['asr']}")
    best = choose(rows, a.min_ratio, a.max_rate, a.max_f0)
    best_path = a.takes[rows.index(best)]     # в отчёте только имена файлов, путь нужен для копии
    print('→', best_path)
    if a.copy_to:
        a.copy_to.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(best_path, a.copy_to)
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps({'text': a.text, 'best': best['take'], 'rows': rows,
                                        'stress_is_heuristic': True}, ensure_ascii=False, indent=1, default=str))
    return 0 if best['ratio'] >= a.min_ratio else 1


if __name__ == '__main__':
    sys.exit(main())
