[English version](landscape.en.md)

# Соседи по теме

Открытые проекты, которые решают похожие задачи. Это не рейтинг и не реклама, а карта: что уже есть, под какой
лицензией и в чём отличие от этого набора. Сверено 2026-10-23. Знаешь соседа, которого здесь нет? Добавь строку через PR.

## Видео силами агента

| Проект | Лицензия | Что это | Отличие от этого набора |
|---|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Apache-2.0 | HTML → видео для агентов, реестр блоков | движок; мы на нём собираем и описываем приёмы поверх |
| [browser-use/video-use](https://github.com/browser-use/video-use) | MIT | монтаж готового футажа агентом | работает с отснятым материалом, мы чаще собираем кадр с нуля |
| [nateherkai/herk-edit-kit](https://github.com/nateherkai/herk-edit-kit) | MIT, кроме ассетов бренда автора | кит монтажа рилсов на HyperFrames | англоязычный, привязан к бренду автора |
| [latent-spaces/brag](https://github.com/latent-spaces/brag) | MIT | ролик-запуск проекта одним скиллом | узкий формат: 20-секундный промо |
| [nexu-io/html-video](https://github.com/nexu-io/html-video) | Apache-2.0 | программное видео HTML → MP4, шаблоны | шаблоны без метрик роликов |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | AGPL-3.0 | агентное видеопроизводство, 12 пайплайнов | код не берём из-за AGPL |
| [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | MIT | тема → готовый шортс одной кнопкой | фабрика «тема → сток → TTS»; мы как раз считаем это источником слопа |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | Unlicense | вырезание пауз | одна операция, хорошо дополняет |
| [mifi/editly](https://github.com/mifi/editly) | MIT | декларативный монтаж JSON → видео | без приёмов и QA |
| [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas) | MIT | анимации кодом на TS | движок |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Remotion License, не OSI | видео на React | лицензия ограничивает компании больше 3 человек |

## Текст

| Проект | Лицензия | Что это | Отличие |
|---|---|---|---|
| [ilyautov/humanizer-ru](https://github.com/ilyautov/humanizer-ru) | MIT | редактура русского текста для агентов, сканер, eval | наш соседний проект, подключается ссылкой |
| [blader/humanizer](https://github.com/blader/humanizer) | MIT | англоязычный хуманайзер по гайду Википедии | английский |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | MIT | скилл + детектор + фикстуры | английский; образцовая организация вкладов |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | MIT | один SKILL.md со штампами | английский |

## Карусели и презентации

| Проект | Лицензия | Что это | Отличие |
|---|---|---|---|
| [slidevjs/slidev](https://github.com/slidevjs/slidev) | MIT | слайды из Markdown | полноценный фреймворк; у нас один HTML-файл без сборки |
| [marp-team/marp-cli](https://github.com/marp-team/marp-cli) | MIT | Markdown → PDF/PPTX/PNG | хорошо для деков, без гейтов текста |
| [presenton/presenton](https://github.com/presenton/presenton) | Apache-2.0 | открытая альтернатива Gamma | сервис с UI |
| [vercel/satori](https://github.com/vercel/satori) | MPL-2.0 | HTML/CSS → SVG для карточек | библиотека-рендерер |
| [Hainrixz/open-carrusel](https://github.com/Hainrixz/open-carrusel) | MIT | карусели Instagram через чат с Claude | без проверок текста до рендера |

## Голос

| Проект | Лицензия | Заметка |
|---|---|---|
| [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | код MIT, веса CC BY-NC | основа наших граблей TTS |
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | Apache-2.0 | лёгкий TTS без NC-ограничения, русский не проверяли |

## Чего не нашли нигде

- русскоязычного набора «видео агентом»;
- репозитория, который публикует реальные просмотры своих роликов, включая провалы;
- каталога граблей русского TTS и ASR.

Это и есть место этого набора.
