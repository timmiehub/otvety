# Генератор страниц. Запуск из корня репо: python3 _project/gen.py
import json, os
BASE="https://timmiehub.github.io/otvety/"
PAGES = [
 dict(slug="da", word="Да", dot=".", a="#b9a4ff", b="#6d4aff", bg="#0b0716",
  badge="Ответ v2.0 уже доступен", tag="Ответ, которому доверяют.",
  cta="Получить «Да»", cta2="Задать вопрос",
  feats=[("Мгновенно","Ноль секунд на раздумья. Собеседник доволен ещё до конца вопроса."),
         ("Без условий","Никаких «да, но…». Чистый продукт без примесей."),
         ("Совместим со всем","Свидания, работа, «ещё по одной». Интеграция из коробки.")],
  stats=[("0 мс","на сомнения"),("100%","уверенности"),("∞","применений")],
  vs=("Может быть",[("Скорость ответа","мгновенно","через неделю"),("Понятность","кристальная","туман"),("Обиды","нет","копятся")]),
  price="Бесплатно. Всегда.", final="Скажи это.", others="Попробуй другие ответы"),
 dict(slug="net", word="Нет", dot=".", a="#ff8a7a", b="#e0262f", bg="#140707",
  badge="Ответ v3.1 · Enterprise Boundaries", tag="Граница, которую уважают.",
  cta="Получить «Нет»", cta2="Попросить ещё раз",
  feats=[("Экономит время","Одно слово вместо трёх часов «ну я подумаю»."),
         ("Без объяснений","Не требует аргументов, справок и презентации на 40 слайдов."),
         ("Работает с первого раза","Повторный запрос возвращает тот же результат. Детерминизм.")],
  stats=[("1","слог"),("0","лишних обязательств"),("+40%","свободного времени")],
  vs=("Ну, наверное…",[("Последствия","никаких","переезд к тёще"),("Ясность","абсолютная","сомнительная"),("Сожаление","редко","каждый раз")]),
  price="Бесплатно. Но вы откажетесь.", final="Откажи красиво.", others="Есть и другие варианты"),
 dict(slug="ne-znayu", word="Не знаю", dot="…", a="#ffd76a", b="#c98a00", bg="#100e06",
  badge="Ответ v0.9 beta · Powered by неопределённость", tag="Честность уровня enterprise.",
  cta="Получить «Не знаю»", cta2="Подумать ещё",
  feats=[("Нулевая ответственность","Ничего не обещал — ничего не должен."),
         ("Подходит на любой вопрос","От «куда пойдём ужинать» до смысла жизни."),
         ("Снимает ожидания","Никто не разочарован, потому что никто ничего не ждал.")],
  stats=[("50/50","точность"),("∞","времени на раздумья"),("0","ошибок за всю историю")],
  vs=("Уверенный бред",[("Честность","100%","0%"),("Риск опозориться","минимальный","высокий"),("Выглядит умно","почему-то да","до первой проверки")]),
  price="Цена? Без понятия.", final="Пожми плечами.", others="Может, другой ответ?"),
 dict(slug="nahuy", word="Иди нахуй", dot=".", a="#d4ff3a", b="#7bd400", bg="#060a02",
  badge="Ответ v∞ · Powered by закончившееся терпение", tag="Ответ, который закрывает тему.",
  cta="Отправить", cta2="Продолжить спор",
  feats=[("Конец диалога","Финальная версия. Обновлений не планируется."),
         ("Понятно без перевода","Поддерживает все языки мира, включая жесты."),
         ("Экологично","Экономит нервные клетки обеим сторонам. Ну, одной точно.")],
  stats=[("2","слова"),("0","встречных вопросов"),("100%","закрытых тем")],
  vs=("Давай обсудим",[("Длительность","2 секунды","до утра"),("Эффективность","максимальная","спорная"),("Катарсис","есть","нет")]),
  price="Бесплатно. Удовольствие бесценно.", final="Отправь уже.", others="Слишком жёстко? Есть мягче"),
 dict(slug="mozhet-byt", word="Может быть", dot=".", a="#8fd0ff", b="#1f7fe0", bg="#040a14",
  badge="Ответ v1.5 · Quantum Edition", tag="Ответ в суперпозиции.",
  cta="Получить «Может быть»", cta2="Уточнить",
  feats=[("Гибкость","Одновременно да и нет, пока кто-нибудь не проверит."),
         ("Выход всегда открыт","Можно передумать в любую сторону. Без штрафов."),
         ("Надежда включена","Собеседник уходит счастливым. Ненадолго.")],
  stats=[("50%","да"),("50%","нет"),("100%","интриги")],
  vs=("Да",[("Обязательства","никаких","все"),("Пространство для манёвра","огромное","ноль"),("Нервы собеседника","на пределе","в норме")]),
  price="Возможно, бесплатно.", final="Оставь интригу.", others="Определился? Выбирай"),
 dict(slug="ya-podumayu", word="Я подумаю", dot=".", a="#79f2d4", b="#0aa585", bg="#03100d",
  badge="Ответ v4.0 · Async Processing", tag="Отказ с отложенной доставкой.",
  cta="Получить «Я подумаю»", cta2="Напомнить позже",
  feats=[("Асинхронно","Ответ придёт когда-нибудь. Скорее всего, никогда."),
         ("Вежливо","Звучит как интерес, работает как «нет»."),
         ("Масштабируется","Можно думать над тысячей предложений одновременно.")],
  stats=[("∞","дней на обработку"),("0","финальных решений"),("97%","так и не подумали")],
  vs=("Нет",[("Конфликт","отложен","прямо сейчас"),("Выглядишь как","вдумчивый","грубиян"),("Результат","тот же","тот же")]),
  price="Цену обдумаем.", final="Подумай об этом.", others="Пока думаешь — глянь другие"),
 dict(slug="ok", word="Ок", dot=".", a="#ececf2", b="#70707e", bg="#0a0a0c",
  badge="Ответ v1.0 · Minimal Edition", tag="Два символа. Бесконечный подтекст.",
  cta="Получить «Ок»", cta2="Расшифровать",
  feats=[("Минимализм","Никаких лишних букв. Даже точка — на ваш страх и риск."),
         ("Многозначность","Может значить «отлично», а может — «ты ещё пожалеешь»."),
         ("Работает везде","Чат, почта, спор с мамой. Универсальный закрыватель.")],
  stats=[("2","символа"),("47","смыслов"),("1","точка, меняющая всё")],
  vs=("Окей!",[("Энтузиазм","не обнаружен","подозрительный"),("Пассивная агрессия","встроена","нет"),("Тревога собеседника","высокая","низкая")]),
  price="Ок.", final="Ок.", others="Не ок? Есть другие"),
 dict(slug="otstan", word="Отстань", dot=".", a="#ff9fd4", b="#d8257f", bg="#14050d",
  badge="Ответ v2.2 · Personal Space Pro", tag="Личное пространство как сервис.",
  cta="Получить «Отстань»", cta2="Ещё один вопрос",
  feats=[("Мгновенная тишина","Количество сообщений падает до нуля. В теории."),
         ("Без мата","Подходит для работы, семьи и общих чатов."),
         ("Защита от «а может»","Блокирует уговоры на уровне протокола.")],
  stats=[("1","слово"),("2 м","личного пространства"),("0","«ну пожалуйста»")],
  vs=("Ну ладно, давай",[("Время на себя","есть","забудь"),("Самоуважение","на месте","под вопросом"),("Следующие просьбы","реже","чаще")]),
  price="Бесплатно. Только отстаньте.", final="Отстань.", others="Слишком мягко? Есть пожёстче"),
 dict(slug="pohuy", word="Похуй", dot=".", a="#ffb675", b="#f05800", bg="#140902",
  badge="Ответ v∞ · Zen Mode", tag="Буддизм для занятых.",
  cta="Получить «Похуй»", cta2="Переживать",
  feats=[("Дзен из коробки","Просветление без медитаций, ретритов и смузи."),
         ("Экономит нервы","Тревожность падает до заводских настроек."),
         ("Совместим с любой проблемой","Дедлайн, бывшая, курс доллара — всё обрабатывается одинаково.")],
  stats=[("0","переживаний"),("0","бессонных ночей"),("100%","спокойствия")],
  vs=("Накрутить себя",[("Сон","крепкий","3 часа"),("Морщины","нет","есть"),("Результат","такой же","такой же")]),
  price="Сколько стоит? Похуй.", final="Отпусти.", others="Не похуй? Выбери другой"),
 dict(slug="sam-durak", word="Сам дурак", dot=".", a="#e8bd8f", b="#9a5f26", bg="#0f0a06",
  badge="Ответ v1.0 · Classic Since 1st Grade", tag="Аргумент, проверенный школой.",
  cta="Получить «Сам дурак»", cta2="Возразить",
  feats=[("Зеркальная защита","Любое оскорбление возвращается отправителю."),
         ("Не требует логики","Работает даже когда аргументов нет. Особенно тогда."),
         ("Классика","Проверено поколениями на продлёнке.")],
  stats=[("100%","отражения"),("0","контраргументов"),("30+","лет в продакшене")],
  vs=("Развёрнутый ответ",[("Время на сочинение","0 сек","20 минут"),("Попадание","точное","мимо"),("Ностальгия","есть","нет")]),
  price="Бесплатно. Сам такой.", final="Отзеркаль.", others="Аргументы кончились? Есть ещё"),
 dict(slug="huynya", word="Хуйня", dot=".", a="#6ef7ff", b="#00a3c7", bg="#020d10",
  badge="Фидбек v1.0 · Code Review Edition", tag="Переделывай.",
  cta="Получить «Хуйня»", cta2="А что не так?",
  feats=[("Конструктивно","Одно слово вмещает весь фидбек. Детали — на ваше усмотрение."),
         ("Мотивирует","Ничто так не вдохновляет переделать, как это слово."),
         ("Универсально","Подходит для дизайна, кода, презентаций и чужих стартапов.")],
  stats=[("1","слово фидбека"),("∞","итераций"),("v27","финал_точно_финал")],
  vs=("В целом неплохо",[("Честность","100%","0%"),("Итог","переделано","как было"),("Экономия времени","сразу","через месяц")]),
  price="Бесплатно. Переделывай.", final="Переделывай.", others="Другие ответы"),
]
ALL = [(p["slug"],p["word"]) for p in PAGES]
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;800;900&family=Manrope:wght@400;500;700&display=swap" rel="stylesheet">'
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;overflow-x:clip}
body{background:var(--bg);color:#f4f1fa;font-family:Manrope,system-ui,sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:560px;margin:0 auto;padding:0 20px}
.grain{position:fixed;inset:0;pointer-events:none;z-index:50;opacity:.07;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.btn{white-space:nowrap;display:inline-flex;align-items:center;gap:8px;height:52px;padding:0 24px;border-radius:999px;font:700 16px Manrope,system-ui,sans-serif;border:0;cursor:pointer;transition:transform .15s}
.btn:active{transform:scale(.96)}
.btn-w{background:#fff;color:#0a0a0a}
.btn-g{background:rgba(255,255,255,.06);color:#fff;border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(10px)}
"""
def page(p):
    other = [x for x in ALL if x[0]!=p["slug"]]
    feats = "".join(f'<div class="card"><div class="num">0{i+1}</div><h3>{t}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(p["feats"]))
    stats = "".join(f'<div class="stat"><b>{v}</b><span>{l}</span></div>' for v,l in p["stats"])
    vsname, rows = p["vs"]
    vrows = "".join(f'<tr><td>{r}</td><td class="us">{u}</td><td>{t}</td></tr>' for r,u,t in rows)
    olinks = "".join(f'<a class="ol" href="../{s}/">{w}<span>→</span></a>' for s,w in other)
    marq = " ".join([f'<span>{p["word"]}{p["dot"]}</span><i>✦</i>']*8)
    long = len(p["word"])>4
    L = max(len(w) for w in (p["word"]+p["dot"]).split())
    vw = min(40, round(84/(L*0.8),1)); fs = f"min({vw}vw,{round(vw*5.2)}px)"
    dpx = min(300, round(1150/(L*0.78))); dfs = f"min({round(dpx/14,1)}vw,{dpx}px)"
    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p["word"]}{p["dot"]} — {p["tag"]}</title>
<meta name="description" content="{p["tag"]}"><meta property="og:type" content="website">
<meta property="og:title" content="{p["word"]}{p["dot"]}"><meta property="og:description" content="{p["tag"]}">
<meta property="og:image" content="{BASE}{p["slug"]}/og.png"><meta property="og:url" content="{BASE}{p["slug"]}/">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="{p["bg"]}">{FONTS}
<style>:root{{--a:{p["a"]};--b:{p["b"]};--bg:{p["bg"]}}}{BASE_CSS}
.hero{{position:relative;min-height:100svh;display:flex;flex-direction:column;overflow:hidden}}
.orb{{position:absolute;border-radius:50%;filter:blur(60px);opacity:.75}}
.o1{{width:120vw;height:120vw;max-width:700px;max-height:700px;right:-45%;top:4%;background:radial-gradient(circle,var(--b),transparent 65%);animation:fl 9s ease-in-out infinite}}
.o2{{width:70vw;height:70vw;max-width:420px;max-height:420px;left:-30%;top:38%;background:radial-gradient(circle,var(--a),transparent 65%);opacity:.35;animation:fl 12s ease-in-out infinite reverse}}
@keyframes fl{{50%{{transform:translate(-6%,5%) scale(1.08)}}}}
.ring{{position:absolute;right:-25%;top:12%;width:85vw;max-width:520px;aspect-ratio:1;border-radius:50%;border:1px solid color-mix(in srgb,var(--a) 35%,transparent);}}
.ring:after{{content:"";position:absolute;inset:14%;border-radius:50%;border:1px dashed color-mix(in srgb,var(--a) 25%,transparent);animation:spin 40s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.nav{{position:relative;z-index:2;margin:18px auto 0;max-width:calc(100% - 32px);display:flex;align-items:center;gap:14px;padding:6px 6px 6px 20px;border-radius:999px;background:rgba(10,10,15,.55);border:1px solid rgba(255,255,255,.08);backdrop-filter:blur(14px)}}
.logo{{font:800 18px Unbounded,system-ui,sans-serif;background:linear-gradient(90deg,#fff,var(--a));-webkit-background-clip:text;color:transparent;white-space:nowrap}}
.nav .btn{{height:40px;padding:0 16px;font-size:14px}}
.hc{{width:100%;position:relative;z-index:2;margin-top:auto;padding-bottom:44px}}
.badge{{display:inline-flex;align-items:center;gap:10px;padding:5px 14px 5px 5px;border-radius:999px;background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.08);font-size:13px;color:rgba(255,255,255,.75);max-width:100%}}
.badge b{{font-size:11px;font-weight:700;padding:4px 10px;border-radius:999px;background:linear-gradient(90deg,var(--a),var(--b));color:#0a0a0a;flex:none}}
.badge span{{min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
h1{{font:900 {fs}/.9 Unbounded,system-ui,sans-serif;letter-spacing:-.05em;margin:18px 0 18px -.04em;background:linear-gradient(180deg,#fff 10%,var(--a));-webkit-background-clip:text;color:transparent}}
h1 em{{font-style:normal;color:var(--a);-webkit-text-fill-color:var(--a)}}
.tag{{font-size:22px;color:rgba(255,255,255,.8);margin-bottom:28px}}
.row{{display:flex;gap:10px;flex-wrap:wrap}}
.marq{{border-block:1px solid rgba(255,255,255,.08);overflow:hidden;padding:18px 0;white-space:nowrap}}
.marq div{{display:inline-flex;gap:28px;align-items:center;animation:mq 22s linear infinite;font:800 28px Unbounded}}
.marq i{{font-style:normal;color:var(--a);font-size:18px}}
@keyframes mq{{to{{transform:translateX(-50%)}}}}
section{{padding:80px 0 0}}
.eyebrow{{font:500 12px Unbounded,system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--a);margin-bottom:14px}}
h2{{font:800 clamp(30px,8vw,44px)/1.05 Unbounded,system-ui,sans-serif;letter-spacing:-.03em;margin-bottom:28px}}
.card{{padding:24px;border-radius:24px;background:linear-gradient(160deg,rgba(255,255,255,.06),rgba(255,255,255,.015));border:1px solid rgba(255,255,255,.08);margin-bottom:12px}}
.num{{font:800 13px Unbounded,system-ui,sans-serif;color:var(--a);margin-bottom:28px}}
.card h3{{font:800 20px Unbounded,system-ui,sans-serif;margin-bottom:8px}}
.card p{{color:rgba(255,255,255,.62);line-height:1.5}}
.stats{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.stat{{padding:22px;border-radius:24px;background:var(--b);color:#fff;min-height:130px;display:flex;flex-direction:column;justify-content:space-between}}
.stat:nth-child(2){{background:#fff;color:#0a0a0a}}
.stat:nth-child(3){{grid-column:1/-1;background:transparent;border:1px solid rgba(255,255,255,.14);color:#fff}}
.stat b{{font:900 40px Unbounded,system-ui,sans-serif;letter-spacing:-.04em}}
.stat span{{font-size:14px;opacity:.75}}
table{{width:100%;border-collapse:collapse;font-size:15px}}
th{{font:500 11px Unbounded,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.45);text-align:left;padding:0 8px 12px}}
th.us{{color:var(--a)}}
td{{padding:16px 8px;border-top:1px solid rgba(255,255,255,.08);color:rgba(255,255,255,.55)}}
td:first-child{{color:#fff;font-weight:500}}
td.us{{color:var(--a);font-weight:700}}
.price{{text-align:center;padding:40px 24px;border-radius:32px;background:radial-gradient(circle at 50% 0,color-mix(in srgb,var(--b) 55%,transparent),transparent 70%),rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.1)}}
.price .big{{font:900 72px Unbounded,system-ui,sans-serif;letter-spacing:-.05em}}
.price p{{color:rgba(255,255,255,.7);margin:6px 0 24px;font-size:18px}}
.price ul{{list-style:none;text-align:left;display:inline-block;margin-bottom:28px;color:rgba(255,255,255,.8);line-height:2}}
.price li:before{{content:"✓  ";color:var(--a);font-weight:700}}
.final{{padding:100px 0 40px;text-align:center}}
.final h2{{font-size:clamp(40px,12vw,64px)}}
.ol{{display:flex;justify-content:space-between;align-items:center;padding:20px 4px;border-top:1px solid rgba(255,255,255,.08);font:800 24px Unbounded}}
.ol span{{color:var(--a);transition:transform .2s}}.ol:active span{{transform:translateX(6px)}}
footer{{padding:40px 0 calc(40px + env(safe-area-inset-bottom));color:rgba(255,255,255,.35);font-size:13px;display:flex;justify-content:space-between}}
.ov{{position:fixed;inset:0;z-index:40;display:grid;place-items:center;background:var(--bg);opacity:0;pointer-events:none;transition:opacity .25s}}
.ov.on{{opacity:1;pointer-events:auto}}
.ov div{{font:900 {fs}/.92 Unbounded,system-ui,sans-serif;letter-spacing:-.05em;text-align:center;padding:20px;background:linear-gradient(180deg,#fff,var(--a));-webkit-background-clip:text;color:transparent;transform:scale(.6);transition:transform .45s cubic-bezier(.2,1.6,.4,1)}}
.ov.on div{{transform:scale(1)}}
.ov small{{position:absolute;bottom:40px;color:rgba(255,255,255,.4);font-size:13px}}
.sheet{{position:fixed;left:0;right:0;bottom:0;z-index:41;padding:28px 20px calc(28px + env(safe-area-inset-bottom));background:#151518;border-radius:28px 28px 0 0;transform:translateY(100%);transition:transform .35s cubic-bezier(.2,.9,.3,1)}}
.sheet{{visibility:hidden}}.sheet.on{{transform:none;visibility:visible}}
.sheet input{{width:100%;height:56px;border-radius:16px;border:1px solid rgba(255,255,255,.12);background:#0c0c0e;color:#fff;font:500 16px Manrope,system-ui,sans-serif;padding:0 18px;margin:14px 0}}
.sheet h3{{font:800 20px Unbounded}}
.ans{{font:800 22px Unbounded,system-ui,sans-serif;color:var(--a);min-height:30px;margin-bottom:14px}}
.rev{{opacity:0;transform:translateY(24px);transition:opacity .7s,transform .7s}}.rev.in{{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
@media (hover:hover){{.btn:hover{{transform:translateY(-2px)}}.btn-w:hover{{box-shadow:0 10px 40px -10px var(--a)}}.btn-g:hover{{background:rgba(255,255,255,.12)}}
.card{{transition:border-color .25s,transform .25s}}.card:hover{{border-color:color-mix(in srgb,var(--a) 45%,transparent);transform:translateY(-4px)}}
.ol:hover span{{transform:translateX(8px)}}.ol:hover{{color:var(--a)}}}}
@media (min-width:900px){{
.wrap{{max-width:1240px;padding:0 56px}}
.nav{{margin-top:28px}}
.o1{{width:1100px;height:1100px;max-width:none;max-height:none;right:-260px;top:-200px}}
.o2{{width:700px;height:700px;max-width:none;max-height:none;left:-200px;top:auto;bottom:-300px}}
.ring{{width:760px;max-width:none;right:-120px;top:6%}}
.hc{{padding-bottom:88px}}
h1{{font-size:{dfs};margin:26px 0 22px -.04em}}
.tag{{font-size:30px;margin-bottom:40px;max-width:700px}}
.btn{{height:60px;padding:0 30px;font-size:17px}}
.nav .btn{{height:42px;font-size:14px}}
.badge{{font-size:14px}}
.marq{{padding:26px 0}}.marq div{{font-size:44px;gap:44px}}
section{{padding-top:140px}}
h2{{font-size:clamp(48px,5vw,76px);margin-bottom:48px}}
.feats{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.feats .card{{margin:0;padding:32px;min-height:300px;display:flex;flex-direction:column}}
.card .num{{margin-bottom:auto}}.card h3{{font-size:24px;margin-top:60px}}.card p{{font-size:17px}}
.stats{{grid-template-columns:repeat(3,1fr);gap:16px}}.stat{{min-height:240px;padding:32px}}.stat:nth-child(3){{grid-column:auto}}.stat b{{font-size:72px}}.stat span{{font-size:17px}}
table{{font-size:20px}}td{{padding:24px 12px}}th{{font-size:13px;padding:0 12px 16px}}
.price{{max-width:680px;margin:0 auto;padding:64px 48px}}.price .big{{font-size:120px}}.price p{{font-size:22px}}
.final{{padding:180px 0 80px}}.final h2{{font-size:clamp(80px,10vw,150px);margin-bottom:56px}}
.ols{{display:grid;grid-template-columns:1fr 1fr;column-gap:48px}}.ol{{font-size:32px;padding:28px 4px}}
.sheet{{left:50%;right:auto;bottom:32px;width:520px;transform:translate(-50%,calc(100% + 40px));border-radius:28px;border:1px solid rgba(255,255,255,.1)}}
.sheet.on{{transform:translate(-50%,0)}}
.ov div{{font-size:{dfs}}}
}}
</style></head><body>
<div class="grain"></div>
<header class="hero"><div class="orb o1"></div><div class="orb o2"></div><div class="ring"></div>
<nav class="nav"><span class="logo">{p["word"]}{p["dot"]}</span><button class="btn btn-w" data-go>{p["cta"] if len(p["cta"])<=10 else "Получить"} →</button></nav>
<div class="wrap hc"><div class="badge"><b>NEW</b><span>{p["badge"]}</span></div>
<h1>{p["word"]}<em>{p["dot"]}</em></h1>
<p class="tag">{p["tag"]}</p>
<div class="row"><button class="btn btn-w" data-go>{p["cta"]} →</button><button class="btn btn-g" data-ask>{p["cta2"]}</button></div></div></header>
<div class="marq"><div>{marq}{marq}</div></div>
<main class="wrap">
<section class="rev"><div class="eyebrow">Почему «{p["word"]}»</div><h2>Один ответ.<br>Ноль вопросов.</h2><div class="feats">{feats}</div></section>
<section class="rev"><div class="eyebrow">В цифрах</div><h2>Проверено<br>на людях.</h2><div class="stats">{stats}</div></section>
<section class="rev"><div class="eyebrow">Сравнение</div><h2>«{p["word"]}» vs «{vsname}»</h2>
<table><tr><th></th><th class="us">{p["word"]}</th><th>{vsname}</th></tr>{vrows}</table></section>
<section class="rev"><div class="price"><div class="eyebrow">Тариф</div><div class="big">0 ₽</div><p>{p["price"]}</p>
<ul><li>Безлимит использований</li><li>Без подписки и SMS</li><li>Работает офлайн</li></ul><br><button class="btn btn-w" data-go>{p["cta"]} →</button></div></section>
<div class="final rev"><h2>{p["final"]}</h2><button class="btn btn-w" data-go>{p["cta"]} →</button></div>
<section class="rev" style="padding-top:20px"><div class="eyebrow">{p["others"]}</div><div class="ols">{olinks}<a class="ol" href="../">Все ответы<span>→</span></a></div></section>
<footer><span>© 2026 {p["word"]} Inc.</span><span>Ответ без лишних слов</span></footer>
</main>
<div class="ov" id="ov"><div>{p["word"]}{p["dot"]}</div><small>Нажми, чтобы закрыть</small></div>
<div class="sheet" id="sh"><h3>Задай любой вопрос</h3><input id="q" placeholder="Например: а можно…?" enterkeyhint="send"><div class="ans" id="an"></div><button class="btn btn-w" id="qa">Получить ответ →</button></div>
<script>
const ov=document.getElementById('ov'),sh=document.getElementById('sh'),q=document.getElementById('q'),an=document.getElementById('an');
document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{{sh.classList.remove('on');ov.classList.add('on');try{{navigator.vibrate&&navigator.vibrate(60)}}catch(e){{}}}});
ov.onclick=()=>ov.classList.remove('on');
document.querySelectorAll('[data-ask]').forEach(b=>b.onclick=()=>{{an.textContent='';sh.classList.add('on');setTimeout(()=>q.focus(),300)}});
const go=()=>{{an.textContent='Думаю…';setTimeout(()=>an.textContent={json.dumps(p["word"]+p["dot"])},700)}};
document.getElementById('qa').onclick=go;q.onkeydown=e=>{{if(e.key==='Enter')go()}};
document.addEventListener('click',e=>{{if(sh.classList.contains('on')&&!sh.contains(e.target)&&!e.target.closest('[data-ask]'))sh.classList.remove('on')}});
const io=new IntersectionObserver(es=>es.forEach(x=>{{if(x.isIntersecting){{x.target.classList.add('in');io.unobserve(x.target)}}}}),{{threshold:.15}});
document.querySelectorAll('.rev').forEach(el=>io.observe(el));
</script></body></html>"""

hub_items = "".join(f'<a href="{p["slug"]}/" style="--a:{p["a"]};--b:{p["b"]}"><span>{p["word"]}{p["dot"]}</span><i>→</i></a>' for p in PAGES)
hub = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ответы — выбери свой</title><meta property="og:title" content="Выбери свой ответ"><meta property="og:description" content="11 ответов на все случаи жизни."><meta property="og:image" content="{BASE}og.png"><meta name="twitter:card" content="summary_large_image">{FONTS}<style>:root{{--bg:#09090b}}{BASE_CSS}
main.wrap{{min-height:100svh;display:flex;flex-direction:column;padding-top:48px}}
.eyebrow{{font:500 12px Unbounded,system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.45)}}
h1{{font:900 clamp(44px,13vw,72px)/.95 Unbounded,system-ui,sans-serif;letter-spacing:-.04em;margin:14px 0 36px}}
.list a{{display:flex;justify-content:space-between;align-items:center;padding:26px 0;border-top:1px solid rgba(255,255,255,.1);font:800 clamp(30px,9vw,44px) Unbounded,system-ui,sans-serif;letter-spacing:-.03em;transition:padding .2s}}
.list a span{{background:linear-gradient(90deg,#fff,var(--a));-webkit-background-clip:text;color:transparent}}
.list a i{{font-style:normal;color:var(--a);font-size:.7em}}
.list a:active{{padding-left:10px}}
footer{{margin-top:auto;padding:40px 0 calc(32px + env(safe-area-inset-bottom));color:rgba(255,255,255,.35);font-size:13px}}
@media (hover:hover){{.list a:hover{{padding-left:14px}}.list a:hover i{{transform:translateX(6px)}}.list a i{{transition:transform .2s}}}}
@media (min-width:900px){{.wrap{{max-width:1240px;padding:0 56px}}main.wrap{{padding-top:96px}}h1{{font-size:clamp(72px,8vw,128px);margin-bottom:64px}}
.list{{display:grid;grid-template-columns:1fr 1fr;column-gap:56px}}.list a{{font-size:clamp(36px,3.4vw,52px);padding:32px 0}}footer{{font-size:15px}}}}
</style></head><body><div class="grain"></div><main class="wrap"><div class="eyebrow">Ответы как сервис</div><h1>Выбери<br>свой ответ.</h1>
<div class="list">{hub_items}</div><footer>Каждый ответ — отдельная страница. Кидай ссылку вместо слов.</footer></main></body></html>"""
open("index.html","w").write(hub)
for p in PAGES:
    os.makedirs(""+p["slug"],exist_ok=True); open(""+p["slug"]+"/index.html","w").write(page(p))
json.dump([dict(slug=p["slug"],word=p["word"],dot=p["dot"],a=p["a"],b=p["b"],bg=p["bg"],tag=p["tag"]) for p in PAGES],open("_project/pages.json","w"),ensure_ascii=False)
