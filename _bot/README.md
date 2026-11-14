# Бот «Ответы»

Supabase-проект **otvety** (`octsacjesrnqzodzjsqg`, Франкфурт). Функция `otvety-bot`, вебхук Telegram.

## Как устроено
- `supabase/functions/otvety-bot/index.ts` — бот. Чистый Bot API без библиотек: ответ отдаётся прямо в теле вебхука, без лишнего запроса.
- `search.ts` — поиск по слову и синонимам; тест: `node search.test.ts` (Node 22.18+).
- `answers.json` — копия списка, вшитая в функцию. Основной список бот берёт с сайта (`BASE_URL/answers.json`, кеш 10 минут), так что **новый ответ появляется в боте после git push, без передеплоя**.
- Сообщение в чат — ссылка на лендинг ответа; Telegram рисует большое превью из `og.png`. В списке `@бот` — иконки `thumb.jpg`.
- `supabase/migrations/` — таблица `events` и отчёты `stats_daily`, `stats_top`.

## Секреты (Supabase → Edge Functions → Secrets)
- `BOT_TOKEN` — от @BotFather.
- `WEBHOOK_SECRET` — любая случайная строка (латиница/цифры, 32+ символа). Из неё же выводится соль для хеша пользователей — не меняйте без нужды, иначе статистика «уникальных» начнётся заново.
- `BASE_URL` — необязательно, по умолчанию `https://otvety.nerdstudio.dev/`.

## Первый запуск / после смены токена
Открыть в браузере: `https://octsacjesrnqzodzjsqg.supabase.co/functions/v1/otvety-bot?setup=<WEBHOOK_SECRET>`
Ответ покажет имя бота, результат установки вебхука и `db: ok`.

## Добавить ответ
1. Дописать объект в `_project/answers.json` (slug, word, dot, цвета, тексты, `keywords`, `top`).
2. `python _project/gen.py` (с `BASE_URL=https://otvety.nerdstudio.dev/`), затем `python _project/og.py` (переменная `FONTS`).
3. git push. Если менялся `search.ts`/`index.ts` — передеплоить функцию.

## Статистика (SQL Editor)
```sql
select * from stats_daily limit 14;   -- отправки, отправители, запросы, /start по дням
select * from stats_top;              -- топ ответов
```
