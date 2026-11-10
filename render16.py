#!/usr/bin/env python3
"""Покадровый рендер 16-секундной версии (cut16.html) -> frames16/."""
import asyncio, os, sys
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(HERE, "cut16.html")
FPS = 30

async def main(step=1):
    out = os.path.join(HERE, "frames16")
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width":1080,"height":1920}, device_scale_factor=1)
        await pg.goto(URL, wait_until="load")
        await pg.evaluate("window.MARJON.ready()")
        dur = await pg.evaluate("window.MARJON.duration")
        n = int(dur*FPS)
        for i in range(0, n, step):
            t = i/FPS
            await pg.evaluate("t => window.MARJON.renderAt(t)", t)
            box = await pg.evaluate("""() => { const r=document.getElementById('stage').getBoundingClientRect();
                return {x:r.x,y:r.y,width:r.width,height:r.height}; }""")
            await pg.screenshot(path=os.path.join(out, f"f{i:05d}.png"), clip=box)
            if i % 60 == 0: print("frame", i, f"{t:.2f}s", flush=True)
        await b.close()
    print("frames:", len(os.listdir(out)))

if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 1))
