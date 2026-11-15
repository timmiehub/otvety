# Превью 1200x630 (og.jpg) и иконка 320x168 для списка в боте (thumb.jpg).
# Если есть фото _project/stock/<slug>.jpg — карточка «тупой сток»: фото на весь фон, поверх слово ответа.
# Иначе — старая карточка с градиентом.
# Запуск из корня репо после gen.py: python3 _project/og.py
# Нужны playwright и шрифты: npm i @fontsource/unbounded @fontsource/manrope, путь к node_modules/@fontsource — в FONTS.
import asyncio, json, os, pathlib, tempfile
from playwright.async_api import async_playwright

F = pathlib.Path(os.environ.get("FONTS", "/tmp/fnt/node_modules/@fontsource")).resolve()
STOCK = pathlib.Path("_project/stock").resolve()
u = lambda rel: (F / rel).as_uri()
ff = f"""@font-face{{font-family:U;font-weight:900;src:url({u('unbounded/files/unbounded-cyrillic-900-normal.woff2')})}}
@font-face{{font-family:U;font-weight:900;src:url({u('unbounded/files/unbounded-latin-900-normal.woff2')});unicode-range:U+0000-00FF,U+2026,U+221E}}
@font-face{{font-family:M;font-weight:500;src:url({u('manrope/files/manrope-cyrillic-500-normal.woff2')})}}
@font-face{{font-family:M;font-weight:500;src:url({u('manrope/files/manrope-latin-500-normal.woff2')});unicode-range:U+0000-00FF}}
@font-face{{font-family:M;font-weight:700;src:url({u('manrope/files/manrope-cyrillic-700-normal.woff2')})}}
@font-face{{font-family:M;font-weight:700;src:url({u('manrope/files/manrope-latin-700-normal.woff2')});unicode-range:U+0000-00FF}}"""

# Подгонка шрифта: уменьшаем заголовок, пока не влезет по ширине и высоте, и подпись — по ширине.
FIT = """<script>
const h=document.querySelector('h1'),t=document.querySelector('p');let s=parseInt(getComputedStyle(h).fontSize);
const W=+h.dataset.w,H=+h.dataset.h;
document.fonts.ready.then(()=>{while(s>56&&(h.scrollWidth>W||h.offsetHeight>H)){s-=4;h.style.fontSize=s+'px'}
let ts=parseInt(getComputedStyle(t).fontSize);while(ts>22&&t.scrollWidth>t.parentElement.clientWidth-140){ts-=2;t.style.fontSize=ts+'px'}
document.body.dataset.ok=1});
</script>"""

def plain_card(p):
    start = 300 if len(p["word"]) <= 4 else 170
    return f"""<html><style>{ff}*{{margin:0}}body{{width:1200px;height:630px;background:{p['bg']};overflow:hidden;position:relative;font-family:M}}
.o{{position:absolute;border-radius:50%;filter:blur(70px)}}
.o1{{width:900px;height:900px;right:-300px;top:-260px;background:radial-gradient(circle,{p['b']},transparent 65%);opacity:.85}}
.o2{{width:500px;height:500px;left:-180px;bottom:-260px;background:radial-gradient(circle,{p['a']},transparent 65%);opacity:.35}}
.r{{position:absolute;right:-120px;top:-60px;width:620px;height:620px;border-radius:50%;border:2px solid {p['a']}55}}
h1{{position:absolute;left:72px;bottom:150px;max-width:1060px;font:900 {start}px/.95 U;letter-spacing:-.05em;background:linear-gradient(180deg,#fff 10%,{p['a']});-webkit-background-clip:text;color:transparent}}
p{{position:absolute;left:78px;bottom:78px;max-width:1050px;font:500 40px M;color:#ffffffcc;white-space:nowrap}}</style>
<body><div class="o o1"></div><div class="o o2"></div><div class="r"></div><h1 data-w="1060" data-h="440">{p['word']}{p['dot']}</h1><p>{p['tag']}</p>{FIT}</body></html>"""

def photo_card(p, photo):
    start = 210 if len(p["word"]) <= 5 else 130
    return f"""<html><style>{ff}*{{margin:0}}body{{width:1200px;height:630px;overflow:hidden;position:relative;font-family:M;background:#000 url({photo.as_uri()}) center/cover no-repeat}}
.g{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.74) 0%,rgba(0,0,0,.42) 40%,rgba(0,0,0,0) 66%),linear-gradient(0deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 45%)}}
h1{{position:absolute;left:64px;bottom:150px;max-width:760px;font:900 {start}px/.92 U;letter-spacing:-.05em;color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.5)}}
h1 em{{font-style:normal;color:{p['a']}}}
p{{position:absolute;left:68px;bottom:62px;font:700 30px M;color:#fff;background:rgba(0,0,0,.58);padding:8px 16px;border-radius:12px;white-space:nowrap}}
</style><body><div class="g"></div><h1 data-w="760" data-h="420">{p['word']}<em>{p['dot']}</em></h1><p>{p['tag']}</p>{FIT}</body></html>"""

async def main():
    pages = json.load(open("answers.json", encoding="utf-8"))
    hub = dict(slug="", word="Ответы", dot=".", a="#ffffff", b="#5b5b6b", bg="#09090b", tag=f"{len(pages)} ответов на все случаи жизни.")
    tmp = pathlib.Path(tempfile.gettempdir()) / "otvety-card.html"
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for p in pages + [hub]:
            d = pathlib.Path(p["slug"] or ".")
            photo = STOCK / f"{p['slug']}.jpg"
            tmp.write_text(photo_card(p, photo) if p["slug"] and photo.exists() else plain_card(p), encoding="utf-8")
            await pg.goto(tmp.as_uri()); await pg.wait_for_selector("body[data-ok]")
            await pg.screenshot(path=str(d / "og.jpg"), type="jpeg", quality=88)
            if p["slug"]:
                # thumb: та же карточка, уменьшенная до 320x168 — быстро грузится в списке inline
                await pg.evaluate("document.documentElement.style.zoom=320/1200")
                await pg.set_viewport_size({"width": 320, "height": 168})
                await pg.screenshot(path=str(d / "thumb.jpg"), type="jpeg", quality=82)
                await pg.set_viewport_size({"width": 1200, "height": 630})
        await b.close()
asyncio.run(main())
