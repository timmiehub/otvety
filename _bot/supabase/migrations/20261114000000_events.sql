-- Статистика бота «Ответы». Telegram user_id не храним — только хеш с солью.
create table public.events (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  type        text not null check (type in ('inline_query', 'chosen', 'start', 'dm')),
  answer_slug text,
  query_text  text check (char_length(query_text) <= 64),
  user_hash   text
);
create index events_type_created_idx on public.events (type, created_at desc);

-- Пишет только бот (service role). Снаружи таблица закрыта.
alter table public.events enable row level security;
revoke all on public.events from anon, authenticated;

-- Отправки по дням (по Москве). sends = выбрал ответ в inline + получил карточку в личке.
create view public.stats_daily with (security_invoker = true) as
select (created_at at time zone 'Europe/Moscow')::date                         as day,
       count(*) filter (where type in ('chosen', 'dm'))                         as sends,
       count(distinct user_hash) filter (where type in ('chosen', 'dm'))        as senders,
       count(*) filter (where type = 'inline_query')                            as queries,
       count(*) filter (where type = 'start')                                   as starts
from public.events
group by 1
order by 1 desc;

-- Топ ответов за всё время.
create view public.stats_top with (security_invoker = true) as
select answer_slug,
       count(*)                  as sends,
       count(distinct user_hash) as users,
       max(created_at)           as last_sent
from public.events
where type in ('chosen', 'dm') and answer_slug is not null
group by 1
order by 2 desc;

revoke all on public.stats_daily, public.stats_top from anon, authenticated;
