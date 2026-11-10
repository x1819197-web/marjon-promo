#!/usr/bin/env python3
"""
Сбор ассетов для ролика Marjon: бесплатный b-roll (Mixkit, бесплатно для коммерческого
использования), музыка и SFX.

1) index  — собрать каталог клипов по темам + контактный лист превью (чтобы выбрать глазами)
2) fetch  — скачать выбранные клипы в assets/broll
3) audio  — скачать музыку + SFX, замерить BPM/drop
"""
import json, os, re, subprocess, sys, urllib.request
import imageio_ffmpeg

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()


def get(url, path=None, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if path:
        with open(path, "wb") as f:
            f.write(data)
    return data


# ---------------------------------------------------------------- b-roll
TOPICS = {
    "restaurant": ["restaurant", "fine-dining", "cafe"],
    "kitchen": ["kitchen", "chef", "cooking"],
    "checkout": ["bar", "coffee", "cash"],
    "mood": ["business", "office", "city"],
}


def index_broll():
    seen = {}
    for group, topics in TOPICS.items():
        for t in topics:
            try:
                html = get(f"https://mixkit.co/free-stock-video/{t}/").decode("utf-8", "ignore")
            except Exception as e:
                print("  !", t, e)
                continue
            ok_ids = set(re.findall(r"videos/(\d+)/\1-1080\.mp4", html))
            for slug, vid in re.findall(r'href="/free-stock-video/([a-z0-9-]+?)-(\d+)/"', html):
                if vid in ok_ids:
                    seen.setdefault(vid, {"slug": slug, "group": group, "topic": t})
            print(f"  {t}: {len(ok_ids)} клипов")
    json.dump(seen, open(os.path.join(HERE, "broll_index.json"), "w"), ensure_ascii=False, indent=1)
    print("всего уникальных:", len(seen))
    return seen


def contact_sheet(seen):
    """Превью 720p-кадра каждого клипа -> одна картинка, чтобы выбрать глазами."""
    from PIL import Image, ImageDraw
    out = os.path.join(HERE, "broll_contact.png")
    tiles = []
    os.makedirs(os.path.join(A, "broll", "thumb"), exist_ok=True)
    for i, (vid, meta) in enumerate(seen.items()):
        p = os.path.join(A, "broll", "thumb", f"{vid}.jpg")
        if not os.path.exists(p):
            try:
                get(f"https://assets.mixkit.co/videos/{vid}/{vid}-thumb-720-0.jpg", p)
            except Exception as e:
                print("  ! thumb", vid, e)
                continue
        tiles.append((vid, meta, p))
        if i % 12 == 0:
            print("  thumbs", i)
    W, H, COLS = 240, 135, 6
    rows = (len(tiles) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * W, rows * (H + 16)), "#111")
    d = ImageDraw.Draw(sheet)
    for k, (vid, meta, p) in enumerate(tiles):
        im = Image.open(p).convert("RGB").resize((W, H))
        x, y = (k % COLS) * W, (k // COLS) * (H + 16)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + H + 2), f"{vid} {meta['group']}", fill="#9fe")
    sheet.save(out)
    print("контактный лист:", out, sheet.size)


def fetch_broll(ids):
    os.makedirs(os.path.join(A, "broll"), exist_ok=True)
    for vid in ids:
        dst = os.path.join(A, "broll", f"{vid}.mp4")
        if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
            print("  =", vid); continue
        for res in ("720", "360"):
            try:
                get(f"https://assets.mixkit.co/videos/{vid}/{vid}-{res}.mp4", dst)
                print(f"  + {vid} ({res}p, {os.path.getsize(dst)//1024} КБ)")
                break
            except Exception as e:
                print("  !", vid, res, e)


# ---------------------------------------------------------------- audio
MUSIC_IDS = ["102", "105", "113", "124", "134", "160", "1167"]      # corporate/tag
SFX = {
    "tick":      "1117",   # soft tick
    "click":     "1125",   # click
    "check":     "1113",   # check / success blip
    "whoosh":    "1143",   # impact
    "pop":       "2364",
    "success":   "2865",
}


def fetch_audio():
    os.makedirs(os.path.join(A, "audio"), exist_ok=True)
    os.makedirs(os.path.join(A, "sfx"), exist_ok=True)
    for mid in MUSIC_IDS:
        p = os.path.join(A, "audio", f"{mid}.mp3")
        if not os.path.exists(p):
            try:
                get(f"https://assets.mixkit.co/music/{mid}/{mid}.mp3", p)
                print("  ♪", mid, os.path.getsize(p) // 1024, "КБ")
            except Exception as e:
                print("  ! music", mid, e)
    for name, sid in SFX.items():
        p = os.path.join(A, "sfx", f"{name}.mp3")
        if not os.path.exists(p):
            try:
                get(f"https://assets.mixkit.co/active_storage/sfx/{sid}/{sid}-preview.mp3", p)
                print("  ♬", name, os.path.getsize(p) // 1024, "КБ")
            except Exception as e:
                print("  ! sfx", name, e)


def analyze():
    """BPM + момент «дропа» по огибающей энергии (для синхронизации монтажа)."""
    import numpy as np
    from scipy.io import wavfile
    rows = []
    for f in sorted(os.listdir(os.path.join(A, "audio"))):
        if not f.endswith(".mp3"):
            continue
        p = os.path.join(A, "audio", f)
        wav = "/tmp/_a.wav"
        subprocess.run([FF, "-y", "-v", "quiet", "-i", p, "-ac", "1", "-ar", "22050", wav], check=True)
        sr, x = wavfile.read(wav)
        x = x.astype(np.float32) / 32768.0
        hop = 512
        frames = len(x) // hop
        env = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)) for i in range(frames)])
        fps = sr / hop
        # автокорреляция огибающей по окну 1.5-12 Гц -> BPM
        e = env - env.mean()
        ac = np.correlate(e, e, mode="full")[len(e)-1:]
        lo, hi = int(fps/3.0), int(fps/0.4)   # 20..150 BPM
        bpm = 0
        if hi < len(ac):
            lag = lo + int(np.argmax(ac[lo:hi]))
            bpm = 60.0 * fps / lag
        # дроп: самый резкий рост энергии на 1 с
        win = int(fps)
        jump = max(range(win, len(env)-1), key=lambda i: env[i]-env[i-win]) if len(env) > win*2 else 0
        rows.append((f, round(bpm, 1), round(jump/fps, 2), round(len(x)/sr, 1)))
        print(f"  {f}: ~{bpm:.0f} BPM, drop≈{jump/fps:.1f}s, len={len(x)/sr:.1f}s")
    json.dump(rows, open(os.path.join(HERE, "audio_report.json"), "w"), indent=1)
    return rows


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "index":
        seen = index_broll(); contact_sheet(seen)
    elif cmd == "fetch":
        fetch_broll(sys.argv[2:])
    elif cmd == "audio":
        fetch_audio(); analyze()
    else:
        print(__doc__)
