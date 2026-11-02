# Security

[Русская версия ниже](#безопасность)

not-a-blogger is a local toolkit: scripts, templates and recipes that run on your machine. There is no hosted
service, no accounts and no telemetry. Publishing to platforms is deliberately not part of the kit.

## What to report

- a script that can execute code it shouldn't, overwrite files outside the project, or follow a path out of it;
- a dependency pinned at a version with a known vulnerability (`requirements*.txt`, `package-lock.json`);
- a secret, token, personal path or private data that slipped into the repository;
- a recipe that tells an agent to do something unsafe (disable checks, publish without approval, scrape behind a
  login).

## How to report

Use GitHub's private vulnerability reporting (Security → Advisories → Report a vulnerability) **if enabled**; otherwise write
to ilyautov@gmail.com. This email is the fallback while the repository is private or the reporting form is unavailable.
Please don't open a public issue for a vulnerability. Expect a reply within 7 days. Fixes go to `main`; there are
no maintained release branches.

CI runs `scripts/privacy_check.sh` (personal paths, tokens, private handles) on every push, and contributors run it
before a PR. That is a safety net, not a guarantee.

## Безопасность

not-a-blogger работает локально: скрипты, шаблоны и рецепты запускаются на твоей машине. Сервиса, аккаунтов и
телеметрии нет. Публикация на площадки в набор намеренно не входит.

Сообщай, если скрипт может выполнить лишний код, перезаписать файлы вне проекта или выйти за его пределы по пути;
если зависимость закреплена на версии с известной уязвимостью; если в репо попал секрет, токен, личный путь или
чужие данные; если рецепт велит агенту делать небезопасное (отключать проверки, публиковать без одобрения, собирать
данные из-под логина).

Если включены приватные отчёты GitHub, используй Security → Advisories → Report a vulnerability; иначе пиши на
ilyautov@gmail.com. Почта работает как запасной путь, пока репозиторий приватный или форма недоступна. Не пиши
об уязвимости в публичный issue. Ответ в течение 7 дней.
