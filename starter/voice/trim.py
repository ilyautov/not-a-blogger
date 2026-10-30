"""Подрезка дублей по ASR, склейка и пословная разметка -> voice-track.json.

Что делает с каждым voice/raw-N.wav:
  0. сверяет дубль с паспортом voice/raw-N.json (voice/passport.py): sha256 и текст реплики. Не сходится — стоп:
     переписанный текст со старым звуком дал бы в кадре слова прошлой версии;
  1. faster-whisper (large-v3, слова с таймкодами) находит первое и последнее слово;
  2. начало = раньшее из «первое слово ASR − 0,12 с» и «атака по энергии − 0,05 с»;
  3. конец = по энергии (последний кадр громче пик −45 dB + 80 мс); если был жертвенный хвост
     «Вот так вот.», режем в самой тихой точке между репликой и хвостом;
  4. фейды 20/40 мс, тишина pause из chunks.json в конец -> voice/line-N.wav;
  5. внутренние паузы длиннее MAX_GAP ужимаются до MAX_GAP (рил должен быть плотным);
  6. ASR готового дубля -> voice/asr-N.json + ratio (сходство с текстом; < 0,9 = точно сломан, ≥ 0,9 ещё не чисто: слушать ушами)
     и sha256 line-N.wav; tools/finish.py проваливает ролик, если хоть у одного дубля ratio < 0,9, и не верит
     результату, если текст реплики или line-N.wav с тех пор поменялись.
Потом склейка всех line-N.wav, loudnorm −16 LUFS / TP −2 (как у дублей, см. QA-THRESHOLDS.md) -> assets/audio/voice-track.wav
и разметка: каждое слово из voice/lines.json получает start/end -> voice-track.json (по нему живёт сцена).

lines.json — что ВИДНО в субтитрах, chunks.json — что ПРОИЗНОСИТСЯ. Они расходятся в цифрах и латинице:
  произносим «двести», показываем «200». Если одно показанное слово = несколько произнесённых,
  пиши «Mi_Box{2}» (подчёркивание = пробел на экране, {2} = съедает 2 произнесённых слова).
NUM ниже — словарь «как ASR пишет цифру» -> «как она в тексте», для сверки.

Запуск (из папки starter):
  python3 locked.py voice -- $PY voice/trim.py          # все реплики, склейка, разметка
  python3 locked.py voice -- $PY voice/trim.py 1        # переподрезать только реплику 1, потом склейка
  python3 locked.py voice -- $PY voice/trim.py track    # только склейка и разметка
  python3 locked.py voice -- $PY voice/trim.py --lang=en  # язык распознавания (по умолчанию ru)
Переменные: ASR_MODEL (по умолчанию large-v3; для пробы быстрее small), ASR_LANG (код языка Whisper,
по умолчанию ru; флаг --lang=<код> важнее переменной). TAIL и NUM ниже русские: для другого языка замени их.
Сверка текста берёт буквы и цифры любой письменности (ё = е, знак ударения не считается)."""
import difflib, hashlib, json, os, re, subprocess, sys, unicodedata
from pathlib import Path
import numpy as np, soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import passport   # noqa: E402

P = Path(__file__).resolve().parent.parent
OUT = P / 'voice'
CH = json.loads((OUT / 'chunks.json').read_text())
SHOW = json.loads((OUT / 'lines.json').read_text())
LEAD, TAIL_SIL = 0.10, 0.7       # тишина до первой реплики и после последней, с
MAX_GAP = 0.34                   # самая длинная пауза внутри реплики, с
TAIL = 'Вот так вот.'
NUM = {'200': 'двести', '0': 'ноль'}          # дополняй под свой текст: '80': 'восемьдесят', '4': 'четыре'
VOICE_WAV = P / 'assets/audio/voice-track.wav'
ASR_LANG = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), os.environ.get('ASR_LANG', 'ru'))
assert len(CH) == len(SHOW), 'chunks.json и lines.json должны иметь одинаковое число реплик'


def norm(w):
    """Слово для сверки: строчные буквы, цифры и знаки-диакритики любой письменности; ё = е, ударение (U+0301/U+0300) выкинуто."""
    w = unicodedata.normalize('NFC', w.lower()).replace('ё', 'е').replace('\u0301', '').replace('\u0300', '')
    w = ''.join(c for c in w if unicodedata.category(c)[0] in 'LNM')
    return NUM.get(w, w)


def match_ratio(text, words):
    """Сходство текста реплики со словами ASR. Пустой текст или пустое распознавание = 0, а не 1."""
    a = [norm(t) for t in text.split() if norm(t)]; b = [norm(w) for w in words if norm(w)]
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)]))


def asr_words(model, wav):
    segs, _ = model.transcribe(str(wav), language=ASR_LANG, word_timestamps=True, beam_size=5)
    return [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in s.words]


def db_frames(x, sr, hop):
    return np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x) - hop, hop)])


def no_words(i, wav):
    """Пустое распознавание: дальше резать не по чему (раньше падало IndexError)."""
    return SystemExit(f'trim: реплика {i}: ASR не нашёл ни одного слова в {wav.relative_to(P)} (тишина, обрыв или другой язык — проверьте ASR_LANG/--lang). '
                      f'Послушайте файл и перезапишите реплику {i}: ./make.sh live … или python3 locked.py voice -- "$OMNI_PY" voice/gen_omni.py {i}')


def token_errors(lines=None):
    """Сколько произнесённых слов съедает каждая строка lines.json ({N} = N слов) против слов реплики в chunks.json."""
    out = []
    for li in (range(len(CH)) if lines is None else lines):
        say = len([t for t in CH[li]['text'].split() if norm(t)]); shown = sum(n for _, n in show_tokens(SHOW[li]))
        if shown != say:
            out.append(f'реплика {li}: voice/lines.json съедает {shown} произнесённых слов, voice/chunks.json произносит {say}. '
                       f'Исправьте voice/lines.json (одно слово на экране = одно слово речи; «Mi_Box{{2}}» = два) или текст в chunks.json')
    return out


def trim(i, asr):
    ch = CH[i]; raw = OUT / f'raw-{i}.wav'
    words = asr_words(asr, raw); allw = list(words)
    if not words: raise no_words(i, raw)
    x, sr = sf.read(raw); hop = int(.01 * sr); db = db_frames(x, sr, hop)
    if len(db) == 0: raise SystemExit(f'trim: реплика {i}: {raw.relative_to(P)} короче 20 мс — перезапишите реплику {i}')
    tail_start = None
    if ch.get('tail'):   # найти «Вот так вот.» с конца по нечёткому совпадению
        tw = [norm(t) for t in TAIL.split()]
        for q in range(len(words) - 1, 0, -1):
            seg = [norm(w[0]) for w in words[q:q + len(tw)]]
            if len(seg) >= 2 and all(difflib.SequenceMatcher(None, a, b).ratio() >= .6 for a, b in zip(seg, tw)):
                tail_start = words[q][1]; words = words[:q]; break
    if not words: raise SystemExit(f'trim: реплика {i}: в {raw.relative_to(P)} ASR услышал только хвост «{TAIL}» — перезапишите реплику {i}')
    start = max(0.0, words[0][1] - 0.12)
    on = np.nonzero(db > db.max() - 40)[0]      # ASR иногда ставит первое слово позже атаки
    if len(on): start = min(start, max(0.0, on[0] * .01 - 0.05))
    if tail_start is not None:
        a2, b2 = int((words[-1][2] - 0.04) * sr), int((tail_start + 0.10) * sr)
        e = [np.sqrt(np.mean(x[k:k + hop] ** 2)) for k in range(a2, b2, hop)]
        end = (a2 + int(np.argmin(e)) * hop + hop // 2) / sr
    else:
        nz = np.nonzero(db > db.max() - 45)[0]
        end = min(len(x) / sr, max(words[-1][2] + 0.08, nz[-1] * .01 + 0.08))
    fin = OUT / f'line-{i}.wav'; L = end - start
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{start:.3f}', '-t', f'{L:.3f}', '-i', str(raw),
                    '-af', f'afade=t=in:d=0.02,afade=t=out:st={max(0, L - 0.04):.3f}:d=0.04,apad=pad_dur={ch["pause"]}',
                    '-ar', '24000', '-ac', '1', str(fin)], check=True)
    squeeze(fin, ch['pause'])
    tw = asr_words(asr, fin)
    ratio = match_ratio(ch['text'], [w[0] for w in tw])
    (OUT / f'asr-{i}.json').write_text(json.dumps({'text': ch['text'], 'raw_words': allw, 'take_words': tw, 'trim': [round(start, 3), round(end, 3)],
                                                  'ratio': round(ratio, 3), 'raw_sha256': passport.sha256(raw), 'line_sha256': passport.sha256(fin)},
                                                 ensure_ascii=False, indent=1))
    print(i, f'{start:.2f}-{end:.2f} ratio {ratio:.2f} |', ' '.join(w for w, _, _ in tw), flush=True)


def squeeze(fin, pause):
    """Внутренние тишины (−40 dB от пика) длиннее MAX_GAP ужать до MAX_GAP: вырезать середину, края с фейдом 10 мс."""
    y, sr = sf.read(fin); hop = int(.01 * sr); db = db_frames(y, sr, hop); q = db < db.max() - 40
    body_end = len(y) - int(round(pause * sr))
    cuts, i = [], 0
    while i < len(q):
        if not q[i]: i += 1; continue
        j = i
        while j < len(q) and q[j]: j += 1
        a, b = i * hop, j * hop
        if a > 0 and b < body_end - hop and (b - a) / sr > MAX_GAP:
            keep = int(MAX_GAP * sr); cuts.append((a + keep // 2, b - keep // 2))
        i = j
    if not cuts: return
    parts, prev, f = [], 0, int(.01 * sr)
    for m0, m1 in cuts:
        seg = y[prev:m0].copy(); seg[-f:] *= np.linspace(1, 0, f); parts.append(seg); prev = m1
    seg = y[prev:].copy(); seg[:f] *= np.linspace(0, 1, f); parts.append(seg)
    sf.write(fin, np.concatenate(parts), sr); print('  squeeze', fin.name, [round((b - a) / sr, 2) for a, b in cuts])


def concat():
    lst = OUT / 'list.txt'; lst.write_text(''.join(f"file 'line-{i}.wav'\n" for i in range(len(CH))))
    tmp = OUT / 'concat.wav'; VOICE_WAV.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-ar', '24000', '-ac', '1', str(tmp)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-af', f'loudnorm=I=-16:TP=-2,adelay={int(LEAD * 1000)},apad=pad_dur={TAIL_SIL}',
                    '-ar', '44100', '-ac', '1', str(VOICE_WAV)], check=True)


def show_tokens(s):
    """«Mi_Box{2}» -> ('Mi Box', 2): показанное слово и сколько произнесённых слов оно съедает."""
    out = []
    for t in s.split():
        m = re.match(r'^(.*?)\{(\d+)\}([.,:!?]*)$', t)
        out.append((m.group(1) + m.group(3), int(m.group(2))) if m else (t, 1))
    return [(a.replace('_', ' '), n) for a, n in out if a.strip('—–-') or n > 1]


def track(asr):
    words, cues, off = [], [], LEAD
    for li, ch in enumerate(CH):
        a = json.loads((OUT / f'asr-{li}.json').read_text())
        if a.get('text') != ch['text']: sys.exit(f'trim: asr-{li}.json от старого текста реплики {li}; переподрежьте: voice/trim.py {li}')
        if not a.get('take_words'): raise no_words(li, OUT / f'line-{li}.wav')
        if bad := token_errors([li]): sys.exit('trim: ' + bad[0])
        tw = [(w[0], w[1] + off, w[2] + off) for w in a['take_words']]
        say = [t for t in ch['text'].split() if norm(t)]
        s_n = [norm(t) for t in say]; a_n = [norm(w) for w, _, _ in tw]
        times = [None] * len(say)
        for blk in difflib.SequenceMatcher(None, s_n, a_n, autojunk=False).get_matching_blocks():
            for k in range(blk.size): times[blk.a + k] = (tw[blk.b + k][1], tw[blk.b + k][2])
        known = [i for i, t in enumerate(times) if t]
        for i in range(len(times)):   # несовпавшие слова: равномерно между соседними известными
            if times[i] is None:
                lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
                x0 = times[lo][1] if lo is not None else tw[0][1]; x1 = times[hi][0] if hi is not None else tw[-1][2]
                n = (hi if hi is not None else len(times)) - (lo if lo is not None else -1); j = i - (lo if lo is not None else -1)
                times[i] = (x0 + (x1 - x0) * (j - 1) / n, x0 + (x1 - x0) * j / n)
        print(li, f'matched {len(known)}/{len(say)}')
        k = 0; st = None
        for text, n in show_tokens(SHOW[li]):
            seg = times[k:k + n]
            words.append({'line': li, 'text': text, 'say': ' '.join(say[k:k + n]), 'start': round(seg[0][0], 3), 'end': round(seg[-1][1], 3)})
            st = st if st is not None else seg[0][0]; k += n
        assert k == len(say), f'реплика {li}: в lines.json {k} произнесённых слов, в chunks.json {len(say)} — поправь {{N}}'
        cues.append({'id': li, 'start': round(st, 3), 'end': round(words[-1]['end'], 3), 'text': ch['text'], 'show': SHOW[li]})
        off += dur(OUT / f'line-{li}.wav')
    aw = asr_words(asr, VOICE_WAV)
    out = {'file': 'assets/audio/voice-track.wav', 'sha256': hashlib.sha256(VOICE_WAV.read_bytes()).hexdigest(), 'duration': round(dur(VOICE_WAV), 3),
           'cues': cues, 'words': words, 'asr_text': ' '.join(w for w, _, _ in aw)}
    (P / 'voice-track.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (P / 'qa').mkdir(exist_ok=True)
    (P / 'qa/asr-track.json').write_text(json.dumps({'words': aw}, ensure_ascii=False, indent=1))
    print('ASR:', out['asr_text']); print('duration', out['duration'])


if __name__ == '__main__':
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    bad = [f'реплика {i}: {e}' for i in (only or range(len(CH))) if 'track' not in sys.argv and (e := passport.check(OUT / f'raw-{i}.wav', CH[i]['text']))]
    if bad: sys.exit('trim: дубли не сходятся с паспортом\n' + '\n'.join(bad))
    if bad := token_errors(): sys.exit('trim: lines.json и chunks.json расходятся по словам\n' + '\n'.join(bad))   # до загрузки модели
    from faster_whisper import WhisperModel
    asr = WhisperModel(os.environ.get('ASR_MODEL', 'large-v3'), device='cpu', compute_type='int8')
    if 'track' not in sys.argv:
        for i in (only or range(len(CH))): trim(i, asr)
    concat(); track(asr)
