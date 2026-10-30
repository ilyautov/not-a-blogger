#!/usr/bin/env python3
"""Блок атрибуции для описания ролика из списка использованных файлов, с проверкой лицензий.

Что делает: читает JSON со списком ассетов (музыка, фото, футаж, шрифты, иконки), нормализует
лицензию и печатает блок «Credits» для описания: текст (по умолчанию) или Markdown (--format md).
Проверяет каждую запись:
  • ошибка: лицензии нет вовсе или она не из списка известных открытых (CC0, Public Domain,
    CC BY, CC BY-SA, MIT, Apache-2.0, BSD, SIL OFL, Pixabay, Pexels, Unsplash);
  • ошибка: у CC BY и CC BY-SA нет автора (атрибуция без имени не выполняет лицензию);
  • предупреждение: NC (CC BY-NC, -NC-SA, -NC-ND) — только для некоммерческих роликов;
    с --commercial это ошибка. Коммерческое = реклама, монетизация, заказ (см. docs/THIRD-PARTY.md);
  • предупреждение: ND (без переработок) — нарезка или подложка под голос может считаться переработкой.
Список не юридическая консультация: открой текст лицензии сам, если ролик приносит деньги.

Вход: [{"file": "music/track.mp3", "title": "Track", "author": "Artist", "source_url": "https://…",
        "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/"}, ...]
  или {"assets": [...]}. Обязательно только "license" (или "license_url" на creativecommons.org).
Выход: блок атрибуции в stdout, проблемы в stderr; с --json — JSON-отчёт в stdout.
Код возврата: 0, если ошибок нет (предупреждения не валят); иначе 1.

Пример:
  python3 tools/publish-prep/credits.py assets.json
  python3 tools/publish-prep/credits.py assets.json --format md --commercial
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

OPEN = {'CC0': 'CC0', 'PD': 'Public Domain', 'MIT': 'MIT', 'APACHE-2.0': 'Apache-2.0', 'BSD': 'BSD',
        'OFL': 'SIL OFL', 'PIXABAY': 'Pixabay License', 'PEXELS': 'Pexels License', 'UNSPLASH': 'Unsplash License'}
ALIASES = {
    'CC0': 'CC0', 'CC0 1.0': 'CC0', 'CC-0': 'CC0', 'CC ZERO': 'CC0',
    'PD': 'PD', 'PUBLIC DOMAIN': 'PD', 'PDM': 'PD', 'PUBLIC DOMAIN MARK': 'PD', 'PUBLICDOMAIN': 'PD',
    'MIT': 'MIT', 'APACHE-2.0': 'APACHE-2.0', 'APACHE 2.0': 'APACHE-2.0', 'APACHE': 'APACHE-2.0',
    'BSD': 'BSD', 'BSD-2-CLAUSE': 'BSD', 'BSD-3-CLAUSE': 'BSD', 'BSD-2': 'BSD', 'BSD-3': 'BSD',
    'OFL': 'OFL', 'OFL-1.1': 'OFL', 'SIL OFL': 'OFL', 'SIL OFL 1.1': 'OFL',
    'PIXABAY': 'PIXABAY', 'PIXABAY LICENSE': 'PIXABAY', 'PIXABAY CONTENT LICENSE': 'PIXABAY',
    'PEXELS': 'PEXELS', 'PEXELS LICENSE': 'PEXELS', 'UNSPLASH': 'UNSPLASH', 'UNSPLASH LICENSE': 'UNSPLASH',
}
CC = re.compile(r'^CC[\s-]*BY((?:[\s-]+(?:NC|SA|ND))*)(?:[\s-]+(\d\.\d))?(?:[\s-]+INTERNATIONAL)?$')
CC_HOSTS = {'creativecommons.org', 'www.creativecommons.org'}
CC_PATH = re.compile(r'^/(?:licenses/([a-z-]+)/(\d\.\d)|publicdomain/(zero|mark)/\d\.\d)(?:/[a-z._-]*)*/?$', re.I)


def cc_url(url):
    """Адрес лицензии CC → match пути или None. Точный хост creativecommons.org и путь лицензии:
    notcreativecommons.org или CC-адрес в query чужого сайта лицензией не считаются."""
    try:
        u = urlparse((url or '').strip())
        host = (u.hostname or '').lower().rstrip('.')
    except ValueError:
        return None
    if u.scheme.lower() not in ('http', 'https') or host not in CC_HOSTS:
        return None
    return CC_PATH.match(u.path)


def normalize(license_name, license_url=''):
    """Лицензия → {'id', 'label', 'nc', 'nd', 'by'} или None, если не распознана."""
    raw = (license_name or '').strip()
    if not raw and license_url:
        m = cc_url(license_url)
        if m:
            raw = {'zero': 'CC0', 'mark': 'PD'}[m.group(3)] if m.group(3) else f'CC {m.group(1)} {m.group(2)}'
    key = re.sub(r'\s+', ' ', raw.upper().replace('_', ' ')).strip()
    if not key:
        return None
    m = CC.match(key)
    if m:
        mods = re.findall(r'NC|SA|ND', m.group(1))
        if 'SA' in mods and 'ND' in mods:
            return None
        order = [x for x in ('NC', 'SA', 'ND') if x in mods]
        cid = 'CC BY' + ''.join('-' + x for x in order)
        label = cid + (f' {m.group(2)}' if m.group(2) else '')
        return {'id': cid, 'label': label, 'nc': 'NC' in mods, 'nd': 'ND' in mods, 'by': True}
    k = ALIASES.get(key) or ALIASES.get(key.removesuffix(' LICENSE'))
    if k:
        return {'id': k, 'label': OPEN[k], 'nc': False, 'nd': False, 'by': False}
    return None


def load_assets(data):
    items = data.get('assets') if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError('ожидал JSON-список ассетов или {"assets": [...]}')
    return items


def check(assets, commercial=False):
    """Вернуть (записи с нормализованной лицензией, ошибки, предупреждения)."""
    rows, errors, warnings = [], [], []
    for i, a in enumerate(assets):
        name = a.get('file') or a.get('title') or a.get('source_url') or f'#{i + 1}'
        lic = normalize(a.get('license', ''), a.get('license_url', ''))
        if not (a.get('license') or a.get('license_url')):
            errors.append(f'{name}: нет лицензии')
        elif lic is None:
            errors.append(f'{name}: лицензия «{a.get("license") or a.get("license_url")}» не из списка открытых')
        else:
            if lic['nc']:
                (errors if commercial else warnings).append(
                    f'{name}: {lic["label"]} — только некоммерческое использование'
                    + (' (--commercial)' if commercial else ''))
            if lic['nd']:
                warnings.append(f'{name}: {lic["label"]} — без переработок; нарезка и подложка могут ими считаться')
            if lic['by'] and not a.get('author'):
                errors.append(f'{name}: {lic["label"]} требует автора, поле "author" пустое')
        rows.append({**a, 'name': name, 'license_label': lic['label'] if lic else (a.get('license') or None)})
    return rows, errors, warnings


def credit_line(r, fmt='text'):
    title = r.get('title') or Path(str(r.get('file') or r['name'])).stem
    author = r.get('author')
    src, lic, lurl = r.get('source_url'), r['license_label'], r.get('license_url')
    if fmt == 'md':
        head = f'[{title}]({src})' if src else title
        lic_s = f'[{lic}]({lurl})' if lurl else lic
        return f'- {head}' + (f' — {author}' if author else '') + f', {lic_s}'
    s = title + (f' — {author}' if author else '') + f', {lic}'
    if src:
        s += f', {src}'
    if lurl:
        s += f' ({lurl})'
    return s


def render(rows, fmt='text'):
    if not rows:
        return ''
    head = '## Credits' if fmt == 'md' else 'Credits:'
    return '\n'.join([head, *(credit_line(r, fmt) for r in rows)]) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Атрибуция для описания ролика из JSON ассетов; провал на неизвестной лицензии.')
    ap.add_argument('assets', help='JSON: список {file, title, author, source_url, license, license_url}')
    ap.add_argument('--format', choices=['text', 'md'], default='text', help='текст для описания или Markdown')
    ap.add_argument('--commercial', action='store_true', help='ролик коммерческий: NC-лицензии = ошибка')
    ap.add_argument('--json', action='store_true', help='JSON-отчёт вместо блока')
    a = ap.parse_args(argv)
    rows, errors, warnings = check(load_assets(json.loads(Path(a.assets).read_text(encoding='utf-8'))), a.commercial)
    ok = not errors
    if a.json:
        print(json.dumps({'file': Path(a.assets).name, 'assets': len(rows), 'commercial': a.commercial,
                          'errors': errors, 'warnings': warnings, 'credits': render(rows, a.format), 'pass': ok},
                         ensure_ascii=False))
    else:
        sys.stdout.write(render(rows, a.format))
        for w in warnings:
            print('ПРЕДУПРЕЖДЕНИЕ:', w, file=sys.stderr)
        for e in errors:
            print('ОШИБКА:', e, file=sys.stderr)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
