#!/usr/bin/env python3
"""
Покадровый рендер Marjon reel v2.

  python3 render.py probe 1.5 6 12 20 30 38     # кадры для проверки (probe/*.png + лист)
  python3 render.py draft                       # быстрый черновик 540p, crf 24
  python3 render.py full                        # мастер 1080x1920, 30 fps, кадры в frames/
  python3 render.py part A|B|C                  # параллельные чанки (см. build.py)

Движок детерминированный: seek(t) + ожидание seeked у видео, поэтому кадры
не «плывут» и рендер можно резать на параллельные куски.
"""
import asyncio, os, sys, shutil
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(HERE, "promo.html")
FPS = 30
W, H = 1080, 1920

CHUNKS = {  # имя: (начало, конец) в секундах — по 3 процесса
    "A": (0.0, 13.6),
    "B": (13.6, 28.6),
    "C": (28.6, 40.0),
}


async def open_page(p, w=W, h=H, scale=1):
    b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required",
                                     "--disable-gpu-vsync", "--force-device-scale-factor=1"])
    pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
    await pg.goto(URL, wait_until="load")
    await pg.evaluate("window.MARJON.ready()")
    return b, pg


async def grab(pg, t, path):
    await pg.evaluate("t => window.MARJON.renderAt(t)", t)
    # element.screenshot ждёт «стабильности» элемента и падает на бесконечных
    # CSS-анимациях видео-слоя -> берём CDP-снимок клипа по боксу сцены.
    box = await pg.evaluate("""() => {
        const r = document.getElementById('stage').getBoundingClientRect();
        return {x:r.x, y:r.y, width:r.width, height:r.height};
    }""")
    await pg.screenshot(path=path, clip=box, animations="disabled", caret="hide")


async def probe(times, outdir="probe"):
    os.makedirs(os.path.join(HERE, outdir), exist_ok=True)
    async with async_playwright() as p:
        b, pg = await open_page(p, W, H, 1)   # в render-режиме сцена 1080×1920
        paths = []
        for t in times:
            path = os.path.join(HERE, outdir, f"t{float(t):05.2f}.png")
            await grab(pg, float(t), path)
            paths.append(path)
            print("probe", t)
        await b.close()
    # контактный лист
    from PIL import Image, ImageDraw
    tiles = [Image.open(x).convert("RGB") for x in paths]
    tw, th = 240, 427
    cols = min(6, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), "#0a0a0a")
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 5, y + th + 3), f"t={times[i]}s", fill="#7de8e2")
    out = os.path.join(HERE, outdir, "sheet.png")
    sheet.save(out)
    print("лист:", out)


async def render_chunk(name, frame_dir):
    a, b_ = CHUNKS[name]
    os.makedirs(frame_dir, exist_ok=True)
    n0, n1 = int(round(a * FPS)), int(round(b_ * FPS))
    async with async_playwright() as p:
        br, pg = await open_page(p)
        for i in range(n0, n1):
            t = i / FPS
            path = os.path.join(frame_dir, f"f{i:05d}.png")
            if os.path.exists(path):
                continue
            await grab(pg, t, path)
            if i % 30 == 0:
                print(f"[{name}] {i}/{n1} ({t:.1f}s)", flush=True)
        await br.close()
    print(f"[{name}] готово: {n1-n0} кадров")


async def render_all(frame_dir, step=1):
    os.makedirs(frame_dir, exist_ok=True)
    async with async_playwright() as p:
        br, pg = await open_page(p)
        n = int(40 * FPS / step)
        for k in range(n):
            i = k * step
            t = i / FPS
            await grab(pg, t, os.path.join(frame_dir, f"f{i:05d}.png"))
            if k % 60 == 0:
                print(f"{i} ({t:.1f}s)", flush=True)
        await br.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd == "probe":
        asyncio.run(probe(sys.argv[2:] or ["0.6", "3.2", "6.5", "9.4", "11.8", "16.0", "21.5", "26.0", "30.5", "35.0", "39.2"]))
    elif cmd == "draft":
        d = os.path.join(HERE, "probe", "draft")
        if os.path.isdir(d):
            shutil.rmtree(d)
        asyncio.run(render_all(d, step=3))
    elif cmd == "full":
        asyncio.run(render_chunk(sys.argv[2] if len(sys.argv) > 2 else "A", os.path.join(HERE, "frames")))
    elif cmd == "all":
        asyncio.run(render_all(os.path.join(HERE, "frames")))
    else:
        print(__doc__)
