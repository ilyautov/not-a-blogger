"""Уточнить начала слов в voice-track.json по энергии звука.
Зачем: Whisper ставит начало слова после паузы с ошибкой до 0,1 с (3 кадра). Для «ноля», который должен встать
в кадре ровно на слове, этого много. Скрипт сдвигает start только у слов, перед которыми в окне
[start − 0,05; start + 0,15] есть тишина: новое начало = первый громкий кадр после этой тишины.
Слова внутри слитной речи не трогает. Файл звука и его sha256 не меняются.

Скопируйте рядом с trim.py (SECOND-REEL.md): cp examples/subscription/voice/snap_onsets.py voice/
Запуск после trim.py, из папки starter:  python3 locked.py voice -- "$PY" voice/snap_onsets.py
Для гудков fake_track.py не нужен: там начала заданы точно."""
import json
from pathlib import Path
import numpy as np, soundfile as sf

P = Path(__file__).resolve().parent.parent
HOP = .01                 # шаг анализа, с
QUIET = 35                # тишина: на 35 dB тише пика дорожки
BEFORE, AFTER = .05, .15  # окно поиска вокруг начала по ASR, с


def main():
    vt = json.loads((P / 'voice-track.json').read_text())
    if vt.get('fake'):
        print('fake-дорожка: уточнять нечего'); return
    x, sr = sf.read(P / vt['file']); x = x if x.ndim == 1 else x.mean(1); h = int(HOP * sr)
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9) for i in range(0, len(x) - h, h)])
    thr = db.max() - QUIET
    for w in vt['words']:
        a, b = max(0, int((w['start'] - BEFORE) / HOP)), min(len(db), int((w['start'] + AFTER) / HOP))
        quiet = np.nonzero(db[a:b] < thr)[0]
        if not len(quiet): continue
        loud = np.nonzero(db[a + quiet[-1] + 1:b] >= thr)[0]
        if not len(loud): continue
        new = round((a + quiet[-1] + 1 + loud[0]) * HOP, 3)
        if abs(new - w['start']) >= HOP and new < w['end'] - .05:
            print(f"{w['text']:>12}  {w['start']:.3f} -> {new:.3f}"); w['start'] = new
    for c in vt['cues']:
        ws = [w for w in vt['words'] if w['line'] == c['id']]
        if ws: c['start'] = ws[0]['start']
    vt['onsets_snapped'] = True
    (P / 'voice-track.json').write_text(json.dumps(vt, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
