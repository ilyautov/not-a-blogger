#!/usr/bin/env python3
"""Процедурные звуковые эффекты на numpy: 14 видов, детерминированно по seed.

Что делает: генерирует короткие SFX без сэмплов и лицензий: click, impact, whoosh, hiss,
sweep, tick, tone, buzz, step, riser, glitch, thud, chime, whip. Один и тот же вид с тем же
seed и параметрами всегда даёт один и тот же массив, поэтому сборка ролика воспроизводима.
Пик каждого звука не выше 1.0 (при необходимости сигнал масштабируется).

Как библиотека:  from sfx import render;  x = render('whip', length=0.3, seed=8, sr=48000)
Как CLI: вход — вид и параметры, выход — моно WAV.

Параметры (если вид их понимает): --length (с), --seed, --freq (Гц), --decay, --weight,
--f0/--f1 (Гц, для riser), --sr (48000).

Пример:
  python3 tools/audio/sfx.py --list
  python3 tools/audio/sfx.py whip --out assets/audio/whip.wav --length 0.32 --seed 8
  python3 tools/audio/sfx.py chime --out chime.wav --freq 880
"""
import argparse
import sys

import numpy as np

SR = 48000


def _smoothstep(n):
    x = np.linspace(0, 1, max(1, n))
    return x * x * (3 - 2 * x)


def _onepole_varying(noise, widths):
    """Сглаживание шума одним полюсом с меняющейся шириной окна (яркость во времени)."""
    out = np.zeros(len(noise))
    acc = 0.0
    for i, (v, w) in enumerate(zip(noise, widths)):
        w = max(float(w), 2.0)
        acc = acc * (1 - 1 / w) + v / w
        out[i] = acc
    return out / (np.abs(out).max() + 1e-9)


def click(length=0.055, seed=42, sr=SR):
    rng = np.random.default_rng(seed); n = round(length * sr); t = np.arange(n) / sr
    return .55 * np.sin(2 * np.pi * (1550 * t - 5200 * t * t)) * np.exp(-t * 72) + .22 * rng.normal(0, 1, n) * np.exp(-t * 115)


def impact(length=0.32, seed=42, weight=1.0, sr=SR):
    rng = np.random.default_rng(seed); n = round(length * sr); t = np.arange(n) / sr
    return (.72 * np.sin(2 * np.pi * (78 * t - 30 * t * t)) * np.exp(-t * 13) + .17 * rng.normal(0, 1, n) * np.exp(-t * 34)) * weight


def whoosh(length=2.5, seed=42, sr=SR):
    """Обратный вжух: шум нарастает к концу, короткое гашение в самом конце."""
    rng = np.random.default_rng(seed); n = round(length * sr); t = np.arange(n) / sr
    air = np.convolve(rng.normal(0, 1, n), np.ones(55) / 55, mode='same')
    env = _smoothstep(n) ** 1.7
    k = min(n, int(.12 * sr)); env[n - k:] *= _smoothstep(k)[::-1]
    return (.62 * air + .20 * np.sin(2 * np.pi * (130 * t + 220 * t * t))) * env


def hiss(length=0.5, seed=7, sr=SR):
    rng = np.random.default_rng(seed); n = round(length * sr)
    noise = np.convolve(rng.normal(0, 1, n), np.ones(60) / 60, mode='same')
    return noise * np.sin(np.linspace(0, np.pi, n)) ** 2 * np.linspace(.4, 1, n)


def sweep(length=1.0, seed=42, sr=SR):
    rng = np.random.default_rng(seed); n = round(length * sr)
    noise = np.convolve(rng.normal(0, 1, n), np.ones(45) / 45, mode='same')
    return noise * np.sin(np.linspace(0, np.pi, n)) ** 2


def tick(length=0.03, freq=2400, sr=SR):
    t = np.arange(round(length * sr)) / sr
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 160)


def tone(length=0.25, freq=880, decay=18, sr=SR):
    t = np.arange(round(length * sr)) / sr
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)


def buzz(length=0.35, sr=SR):
    """Пила 110 Гц с ограниченной полосой: тревога, ошибка, сбой."""
    t = np.arange(round(length * sr)) / sr
    saw = 2 * ((t * 110) % 1) - 1
    return np.convolve(saw, np.ones(12) / 12, mode='same') * np.sin(np.linspace(0, np.pi, len(t))) ** .5


def step(length=0.09, freq=520, seed=5, sr=SR):
    """Шаг по плитке: щелчок с понижением высоты поверх короткого шума."""
    rng = np.random.default_rng(seed); n = round(length * sr); t = np.arange(n) / sr
    body = np.sin(2 * np.pi * freq * t * (1 - .35 * t / length)) * np.exp(-t * 70)
    noise = np.convolve(rng.normal(0, 1, n), np.ones(24) / 24, mode='same') * np.exp(-t * 120) * .6
    return (body + noise) * .9


def riser(length=1.2, seed=9, f0=180, f1=1400, sr=SR):
    """Нарастание напряжения: шум светлеет, синус скользит вверх; обрывается под удар."""
    rng = np.random.default_rng(seed); n = round(length * sr); x = np.arange(n) / sr / length
    glide = np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** x) / sr) * .5
    out = _onepole_varying(rng.normal(0, 1, n), 60 - 56 * x)
    return (out * .8 + glide) * x ** 2.2


def glitch(length=0.25, seed=4, sr=SR):
    """Цифровой сбой: прямоугольные всплески с понижением разрядности."""
    rng = np.random.default_rng(seed); n = round(length * sr); t = np.arange(n) / sr
    out = np.zeros(n)
    for _ in range(6):
        a = int(rng.uniform(0, .8) * n); b = min(n, a + int(rng.uniform(.03, .12) * n))
        f = rng.choice([230, 460, 690, 920, 1380])
        seg = np.sign(np.sin(2 * np.pi * f * t[a:b])); hold = max(1, int(rng.uniform(6, 40)))
        out[a:b] += np.repeat(seg[::hold], hold)[:b - a] * rng.uniform(.4, 1)
    out = np.convolve(out, np.ones(10) / 10, mode='same')
    k = min(n, round(.02 * sr)); out[n - k:] *= np.linspace(1, 0, k)
    return out * .7


def thud(length=0.5, freq=62, sr=SR):
    """Низкое падение: синус уходит вниз на октаву, плюс короткий стук."""
    n = round(length * sr); t = np.arange(n) / sr
    ph = 2 * np.pi * np.cumsum(freq * (2 ** (-t / length * 1.2))) / sr
    return np.sin(ph) * np.exp(-t * 7) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 220) * .35


def chime(length=0.7, freq=1046, sr=SR):
    """Колокольчик проверки: три партиала с разным затуханием."""
    t = np.arange(round(length * sr)) / sr
    out = (np.sin(2 * np.pi * freq * t) * np.exp(-t * 5) + .45 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 9)
           + .25 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 14))
    return out * (1 - np.exp(-t * 600)) * .55


def whip(length=0.32, seed=8, sr=SR):
    """Хлыст камеры: шум с быстрым спуском полосы, короткий и сухой."""
    rng = np.random.default_rng(seed); n = round(length * sr); x = np.arange(n) / sr / length
    out = _onepole_varying(rng.normal(0, 1, n), 4 + 90 * x)
    return out * np.sin(np.pi * x) ** .6 * (1 - x * .5)


KINDS = {
    'click': click, 'impact': impact, 'whoosh': whoosh, 'hiss': hiss, 'sweep': sweep, 'tick': tick,
    'tone': tone, 'buzz': buzz, 'step': step, 'riser': riser, 'glitch': glitch, 'thud': thud,
    'chime': chime, 'whip': whip,
}


def render(kind, sr=SR, **params):
    """Сгенерировать звук вида kind. Лишние параметры, которых вид не знает, игнорируются."""
    if kind not in KINDS:
        raise ValueError(f'неизвестный вид SFX: {kind}; есть {", ".join(KINDS)}')
    fn = KINDS[kind]
    names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    kw = {k: v for k, v in params.items() if k in names and v is not None}
    x = np.asarray(fn(sr=sr, **kw), dtype=np.float64)
    peak = np.abs(x).max() if len(x) else 0.0
    if peak > 1.0:
        x = x / peak * 0.99
    return x.astype(np.float32)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Процедурные SFX на numpy.')
    ap.add_argument('kind', nargs='?', help='вид звука (см. --list)')
    ap.add_argument('--list', action='store_true', help='показать виды и выйти')
    ap.add_argument('--out', help='куда писать WAV')
    ap.add_argument('--sr', type=int, default=SR)
    for p, t in (('length', float), ('seed', int), ('freq', float), ('decay', float), ('weight', float),
                 ('f0', float), ('f1', float)):
        ap.add_argument('--' + p, type=t)
    a = ap.parse_args(argv)
    if a.list or not a.kind:
        for k, fn in KINDS.items():
            names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
            print(f'{k:8s} параметры: {", ".join(n for n in names if n != "sr")}')
        return 0
    if not a.out:
        ap.error('нужен --out')
    import soundfile as sf
    x = render(a.kind, sr=a.sr, length=a.length, seed=a.seed, freq=a.freq, decay=a.decay,
               weight=a.weight, f0=a.f0, f1=a.f1)
    sf.write(a.out, x, a.sr, subtype='PCM_24')
    print(f'{a.kind}: {len(x) / a.sr:.3f} с → {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
