#!/usr/bin/env python3
"""Статический линт движения для GSAP-сцены (scene.js), написанной агентом или руками.

Что делает: читает исходник и проверяет минимумы, без которых анимация выглядит как слайды:
  ≥4 семейства ease, среди них спокойное (sine/power1) и резкое (power4/expo/springEase);
  разброс длительностей (коэффициент вариации ≥ 0,35); движение по двум осям; ≥5 видов
  свойств; stagger у групп; камера (твины на селектор камеры, по умолчанию #world) ≥ 2;
  хотя бы одна пружина или перелёт (springEase, back., elastic.); хотя бы один признак глубины
  (blur, rotationX/Y, perspective); число разных моментов старта ≥ длительность / 2,5;
  запрет Math.random/Date.now (рендер должен быть детерминированным) и твинов width/height/top/left.
Вкус линт не оценивает. Он только отсекает плоскую «карточку с fade».
Для Canvas-сцен (как scene.ts в стартере) неприменим: там нет GSAP-твинов.

Вход: путь к scene.js и длительность (--duration или --story story.json с полем duration).
Выход: краткий JSON в stdout и полный отчёт в --out (по умолчанию не пишется).
Код возврата: 0, если все проверки пройдены, иначе 1.

Пример:
  python3 tools/lint/motion_lint.py scene.js --duration 30
  python3 tools/lint/motion_lint.py scene.js --story story.json --camera "#cam" --out qa/motion-lint.json
"""
import argparse
import json
import re
import sys
from pathlib import Path


def analyse(source, duration, camera='#world'):
    eases = re.findall(r"""ease\s*:\s*(?:['"]([^'"]+)['"]|(springEase\([^)]*\)))""", source)
    ease_names = [a or 'springEase' for a, b in eases]
    families = set()
    for e in ease_names:
        m = re.match(r'(power\d|sine|expo|circ|back|elastic|bounce|none|steps|springEase)', e)
        families.add(m.group(1) if m else e)
    durations = [float(d) for d in re.findall(r'duration\s*:\s*([0-9.]+)', source)]
    mean = sum(durations) / len(durations) if durations else 0
    cv = (sum((d - mean) ** 2 for d in durations) / len(durations)) ** .5 / mean if durations and mean else 0
    props = set(re.findall(r'\b(x|y|xPercent|yPercent|scale|scaleX|scaleY|rotation|rotationX|rotationY|opacity|filter|'
                           r'clipPath|strokeDashoffset|backgroundPosition|letterSpacing)\s*:', source))
    # разные моменты старта на таймлайне: числа или выражения от констант (T.b2+.3, AT[i], at+.5)
    starts = set(m.strip() for m in re.findall(
        r'\}\s*,\s*([A-Za-z_$][\w.$\[\]]*(?:\s*[+-]\s*[0-9.]+)?|[0-9.]+)\s*\)', source))
    cam = re.escape(camera.lstrip('#.'))
    camera_tweens = len(re.findall(r"""['"]\s*[#.]""" + cam + r"""\s*['"]""", source))
    calm = families & {'sine', 'power1'}
    punch = families & {'power4', 'expo', 'springEase'}
    report = {
        'ease_names': sorted(set(ease_names)),
        'ease_families': sorted(families),
        'duration_cv': round(cv, 2),
        'properties': sorted(props),
        'distinct_beats': len(starts),
        'camera_tweens': camera_tweens,
        'stagger': bool(re.search(r'stagger\s*:', source)) or bool(re.search(r'\*\s*STAGGER|i\s*\*\s*0?\.\d+', source)),
        'spring_or_overshoot': bool(re.search(r'springEase\(|back\.|elastic\.', source)),
        'blur_or_depth': bool(re.search(r'blur\(|stdDeviation|--dof|rotationY|rotationX|perspective', source)),
        'forbidden_random': bool(re.search(r'Math\.random|Date\.now', source)),
        'forbidden_layout_tweens': bool(re.search(r'\b(width|height|top|left)\s*:\s*[^,}]+\s*,\s*duration', source)),
    }
    checks = {
        'ease_families>=4': len(families) >= 4,
        'has_calm_ease': bool(calm),
        'has_punch_ease': bool(punch),
        'duration_cv>=0.35': cv >= .35,
        'movement_axes>=2': len(props & {'x', 'y', 'xPercent', 'yPercent'}) >= 2,
        'property_kinds>=5': len(props) >= 5,
        'stagger': report['stagger'],
        'camera_tweens>=2': camera_tweens >= 2,
        'spring_or_overshoot': report['spring_or_overshoot'],
        'blur_or_depth': report['blur_or_depth'],
        'beats>=duration/2.5': len(starts) >= duration / 2.5,
        'no_random_or_clock': not report['forbidden_random'],
        'no_layout_tweens': not report['forbidden_layout_tweens'],
    }
    return report, checks


def main(argv=None):
    ap = argparse.ArgumentParser(description='Статический линт движения GSAP-сцены.')
    ap.add_argument('scene', type=Path, help='scene.js')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--duration', type=float, help='длительность ролика, с')
    g.add_argument('--story', type=Path, help='JSON с полем duration')
    ap.add_argument('--camera', default='#world', help='селектор камеры (#world)')
    ap.add_argument('--out', type=Path, help='куда записать полный отчёт')
    a = ap.parse_args(argv)
    duration = a.duration if a.duration is not None else float(json.loads(a.story.read_text())['duration'])
    report, checks = analyse(a.scene.read_text(encoding='utf-8'), duration, a.camera)
    out = {'ok': all(checks.values()), 'checks': checks, 'report': report}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'ok': out['ok'], 'failed': [k for k, v in checks.items() if not v]}, ensure_ascii=False))
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
