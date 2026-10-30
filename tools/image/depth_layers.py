#!/usr/bin/env python3
"""Резка картинки на слои по карте глубины для настоящего параллакса.

Что делает: по порогам глубины (--cuts, 0..255) делит картинку на N+1 слоёв от дальнего к
ближнему. Маски чистятся морфологией (закрытие + открытие эллипсом 9×9): без этого слой
рассыпается на сотни пятен, и параллакс читается как шум. Всё, что закрыто более близкими
слоями, на каждом слое дорисовывается инпейнтом (Telea), иначе при разъезде слоёв в кадре
открываются дыры. Дальний слой отдаётся целиком (альфа 255 везде), ближние — по своей маске,
расширенной и размытой, чтобы край не был бритвенным.

Вход: изображение и карта глубины (по умолчанию <имя>.depth.png рядом, её делает depth.py;
0 — дальше всего, 255 — ближе всего). Выход: PNG с альфой <имя>.L0.png … <имя>.LN.png
(или в --out-dir), по строке-отчёту с покрытием каждого слоя.
Зависимости: opencv-python-headless, numpy.

Пример:
  python3 tools/image/depth_layers.py assets/art/room.jpg
  python3 tools/image/depth_layers.py assets/art/room.jpg --cuts 70 150 --out-dir build/layers
"""
import argparse
import os
import sys

import cv2
import numpy as np


def make_masks(depth, cuts, kernel=9):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel, kernel))
    edges = [0] + sorted(cuts) + [256]
    masks = []
    for i in range(len(edges) - 1):
        m = ((depth >= edges[i]) & (depth < edges[i + 1])).astype('uint8') * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
        masks.append(m)
    return masks, k


def make_layers(img, depth, cuts=(55, 105, 175), kernel=9, feather=6.0):
    """img: BGR uint8 (h, w, 3); depth: uint8 (h, w). Возвращает [(BGRA uint8, покрытие_%)]."""
    if depth.shape != img.shape[:2]:
        h, w = img.shape[:2]
        dh, dw = depth.shape
        if abs(dw / dh - w / h) > 0.02:
            raise ValueError(f'карта глубины {dw}×{dh} не той пропорции, что картинка {w}×{h}: '
                             'обычно это EXIF-поворот телефонного JPEG; пересчитайте карту свежим depth.py')
        depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_LINEAR)
    masks, k = make_masks(depth, cuts, kernel)
    h, w = depth.shape
    out = []
    for i in range(len(masks)):
        nearer = np.zeros((h, w), 'uint8')
        for j in range(i + 1, len(masks)):
            nearer = cv2.bitwise_or(nearer, masks[j])
        plate = img if not nearer.any() else cv2.inpaint(img, cv2.dilate(nearer, k, iterations=2), 7, cv2.INPAINT_TELEA)
        if i == 0:
            alpha = np.full((h, w), 255, 'uint8')
        else:
            alpha = cv2.GaussianBlur(cv2.dilate(masks[i], k, iterations=2), (0, 0), feather)
        out.append((np.dstack([plate, alpha]), round(float(masks[i].mean()) / 2.55, 1)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description='Слои параллакса по карте глубины.')
    ap.add_argument('image')
    ap.add_argument('--depth', help='карта глубины (по умолчанию <имя>.depth.png)')
    ap.add_argument('--cuts', type=int, nargs='+', default=[55, 105, 175], help='пороги глубины 0..255')
    ap.add_argument('--out-dir', help='папка для слоёв (по умолчанию рядом с картинкой)')
    a = ap.parse_args(argv)
    stem = os.path.splitext(a.image)[0]
    img = cv2.imread(a.image)
    depth = cv2.imread(a.depth or stem + '.depth.png', cv2.IMREAD_GRAYSCALE)
    if img is None or depth is None:
        sys.exit('не прочитал картинку или карту глубины')
    base = os.path.join(a.out_dir, os.path.basename(stem)) if a.out_dir else stem
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    try:
        layers = make_layers(img, depth, a.cuts)
    except ValueError as e:
        sys.exit(str(e))
    for i, (layer, cover) in enumerate(layers):
        p = f'{base}.L{i}.png'
        cv2.imwrite(p, layer, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        print(p, 'покрытие', cover, '%')
    return 0


if __name__ == '__main__':
    sys.exit(main())
