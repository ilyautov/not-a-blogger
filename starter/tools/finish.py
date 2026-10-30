"""Сведение и QA: output/picture.mp4 + assets/audio/master.wav -> output/final.mp4, потом проверки:
  - ffmpeg -xerror: файл декодируется без ошибок;
  - faststart: moov в начале файла (площадки начинают показ, не докачав весь файл);
  - громкость ebur128: интегральная −15 ±1 LUFS, true peak ≤ −1,5 dBTP;
  - статика: самый длинный кусок, где кадр почти не меняется, ≤ 3 с (камера в кадре, поэтому мягче, чем tools/lint/still_lint.py);
  - ASR финала (faster-whisper) против текста реплик: ratio ≥ 0,9 — нижняя граница, не пропуск (пропущенные слова ищут отдельно);
  - ASR каждого дубля из voice/asr-N.json (пишет voice/trim.py): все ratio ≥ 0,9 (takes_asr_ge_0_9). Результат,
    у которого текст реплики в chunks.json или sha256 line-N.wav не совпадают с текущими, считается отсутствующим;
  Сверка слов: буквы и цифры любой письменности, ё = е; пустой текст или пустое распознавание = ratio 0.
  Все пороги и откуда они взялись: docs/QA-THRESHOLDS.md в корне набора.
  - контактный лист qa/sheet.jpg (кадр каждые 0,75 с с меткой времени);
  -> qa/final-result.json. Видео собирается во временный output/final.tmp.mp4 и встаёт на место вместе с отчётом;
     если сборка или проверка упала (ffmpeg, ASR…), отчёт пишется technical_failed с ошибкой, старый зелёный не остаётся.
     technical_pass = все проверки зелёные. Это НЕ одобрение: artistic_approval и
     publication_approved ставит только человек, посмотрев ролик.
Запуск (из папки starter): python3 locked.py render -- $PY tools/finish.py [--no-asr] [--lang ru]
--no-asr: для заглушки fake_track.py (гудки вместо речи) или если Whisper ещё не поставлен.
--lang: язык распознавания финала, код Whisper (ru, en, de…). По умолчанию переменная ASR_LANG, без неё ru."""
import argparse, difflib, hashlib, json, os, re, subprocess, sys, unicodedata
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent.parent
OUT = P / 'output/final.mp4'
TMP = P / 'output/final.tmp.mp4'                 # сборка и проверки идут здесь; на место OUT встаёт только проверенный файл
REPORT = P / 'qa/final-result.json'
NUM = {'200': 'двести', '0': 'ноль'}            # как ASR пишет цифры -> как в тексте (тот же словарь, что в voice/trim.py)


def run(c):
    try: return subprocess.run(c, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:   # без этого причина ffmpeg (нет файла, битый вход) тонет внутри исключения
        print(f'команда упала (код {e.returncode}): {" ".join(map(str, c))}\n{(e.stderr or "").strip()}', file=sys.stderr); raise


def words(x):
    """Слова для сверки: буквы, цифры и диакритики любой письменности; ё = е, ударение выкинуто, остальное — разделитель."""
    x = unicodedata.normalize('NFC', x.lower()).replace('ё', 'е').replace('\u0301', '').replace('\u0300', '')
    x = ''.join(c if unicodedata.category(c)[0] in 'LNM' else ' ' for c in x)
    return [NUM.get(w, w) for w in x.split()]


def ratio(want, got):
    """Сходство двух текстов по словам. Пустая сторона = 0: пустая нормализация не должна давать успех."""
    a, b = words(want), words(got)
    return round(difflib.SequenceMatcher(None, a, b, autojunk=False).ratio(), 3) if a and b else 0.0


def takes_asr(root=P):
    """Порог ASR на каждый дубль: (True | False | None, подробности). False — хоть один дубль < 0,9;
    None — у какой-то реплики нет asr-N.json или он устарел (другой текст в chunks.json, другой line-N.wav)."""
    chunks = json.loads((root / 'voice/chunks.json').read_text())
    low, stale = [], []
    for i, ch in enumerate(chunks):
        wav = root / f'voice/line-{i}.wav'
        try: a = json.loads((root / f'voice/asr-{i}.json').read_text())
        except (OSError, ValueError): stale.append(i); continue
        if (a.get('text') != ch['text'] or not wav.is_file() or not isinstance(a.get('ratio'), (int, float))
                or a.get('line_sha256') != hashlib.sha256(wav.read_bytes()).hexdigest()):
            stale.append(i); continue
        if a['ratio'] < .9: low.append({'line': i, 'ratio': a['ratio']})
    ok = False if low else None if stale or not chunks else True
    return ok, {'below_0_9': low, 'missing_or_stale': stale}


def verdict(checks, fake):
    """technical_failed — есть False; preview_partial — гудки или проверка не выполнена (None); иначе ready_for_user_preview."""
    if any(v is False for v in checks.values()): return 'technical_failed'
    return 'preview_partial' if fake or any(v is None for v in checks.values()) else 'ready_for_user_preview'


def sheet(v, step=.75, cols=8):
    from PIL import Image, ImageDraw, ImageFont
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(v), '-vf', f'fps=1/{step},scale=270:480', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3); rows = (len(fr) + cols - 1) // cols
    im = Image.new('RGB', (270 * cols, 480 * rows)); dr = ImageDraw.Draw(im)
    font = None
    for f in ('/System/Library/Fonts/Menlo.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'):
        if os.path.exists(f): font = ImageFont.truetype(f, 22); break
    font = font or ImageFont.load_default()
    for i, f in enumerate(fr):
        x, y = 270 * (i % cols), 480 * (i // cols); im.paste(Image.fromarray(f), (x, y))
        dr.rectangle([x, y, x + 84, y + 28], fill=(0, 0, 0)); dr.text((x + 4, y + 2), f'{i * step + step / 2:5.2f}', fill=(255, 230, 0), font=font)
    im.save(P / 'qa/sheet.jpg', quality=85)


def longest_still(v, fps):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(v), '-vf', 'scale=135:240,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 240, 135).astype(np.float32)
    still = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2)) < 0.15     # средняя разница соседних кадров < 0,15 из 255
    longest = cur = at = 0
    for i, st in enumerate(still):
        cur = cur + 1 if st else 0
        if cur > longest: longest, at = cur, i - cur + 1
    return round(longest / fps, 2), round(at / fps, 2)


def asr_check(v, vt, lang):
    from faster_whisper import WhisperModel
    asr = WhisperModel(os.environ.get('ASR_MODEL', 'large-v3'), device='cpu', compute_type='int8')
    segs, _ = asr.transcribe(str(v), language=lang, beam_size=5)
    text = ' '.join(x.text.strip() for x in segs)
    return text, ratio(' '.join(c['text'] for c in vt['cues']), text)


def save(res):
    """Отчёт и видео встают парой: сначала убрать старый отчёт, потом видео, потом новый отчёт (обрыв между шагами не оставит зелёный от прошлого)."""
    REPORT.parent.mkdir(exist_ok=True); tmp = REPORT.with_suffix('.tmp')
    tmp.write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n')
    REPORT.unlink(missing_ok=True)
    if TMP.exists(): os.replace(TMP, OUT)
    os.replace(tmp, REPORT)


def failed_report(e):
    """Сбой посреди сборки или проверки: отчёт этого запуска = technical_failed с ошибкой; недопроверенное видео не ставим."""
    TMP.unlink(missing_ok=True)
    return {'status': 'technical_failed', 'technical_pass': False, 'checks': {}, 'error': f'{type(e).__name__}: {e}'[:500],
            'artistic_approval': False, 'publication_approved': False, 'video': None, 'video_sha256': None}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--no-asr', action='store_true')
    ap.add_argument('--lang', default=os.environ.get('ASR_LANG', 'ru'), help='ASR language code (Whisper), default ru'); a = ap.parse_args()
    try:
        res = build(a)
    except BaseException as e:     # и Ctrl+C: старый зелёный отчёт рядом с другим видео хуже, чем честный провал
        res = failed_report(e); save(res)
        print('QA: сборка или проверка упала, отчёт qa/final-result.json = technical_failed: ' + res['error'], file=sys.stderr)
        raise
    save(res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    failed = [name for name, value in res['checks'].items() if value is False]
    if failed:
        print('QA: провалены ' + ', '.join(failed), file=sys.stderr)
    return 1 if failed else 0


def build(a):
    OUT.parent.mkdir(exist_ok=True); (P / 'qa').mkdir(exist_ok=True); TMP.unlink(missing_ok=True)
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(P / 'output/picture.mp4'), '-i', str(P / 'assets/audio/master.wav'), '-map', '0:v', '-map', '1:a',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', str(TMP)])
    pr = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,r_frame_rate,codec_type', '-of', 'json', str(TMP)]).stdout)
    dur = float(pr['format']['duration']); vs = next(x for x in pr['streams'] if x['codec_type'] == 'video')
    num, den = map(int, vs['r_frame_rate'].split('/')); fps = num / den
    xerr = subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(TMP), '-f', 'null', '-'], capture_output=True, text=True)
    sheet(TMP); still, still_at = longest_still(TMP, fps)
    eb = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(TMP), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', eb)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', eb)[-1]); LRA = float(re.findall(r'LRA:\s+(-?[\d.]+) LU', eb)[-1])
    vt = json.loads((P / 'voice-track.json').read_text()); reel = json.loads((P / 'reel.json').read_text())
    asr_text, asr_ratio = ('', None) if a.no_asr else asr_check(TMP, vt, a.lang)
    takes_ok, takes = (None, {'skipped': 'fake' if vt.get('fake') else '--no-asr'}) if a.no_asr or vt.get('fake') else takes_asr()
    size_mb = round(TMP.stat().st_size / 1e6, 1)
    head = TMP.read_bytes()[:200000]; faststart = head.find(b'moov') != -1 and (head.find(b'mdat') == -1 or head.find(b'moov') < head.find(b'mdat'))
    checks = {'decodes': xerr.returncode == 0, 'faststart': faststart, 'loudness': abs(I + 15) <= 1 and TP <= -1.5, 'static_le_3s': still <= 3,
              'format_1080x1920_30fps': vs['width'] == 1080 and vs['height'] == 1920 and abs(fps - 30) < .001,
              'duration_ok': dur <= reel.get('max_duration', 60), 'size_le_100mb': size_mb <= 100, 'asr_ge_0_9': None if a.no_asr else asr_ratio >= .9,
              'takes_asr_ge_0_9': takes_ok}
    status = verdict(checks, bool(vt.get('fake')))
    res = {'status': status, 'technical_pass': status == 'ready_for_user_preview', 'checks': checks,
           'artistic_approval': False, 'publication_approved': False,
           'video': 'output/final.mp4', 'video_sha256': hashlib.sha256(TMP.read_bytes()).hexdigest(), 'duration': round(dur, 3), 'size_mb': size_mb,
           'size': f"{vs['width']}x{vs['height']}", 'fps': vs['r_frame_rate'], 'ffmpeg_xerror': 'pass' if xerr.returncode == 0 else xerr.stderr[:300],
           'loudness': {'integrated_lufs': I, 'true_peak_dbfs': TP, 'lra': LRA}, 'longest_static_s': still, 'longest_static_at_s': still_at,
           'asr_final': asr_text, 'asr_language': None if a.no_asr else a.lang, 'asr_vs_script_ratio': asr_ratio, 'asr_takes': takes, 'voice_fake': bool(vt.get('fake')), 'voice_track_sha256': vt['sha256'],
           'music': reel['music'], 'sheet': 'qa/sheet.jpg'}
    return res


if __name__ == '__main__':
    sys.exit(main())
