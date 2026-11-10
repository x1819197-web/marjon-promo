#!/usr/bin/env python3
"""
Marjon reel v2 — сборка мастера.

  python3 build.py frames            # все 1200 кадров (последовательно)
  python3 build.py chunk A|B|C       # параллельные чанки (3 процесса)
  python3 build.py encode            # кадры + музыка/SFX -> mp4 (1080x1920, 30 fps)
  python3 build.py all               # всё подряд

Звук: музыка Mixkit (бесплатно для коммерческого использования) + SFX,
сведение: ducking под «голос» не нужен (озвучки нет), музыка -14 LUFS,
SFX ставятся по измеренным пикам и попадают в монтажные акценты.
"""
import os, subprocess, sys
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
FRAMES = os.path.join(HERE, "frames")
OUT = os.path.join(HERE, "marjon_reel_v2_9x16.mp4")
MUSIC = os.path.join(HERE, "assets", "audio", "134.mp3")   # 123 BPM, плотный бит
SFX = os.path.join(HERE, "assets", "sfx")

# Монтажные акценты: (время, файл, усиление)
HITS = [
    (0.05,  "whoosh.mp3", 0.55),   # вход хука
    (4.95,  "whoosh.mp3", 0.5),    # смена сцены -> боль
    (5.45,  "tick.mp3",   0.5),    # карточка 01
    (5.87,  "tick.mp3",   0.45),   # 02
    (6.29,  "tick.mp3",   0.4),    # 03
    (6.71,  "tick.mp3",   0.35),   # 04
    (10.05, "success.mp3",0.45),   # сборка логотипа
    (13.55, "whoosh.mp3", 0.5),    # -> модули
    (15.32, "click.mp3",  0.35),   # смены панелей (каждые 1.72 c)
    (17.04, "click.mp3",  0.33),
    (18.76, "click.mp3",  0.33),
    (20.48, "click.mp3",  0.33),
    (22.20, "click.mp3",  0.33),
    (24.35, "whoosh.mp3", 0.5),    # -> доверие
    (28.55, "whoosh.mp3", 0.5),    # -> цена
    (30.20, "check.mp3",  0.5),    # цифра «доехала»
    (32.75, "whoosh.mp3", 0.55),   # -> CTA
    (34.00, "pop.mp3",    0.45),   # появление кнопки
    (38.60, "success.mp3",0.4),    # финальный акцент
]

INPUTS = ["-i", MUSIC]
for i, (t, f, g) in enumerate(HITS):
    INPUTS += ["-i", os.path.join(SFX, f)]

# музыка: 40 c с 4.9 s (там, где начинается бит), фейды, −14 LUFS
def audio_filter(offset=0):
    """offset — число видеовходов перед аудио (0: только музыка, 1: кадры+музыка)."""
    mus_idx = offset
    parts = [
        f"[{mus_idx}:a]atrim=4.90:44.90,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.6,"
        f"afade=t=out:st=38.4:d=1.6,volume=1.0[mus]"
    ]
    mix = "[mus]"
    for i, (t, f, g) in enumerate(HITS):
        idx = i + offset + 1
        delay = int(t * 1000)
        parts.append(f"[{idx}:a]adelay={delay}|{delay},volume={g}[s{i}]")
        mix += f"[s{i}]"
    parts.append(f"{mix}amix=inputs={len(HITS)+1}:normalize=0:dropout_transition=0,"
                 f"loudnorm=I=-14:TP=-1.3:LRA=9,alimiter=limit=0.94[aout]")
    return ";".join(parts)


FILTER = audio_filter(1)


def encode():
    if not os.path.isdir(FRAMES) or not os.listdir(FRAMES):
        raise SystemExit("нет кадров: сначала python3 build.py frames")
    n = len([f for f in os.listdir(FRAMES) if f.endswith(".png")])
    print("кадров:", n)
    # 1) аудио-микс (без видео, чтобы не упереться в память)
    wav = os.path.join(HERE, "audio_mix.wav")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *INPUTS,
                    "-filter_complex", audio_filter(0), "-map", "[aout]",
                    "-ar", "48000", "-ac", "2", "-t", "40", wav], check=True)
    print("аудио:", os.path.getsize(wav) // 1024, "КБ")
    # 2) видео + готовая дорожка
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "warning",
           "-framerate", "30", "-i", os.path.join(FRAMES, "f%05d.png"),
           "-i", wav,
           "-map", "0:v", "-map", "1:a",
           "-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-threads", "1", "-profile:v", "high",
           "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-shortest",
           OUT]
    print(" ".join(cmd[:12]), "...")
    subprocess.run(cmd, check=True)
    # второй проход loudnorm (точная нормализация громкости) — необязательно

    print("готово:", OUT, os.path.getsize(OUT) // 1024, "КБ")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "encode"
    if cmd == "encode":
        encode()
    elif cmd == "frames":
        subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "all"], check=True)
    elif cmd == "chunk":
        env = dict(os.environ, LD_LIBRARY_PATH="/home/user/.libs/root/usr/lib/x86_64-linux-gnu")
        subprocess.run([sys.executable, os.path.join(HERE, "render.py"), "full", sys.argv[2]], check=True, env=env)
    elif cmd == "all":
        for c in "ABC":
            print("== chunk", c)
            subprocess.run([sys.executable, __file__, "chunk", c], check=True)
        encode()
    else:
        print(__doc__)
