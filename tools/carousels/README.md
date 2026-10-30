<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 not-a-blogger contributors. -->
# carousels: карточки 1080×1350, PDF-методичка, нарезка в карусель

Три CLI на одном стеке Python + WeasyPrint + poppler (pdftoppm, pdfinfo, pdftotext):

| Файл | Вход | Выход |
|---|---|---|
| `cards.py` | JSON с карточками | `pack.pdf` + PNG 1080×1350 на каждую карточку |
| `longread.py` | Markdown со вставками-выносками | PDF A4 (обложка, страница на каждый H2, SVG-инфографика) |
| `slice.py` | любой PDF | PNG 1080×1350: страницы вписаны в холст цвета страницы |
| `infographics.py` | модуль | SVG-схемы `flow`, `bars`, `numbers`, которые WeasyPrint рисует без потерь |

Контент отделён от вида: текст в JSON или Markdown, вид в одном CSS-файле темы (`themes/*.css`, переменные в
`:root`). Новая тема = копия `paper.css` с другими токенами. Есть `paper` (тёплая бумага), `night` (графит), `plain`.

## Установка

```bash
pip install -r tools/carousels/requirements.txt
brew install poppler            # Linux: apt install poppler-utils
```

WeasyPrint на macOS и Linux тянет системные Pango и HarfBuzz, см. его документацию по установке.

**Шрифты.** Файлы шрифтов в репозитории нет. Темы зовут их по имени с фолбэком: `'Inter', 'Noto Sans', sans-serif`
для текста и `'PT Serif', 'Noto Serif', serif` для заголовков. Все под SIL Open Font License. Поставь в систему
полные файлы (не сабсеты):
- Inter: https://rsms.me/inter/ или https://fonts.google.com/specimen/Inter
- Noto Sans и Noto Serif: https://fonts.google.com/noto
- PT Serif: https://fonts.google.com/specimen/PT+Serif

Не установлены: WeasyPrint возьмёт системный sans-serif, кириллица останется читаемой, но вид будет другой.

## Карточки

```bash
cd tools/carousels
python3 cards.py examples/coffee-turka.json --check-only          # только гейты
python3 cards.py examples/coffee-turka.json --theme paper --out out/coffee
python3 cards.py examples/coffee-turka.json --theme night --out out/coffee-night --logo my-logo.png
```

Формат входа (`examples/coffee-turka.json`):

```json
{"theme": "paper", "footer": "Кофейные заметки", "swipe": "листай →", "ban_words": ["лайфхак"],
 "cards": [{"name": "card-01-cover", "label": "Кофе дома", "num": "1 / 5", "body": "<div class=\"giant\">3</div>...", "last": false}]}
```

`body` пишется HTML из классов компонентов. Картинки (`<img src="assets/photo.png">`) ищутся относительно папки
JSON-файла; если какая-то не загрузилась, рендер останавливается с кодом 2, а не выходит с пустым местом.

| Класс | Что это |
|---|---|
| `.giant` + `.gianttag` | гигантское число для обложки и подпись к нему |
| `.phrase` | фраза-герой ~150 px, строки через `<br>` |
| `.h1`, `.lead` | заголовок и подзаголовок |
| `.accent`, `.accent2` | цветной `span` внутри текста |
| `.bignum-grid` > `.bignum` > `.n` + `.cap` | сетка чисел в панелях |
| `.check` > `.item` | список с галочками |
| `.chip`, `.note` | пилюля-источник, мелкая приписка |
| `.panel` (+ `.bad` / `.good`) | панель, с красной или зелёной границей слева |

Структура пака, которая работает: обложка (число или фраза) → что произошло → цифры → контрпозиция → что делать.
Разбор по осям: обложка + 4–8 карточек + финал.

### Гейты

До рендера, жёсткие (код возврата 1, PNG не создаются):
- 0 длинных тире `—`;
- номер «N / M» совпадает с позицией и числом карточек;
- нет «не просто X, а Y» и «не только X, но и Y»;
- нет глифов, которые станут квадратами: `⏵ ⏴ ⏶ ⏷`, U+FFFD, символы private use. Для маркеров бери `→ ✓`;
- последняя карточка помечена `"last": true` (на ней нет «листай»);
- нет слов из `ban_words`.
- у двух карточек не совпадают итоговые имена PNG (без учёта регистра: на macOS `Card` и `card` — один файл).

После рендера: `pdfinfo` по каждой странице, ожидается 810×1012.5 pt. Не совпало: код возврата 2.

## Статья → PDF → карусель

```bash
python3 longread.py examples/coffee-turka.md --theme paper --out out/longread
python3 slice.py out/longread/coffee-turka.pdf --out out/longread-slides
# своя обложка 4:5 первым слайдом вместо A4-обложки
python3 slice.py out/longread/coffee-turka.pdf --out out/slides --cover art.png --skip-first
```

Вставки в Markdown: `:::callout Заголовок`, `:::caveat`, `:::good`, `:::bad`, `:::numbers` (строки «число | подпись»),
`:::bars Заголовок` (строки «подпись | число»), `:::flow` (строка на шаг), закрываются строкой `:::`. Цитата `>` идёт
выделенным абзацем. Front matter: `title`, `kicker`, `subtitle`, `footer`, `cover` (AI-фон без текста; заголовок
кладётся поверх CSS-слоем). `longread.py` прогоняет те же текстовые гейты, затем проверяет, что каждая страница A4
(595×842 pt) и в `pdftotext` нет ни одного `—`.

## Грабли

- **pdftoppm только с `-r 96`.** WeasyPrint пишет 1 px как 0,75 pt, страница 1080×1350 px = 810×1012,5 pt. С `-r 72`
  PNG выходят 810×1013. Рецепт: `recipes/carousels/carousels-pdftoppm-96dpi.md`. Тест `test_render_one_card_png_1080x1350`
  проверяет размер PNG.
- **`@page` пропадает от склейки строк.** `CSS = "X" + """...""".replace("X", faces)`: `.replace` цепляется только к
  тройной строке, литерал остаётся в начале CSS, парсер съедает вместе с ним правило `@page`, и страница уезжает в A4,
  макет обрезается справа. Склеивай `faces + css` или бери выражение в скобки. Поэтому `pdfinfo` после каждого рендера
  (`recipes/carousels/carousels-pdfinfo-page-size.md`).
- **Шрифты.** Google Fonts через `@import` при рендере тянется по сети и может повиснуть на десятки секунд. Сабсеты
  (только latin или только cyrillic) дают квадраты на цифрах и латинице. Ставь полные файлы в систему, см. выше
  (`recipes/carousels/carousels-local-full-fonts.md`).
- **Фон страницы PDF** задаётся в `@page { background }`. Фон на `html`/`body` не доходит до полей, края выйдут белыми.
  Проверка: пиксель угла `(6, 6)` у PNG страницы.
- **Выноски рвутся через страницу.** На всех блоках стоит `break-inside: avoid`; бюджет текста на страницу закладывай
  сразу, H2 = одна тема = одна страница.
- **Длинное тире прячется в подписях SVG** и в разделителях, которые генерирует код. Гейт по `pdftotext` ловит и их.
- **SVG для WeasyPrint:** только rect, circle, path, line, polygon, text и градиенты. `filter`, `mask` и тени через CSS он
  не рисует; тень делается вторым прямоугольником со сдвигом. `backdrop-filter: blur()` тоже нет: глубину дают пятна
  (`.blob`) и полупрозрачные панели.
- **Номера страниц pdftoppm** добиваются нулями по числу страниц (`p-1.png` или `p-01.png`). `slice.py` сортирует по
  числу, а `cards.py` вызывает pdftoppm на каждую страницу с `-singlefile`.
- **Обложка:** генератор картинок рисует только фон, буквы кладёт код (`tools/covers/overlay.py`). Текст в модели
  выходит с опечатками.
- **Зелёные гейты не заменяют глаз.** Открой обложку и 2–3 плотные карточки: кириллица без квадратов, числа не обрезаны,
  нумерация совпадает, контраст.
