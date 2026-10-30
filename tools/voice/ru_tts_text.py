#!/usr/bin/env python3
"""Подготовка русского текста к синтезу речи (TTS): что модель читает как паузу и что глотает.

Что делает: применяет к реплике набор замен и выдаёт предупреждения о местах, где синтез
обычно ошибается. Правила получены замерами на русском клоне F5-TTS (спокойный референс,
энергетический поиск тишины между словами):
  . ! ?  ≈ 0,43 с паузы   «»  ≈ 0,39 с   :  ≈ 0,30 с   , ; — …  ≈ 0,08 с (то же, что без знака).
То есть тире и многоточие паузы не дают, паузу даёт только конец предложения.
Для других моделей правила стоит перемерить, но предупреждения полезны почти везде.

Замены (порядок важен):
  «: » → «. »                  двоеточие даёт короткую паузу или никакой, точка надёжнее;
  ИИ                           не заменяется, а помечается: «ИИ» сливается в одно долгое «и», «И-И»
                               синтез глотает так же; пишите «нейросеть» в нужном падеже («у нейросети»);
  знак ударения U+0301 → убрать  в тексте для OmniVoice знаки ударения почти на каждом слове дали
                               «лютый акцент» (гипотеза: слепой A/B ещё не прослушан); неверно читаемое
                               слово переформулируйте;
  AI → эй-ай                   латинское AI (OpenAI, X-AI и т. п. не трогаются);
  двойные пробелы → один.

Предупреждения ещё и на «!»: синтез восклицания не играет и иногда уходит в фальцет; держите «!» не
больше чем в ~10 % реплик (сводка по всем строкам печатается в конце).

Вход: строки реплик аргументами, файлом (--file, по строке на реплику) или из stdin.
Выход: подготовленный текст, применённые правила и предупреждения (текстом или --json).
Код возврата: 0; с --strict 1, если есть хотя бы одно предупреждение.

Пример:
  python3 tools/voice/ru_tts_text.py "Отчёт: готов, ИИ-агент вернул 200."
  python3 tools/voice/ru_tts_text.py --file voice/lines.txt --json > qa/tts-text.json
"""
import argparse
import json
import re
import sys

# (шаблон, замена, пояснение) — порядок важен
RULES = [
    (r'\s*:\s+', '. ', 'двоеточие даёт короткую паузу (0,3 с) или никакой → точка (0,43 с)'),
    ('\u0301', '', 'знаки ударения U+0301 убраны: в OmniVoice они дают акцент; слово с неверным ударением переформулируйте'),
    (r'(?<![A-Za-z\-])AI(?![A-Za-z])', 'эй-ай', 'латинское AI → «эй-ай»'),
    (r'[ \t]{2,}', ' ', 'двойные пробелы'),
]


def prepare(text):
    """Вернуть (подготовленный_текст, применённые_правила, предупреждения)."""
    out, notes = text, []
    for pat, rep, note in RULES:
        new = re.sub(pat, rep, out)
        if new != out:
            notes.append(note)
            out = new
    out = out.strip()
    warn = []
    first = re.match(r'[^\wЁё]*([\wЁё]+)', out.replace('+', ''))
    if first and len(first.group(1)) <= 3:
        warn.append(f'короткое первое слово «{first.group(1)}»: синтез может срезать его вместе '
                    'с тишиной в начале; добавьте «Вот …» или переставьте слова')
    if re.search(r'\d', out):
        warn.append('цифры: синтез читает их непредсказуемо, лучше написать словами')
    if re.search(r'(?<![А-Яа-яЁё])ИИ(?![А-Яа-яЁё])', out):
        warn.append('«ИИ»: синтез сливает в долгое «и», «И-И» глотает; напишите «нейросеть» '
                    'в нужном падеже («у нейросети», «агент на нейросети»)')
    if ':' in out:
        warn.append('осталось двоеточие без пробела после него')
    if re.search(r'\s[—…]\s|…', out):
        warn.append('тире/многоточие: паузы на них нет (≈0,08 с); для паузы нужна точка')
    if '!' in out:
        warn.append('«!»: синтез восклицание не играет, иногда даёт фальцет; оставьте «!» в ~10 % реплик')
    return out, notes, warn


def exclamation_share(texts):
    """Доля реплик с «!» (включая «?!»)."""
    texts = [x for x in texts if x.strip()]
    return round(sum('!' in x for x in texts) / len(texts), 2) if texts else 0.0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Подготовка русского текста к TTS.')
    ap.add_argument('lines', nargs='*', help='реплики; без аргументов читается --file или stdin')
    ap.add_argument('--file', help='файл с репликами, по одной на строку')
    ap.add_argument('--json', action='store_true', help='вывод JSON-списком')
    ap.add_argument('--strict', action='store_true', help='код 1, если есть предупреждения')
    a = ap.parse_args(argv)
    if a.lines:
        lines = a.lines
    elif a.file:
        with open(a.file, encoding='utf-8') as f:
            lines = [s.rstrip('\n') for s in f if s.strip()]
    else:
        lines = [s.rstrip('\n') for s in sys.stdin if s.strip()]
    rows = []
    for line in lines:
        t, n, w = prepare(line)
        rows.append({'source': line, 'text': t, 'rules': n, 'warnings': w})
    share = exclamation_share([r['text'] for r in rows])
    if len(rows) >= 3 and share > 0.1:
        print(f'внимание: «!» в {share:.0%} реплик (у одобренных эталонов ~10 %)', file=sys.stderr)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print(r['text'])
            for x in r['rules']:
                print('   правило:', x)
            for x in r['warnings']:
                print('   внимание:', x)
    return 1 if a.strict and any(r['warnings'] for r in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
