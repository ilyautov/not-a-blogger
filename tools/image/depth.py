#!/usr/bin/env python3
"""Карта глубины картинки через Depth-Anything-V2-Small, локально.

Что делает: прогоняет изображение через модель оценки глубины и сохраняет серую карту
того же размера: 0 — дальше всего, 255 — ближе всего к зрителю. Карта нужна depth_layers.py,
чтобы порезать картинку на слои для параллакса вместо плоского Ken Burns.

Модель: только depth-anything/Depth-Anything-V2-Small-hf (лицензия Apache-2.0).
Base и Large распространяются под CC-BY-NC, для них скрипт выдаёт предупреждение.
Весов в репозитории нет. Скачайте их один раз сами:
  huggingface-cli download depth-anything/Depth-Anything-V2-Small-hf
или запустите скрипт с --download. По умолчанию работает офлайн, только из локального кэша.
--model может указывать и на локальную папку с весами.

Вход: изображение (jpg/png). Выход: <имя>.depth.png рядом (или --out), строка-отчёт.
Зависимости: torch, transformers, pillow, numpy.

Пример:
  python3 tools/image/depth.py assets/art/room.jpg
  python3 tools/image/depth.py assets/art/room.jpg --out /tmp/room.depth.png --download
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageOps

DEFAULT_MODEL = 'depth-anything/Depth-Anything-V2-Small-hf'


def normalize(depth):
    """Привести карту глубины к uint8 0..255 (0 — дальше всего)."""
    d = np.asarray(depth, dtype=np.float64)
    span = d.max() - d.min()
    if span <= 0:
        return np.zeros(d.shape, np.uint8)
    return ((d - d.min()) / span * 255).astype(np.uint8)


def load_image(path):
    """Открыть картинку с учётом EXIF Orientation: телефонные JPEG хранят кадр повёрнутым,
    cv2.imread в depth_layers.py его разворачивает, и без этого карта глубины не совпала бы с картинкой."""
    return ImageOps.exif_transpose(Image.open(path))


def load_model(model=DEFAULT_MODEL, download=False):
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation
    if 'small' not in model.lower():
        print('ВНИМАНИЕ: веса Depth-Anything-V2 Base/Large — CC-BY-NC; для открытого проекта берите Small',
              file=sys.stderr)
    kw = {'local_files_only': not download}
    proc = AutoImageProcessor.from_pretrained(model, **kw)
    net = AutoModelForDepthEstimation.from_pretrained(model, **kw).eval()
    return proc, net


def estimate(img, proc, net):
    """PIL.Image → карта глубины uint8 того же размера."""
    import torch
    img = img.convert('RGB')
    with torch.no_grad():
        out = net(**proc(images=img, return_tensors='pt')).predicted_depth
    d = torch.nn.functional.interpolate(out[:, None], size=img.size[::-1], mode='bicubic',
                                        align_corners=False)[0, 0].numpy()
    return normalize(d)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Карта глубины через Depth-Anything-V2-Small.')
    ap.add_argument('image')
    ap.add_argument('--out', help='куда писать (по умолчанию <имя>.depth.png)')
    ap.add_argument('--model', default=DEFAULT_MODEL, help='имя модели на HF или локальная папка')
    ap.add_argument('--download', action='store_true', help='разрешить скачивание весов')
    a = ap.parse_args(argv)
    if not a.download:
        os.environ.setdefault('HF_HUB_OFFLINE', '1')
    try:
        proc, net = load_model(a.model, a.download)
    except OSError as e:
        sys.exit(f'модель не найдена локально ({e.__class__.__name__}). Скачайте: '
                 f'huggingface-cli download {a.model}  или запустите с --download')
    img = load_image(a.image)
    d = estimate(img, proc, net)
    dst = a.out or os.path.splitext(a.image)[0] + '.depth.png'
    Image.fromarray(d).save(dst)
    print(dst, img.size, 'медиана', int(np.median(d)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
