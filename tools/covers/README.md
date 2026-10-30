<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 not-a-blogger contributors. -->
# covers: обложки, где AI рисует фон, а текст кладёт код

Два CLI:

| Файл | Что делает | Стек |
|---|---|---|
| `overlay.py` | кладёт надзаголовок, заголовок, подзаголовок и подпись поверх готового AI-арта, со скримом под текст | Pillow |
| `cover.py` | векторная обложка без AI: иконка-метафора + число или фраза + 2–3 строки; SVG и PNG | cairosvg |

Палитра приходит из CSS-темы `themes/*.css` (переменные в `:root`): `dark` (светлый текст на тёмном скриме, янтарный
акцент) и `paper` (графит на бумажном скриме, сине-зелёный акцент). Своя тема = копия файла с другими цветами.

## Установка

```bash
pip install -r tools/covers/requirements.txt
```

cairosvg нужен системный cairo (`brew install cairo`, `apt install libcairo2`). Без cairosvg `cover.py` пишет только SVG.

**Шрифты.** Файлы в репозитории нет. `fonts.py` ищет по имени установленный Inter, затем Noto Sans (оба SIL Open Font
License), затем системный sans через `fc-match`. Свой файл: `overlay.py --font путь.ttf`, своё семейство:
`cover.py --font-family "Noto Sans"`. Скачать: https://rsms.me/inter/, https://fonts.google.com/noto/specimen/Noto+Sans.

## Обложка поверх AI-арта

1. Сгенерируй фон. Пример промпта: `examples/art-prompt.txt`. В промпте прямо: без текста, букв, цифр, логотипов, и где
   оставить спокойную зону под заголовок.
2. Положи текст:

```bash
cd tools/covers
python3 overlay.py --demo-bg demo.png                       # заглушка, если арта пока нет
python3 overlay.py demo.png out/cover.png --spec examples/coffee-cover.json
python3 overlay.py art.png out/link.png --spec examples/coffee-cover.json --size 1200x630 --pos bottom --theme paper
```

Поля `examples/coffee-cover.json`: `eyebrow`, `h1`, `h2` (акцентом), `sub` (список строк), `footer`, `pos` (`top` или
`bottom`), `theme`, `size`. Арт кадрируется по центру под размер, строки переносятся по ширине. Выбирай `pos` так,
чтобы текст не лёг на главный объект арта.

## Векторная обложка

```bash
python3 cover.py --list-icons
python3 cover.py examples/coffee-covers.json --out out/covers
python3 cover.py examples/coffee-covers.json --theme dark --out out/covers-dark
```

Обложка = строка в `covers`: `file`, `eyebrow`, `icon` (`cup`, `clock`, `eye`, `bill`, `shield`, `chart`, `search`,
`route`, `power`, `folder`), `badge` (1–3 символа или `✓`, по умолчанию без бейджа), `hero` (`number` + `tag` или
`line1` + `line2`), `sub`, `footer`. Новая иконка = функция `icon_<имя>(c, badge=None)` в `cover.py`, рисует в
координатах с центром (0, 0) и радиусом около 150 px, цвета берёт из `c`.

## Гейты

Оба скрипта отказываются рендерить (код 1), если в тексте есть длинное тире `—`; `overlay.py` ещё ловит «не просто X,
а Y», `cover.py` неизвестную иконку, бейдж длиннее трёх символов и два `file`, которые дают одно имя файла (`a/b` и `a b`,
`Cover` и `cover` на регистронезависимой ФС macOS/Windows, две обложки без `file`): иначе вторая молча перезаписала бы
первую.

## Грабли

- **Модель не рисует буквы.** Текст из генератора картинок выходит с опечатками и «почти кириллицей». Фон отдельно,
  текст кодом (`recipes/carousels/carousels-cover-ai-background-only.md`).
- **Зашитое число на иконке переезжает в следующий пост.** Иконка с бейджем «8x» скопировалась в другую обложку и
  подписала её чужой цифрой. Поэтому бейдж только параметр конкретной обложки, в иконке текста нет.
- **cairosvg не понимает список шрифтов.** `font-family="Inter, sans-serif"` он передаёт cairo целиком, тот не находит
  такое имя и молча берёт шрифт по умолчанию без жирности. `cover.py` подставляет одно установленное имя.
- **Скрим под текстом обязателен.** Без него заголовок теряется на пёстром арте. На светлой гравюре тёмный скрим убивает
  арт: бери тему `paper`.
- **Встроенный шрифт Pillow без кириллицы.** Если в системе нет ни Inter, ни Noto Sans, ни системного sans, будут квадраты;
  скрипт пишет об этом в stderr. Ставь шрифт.
- **Смотри результат глазами** на телефонном размере: заголовок читается в превью ленты, текст не лёг на лицо или предмет.
