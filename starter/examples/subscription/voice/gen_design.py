"""Синтез реплик OmniVoice БЕЗ референса и без клона (режим voice design) -> voice/raw-N.wav.
Нужен учебному примеру, чтобы собрать ролик с речью, не записывая и не публикуя ничей голос.
Голос задаётся описанием атрибутов (OMNI_INSTRUCT), а не чужой записью. Веса OmniVoice — CC-BY-NC, см. THIRD-PARTY.md.

Скопируйте рядом с voice/gen_omni.py (SECOND-REEL.md, шаг 2): cp examples/subscription/voice/gen_design.py voice/
Окружение: OMNI_MODEL, OMNI_DEVICE, OMNI_SPEED — как у gen_omni.py; OMNI_REF не нужен.
  OMNI_INSTRUCT  атрибуты голоса через запятую, по умолчанию «male, middle-aged, moderate pitch»
Запуск (из папки starter):
  python3 locked.py voice -- "$OMNI_PY" voice/gen_design.py      # все реплики
  python3 locked.py voice -- "$PY" voice/trim.py                  # подрезка, ASR, voice-track.json
Сид 42, обрыв окончания лечится тем же жертвенным хвостом, что в gen_omni.py."""
import json, os, sys
from pathlib import Path
import numpy as np, soundfile as sf, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_omni import OUT, TAIL, SR, SPEED, DEVICE, env_path, clipped   # noqa: E402
import passport   # noqa: E402

INSTRUCT = os.environ.get('OMNI_INSTRUCT', 'male, middle-aged, moderate pitch')


def main():
    os.environ.setdefault('HF_DEACTIVATE_ASYNC_LOAD', '1')
    from omnivoice import OmniVoice
    model_dir = env_path('OMNI_MODEL')
    chunks = json.loads((OUT / 'chunks.json').read_text())
    dtype = torch.float32 if DEVICE == 'cpu' else torch.float16
    print('OmniVoice (voice design):', INSTRUCT, flush=True)
    m = OmniVoice.from_pretrained(str(model_dir), device_map=DEVICE, dtype=dtype)
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    for i in (only or range(len(chunks))):
        ch = chunks[i]
        for tail in (False, True):
            torch.manual_seed(42); np.random.seed(42)
            text = ch['text'] + (' ' + TAIL if tail else '')
            x = np.asarray(m.generate(text=text, language='ru', instruct=INSTRUCT,
                                      speed=None if SPEED == 1.0 else SPEED)[0], dtype=np.float32).squeeze()
            if tail or not clipped(x, SR):
                break
            print(i, 'конец рвётся, повтор с хвостом', flush=True)
        sf.write(OUT / f'raw-{i}.wav', x, SR)
        ch['tail'] = tail; ch['engine'] = 'omnivoice-design'; ch['omni_instruct'] = INSTRUCT; ch['omni_speed'] = SPEED
        passport.write(OUT / f'raw-{i}.wav', ch['text'], 'omnivoice-design', {'speed': SPEED, 'seed': 42, 'tail': tail, 'device': DEVICE,
                                                                            'model': model_dir.name, 'instruct': INSTRUCT})
        print(i, f'{len(x) / SR:.2f}s tail={tail}', flush=True)
    (OUT / 'chunks.json').write_text(json.dumps(chunks, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main()
