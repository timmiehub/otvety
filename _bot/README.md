# Бот «Ответы»

Supabase-проект **otvety** (`octsacjesrnqzodzjsqg`, Франкфурт). Функция `otvety-bot`, вебхук Telegram.

## Как устроено
- `supabase/functions/otvety-bot/index.ts` — бот. Чистый Bot API без библиотек: ответ отдаётся прямо в теле вебхука, без лишнего запроса.
- `search.ts` — поиск по слову и синонимам; тест: `node search.test.ts` (Node 22.18+).
- `answers.json` — копия списка, вшитая в функцию. Основной список бот берёт с сайта (`BASE_URL/answers.json`, кеш 10 минут), так что **новый ответ появляется в боте после git push, без передеплоя**.
- Сообщение в чат — ссылка на лендинг ответа; Telegram рисует большое превью из `og.png`. В списке `@бот` — иконки `thumb.jpg`.
- `supabase/migrations/` — таблица `events` и отчёты `stats_daily`, `stats_top`.

## Секреты (Supabase → Edge Functions → Secrets)
- `BOT_TOKEN` — от @BotFather. Это единственный обязательный секрет.
- `BASE_URL` — необязательно, по умолчанию `https://otvety.nerdstudio.dev/`.
- `WEBHOOK_SECRET` больше не нужен (можно удалить): секрет вебхука и соль для хеша пользователей выводятся из токена.
  Смена токена → новый секрет вебхука (ставится сам) и новая соль (счётчик «уникальных» начнётся заново).

## Вебхук и проверка
Бот ставит вебхук сам при каждом холодном старте. Состояние — открыть
`https://octsacjesrnqzodzjsqg.supabase.co/functions/v1/otvety-bot`:
`webhook_set: true`, `last_error: null`, `db: ok`.

## Добавить ответ
1. Дописать объект в `_project/answers.json` (slug, word, dot, цвета, тексты, `keywords`, `top`).
2. `python _project/gen.py` (с `BASE_URL=https://otvety.nerdstudio.dev/`), затем `python _project/og.py` (переменная `FONTS`).
3. git push. Если менялся `search.ts`/`index.ts` — передеплоить функцию.

## Метки источников
Ссылка `t.me/vototvet_app?start=<метка>`: `a_<slug>` — кнопка под карточкой, `w_<slug>` — лендинг ответа,
`w_hub` — главная, `r_<код>` — ролик (код латиницей, до 20 символов). Метка пишется в `events.query_text` у события `start`.

## Статистика (SQL Editor)
```sql
select * from stats_daily limit 14;   -- отправки, отправители, запросы, /start по дням
select * from stats_top;              -- топ ответов
select * from stats_sources;          -- откуда пришли в бота: карточка в чате / лендинг / главная / ролик
```
