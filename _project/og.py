# Превью 1200x630 для мессенджеров. Запуск из корня репо после gen.py: python3 _project/og.py (нужен playwright)
import asyncio, json, sys
from playwright.async_api import async_playwright
import os
F=os.environ.get("FONTS","/tmp/fnt/node_modules/@fontsource")  # npm i @fontsource/unbounded @fontsource/manrope
ff=f"""@font-face{{font-family:U;font-weight:900;src:url(file://{F}/unbounded/files/unbounded-cyrillic-900-normal.woff2)}}
@font-face{{font-family:U;font-weight:900;src:url(file://{F}/unbounded/files/unbounded-latin-900-normal.woff2);unicode-range:U+0000-00FF,U+2026,U+221E}}
@font-face{{font-family:M;font-weight:500;src:url(file://{F}/manrope/files/manrope-cyrillic-500-normal.woff2)}}
@font-face{{font-family:M;font-weight:500;src:url(file://{F}/manrope/files/manrope-latin-500-normal.woff2);unicode-range:U+0000-00FF}}"""
def card(p):
    long=len(p["word"])>4
    return f"""<html><style>{ff}*{{margin:0}}body{{width:1200px;height:630px;background:{p['bg']};overflow:hidden;position:relative;font-family:M}}
.o{{position:absolute;border-radius:50%;filter:blur(70px)}}
.o1{{width:900px;height:900px;right:-300px;top:-260px;background:radial-gradient(circle,{p['b']},transparent 65%);opacity:.85}}
.o2{{width:500px;height:500px;left:-180px;bottom:-260px;background:radial-gradient(circle,{p['a']},transparent 65%);opacity:.35}}
.r{{position:absolute;right:-120px;top:-60px;width:620px;height:620px;border-radius:50%;border:2px solid {p['a']}55}}
h1{{position:absolute;left:72px;bottom:150px;font:900 {170 if long else 300}px/{.98 if long else .85} U;letter-spacing:-.05em;background:linear-gradient(180deg,#fff 10%,{p['a']});-webkit-background-clip:text;color:transparent}}
p{{position:absolute;left:78px;bottom:78px;font:500 40px M;color:#ffffffcc}}</style>
<body><div class="o o1"></div><div class="o o2"></div><div class="r"></div><h1>{p['word']}{p['dot']}</h1><p>{p['tag']}</p></body></html>"""
async def main():
    pages=json.load(open("_project/pages.json"))
    hub=dict(word="Ответы",dot=".",a="#ffffff",b="#5b5b6b",bg="#09090b",tag="11 ответов на все случаи жизни.")
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':630})
        for p,out in [(x,f"{x['slug']}/og.png") for x in pages]+[(hub,"og.png")]:
            open("/tmp/c.html","w").write(card(p)); await pg.goto("file:///tmp/c.html"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=out)
        await b.close()
asyncio.run(main())
