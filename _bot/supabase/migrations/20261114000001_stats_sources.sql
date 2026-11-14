-- Откуда приходят в бота: метка из t.me/<бот>?start=<метка> (пишется в query_text у событий start).
create view public.stats_sources with (security_invoker = true) as
select case
         when query_text like 'a\_%' then 'карточка в чате'
         when query_text = 'w_hub' then 'главная сайта'
         when query_text like 'w\_%' then 'лендинг ответа'
         when query_text like 'r\_%' then 'ролик'
         when query_text is null then 'напрямую'
         else 'другое'
       end as source,
       query_text as label,
       count(*) as starts,
       count(distinct user_hash) as users,
       max(created_at) as last_at
from public.events
where type = 'start'
group by 1, 2
order by 3 desc;
revoke all on public.stats_sources from anon, authenticated;
