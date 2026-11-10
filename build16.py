#!/usr/bin/env python3
"""Сборка 16-секундной версии: музыка + SFX по монтажным акцентам -> mp4."""
import os, subprocess
import imageio_ffmpeg
HERE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
MUSIC = os.path.join(HERE, "assets", "audio", "134.mp3")
SFX = os.path.join(HERE, "assets", "sfx")
OUT = os.path.join(HERE, "marjon_reel_16s_9x16.mp4")
HITS = [
    (0.05, "whoosh.mp3", 0.55), (2.70, "whoosh.mp3", 0.5),
    (2.95, "tick.mp3", 0.5), (3.17, "tick.mp3", 0.45), (3.39, "tick.mp3", 0.4),
    (5.40, "whoosh.mp3", 0.5), (5.85, "click.mp3", 0.35), (6.75, "click.mp3", 0.33),
    (7.65, "click.mp3", 0.33), (8.55, "success.mp3", 0.4),
    (9.00, "whoosh.mp3", 0.45), (11.40, "whoosh.mp3", 0.5),
    (12.55, "check.mp3", 0.5), (13.60, "whoosh.mp3", 0.55),
    (14.30, "pop.mp3", 0.45), (15.30, "success.mp3", 0.4),
]
def build_audio():
    inputs = ["-i", MUSIC]
    for _, f, _ in HITS: inputs += ["-i", os.path.join(SFX, f)]
    parts = ["[0:a]atrim=4.90:20.90,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.4,"
             "afade=t=out:st=14.9:d=1.1[mus]"]
    mix = "[mus]"
    for i, (t, f, g) in enumerate(HITS):
        d = int(t * 1000)
        parts.append(f"[{i+1}:a]adelay={d}|{d},volume={g}[s{i}]")
        mix += f"[s{i}]"
    parts.append(f"{mix}amix=inputs={len(HITS)+1}:normalize=0:dropout_transition=0,"
                 f"loudnorm=I=-14:TP=-1.3:LRA=9,alimiter=limit=0.94[aout]")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(parts), "-map", "[aout]",
                    "-ar", "48000", "-ac", "2", "-t", "16", os.path.join(HERE, "audio16.wav")], check=True)
def encode():
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error",
                    "-framerate", "30", "-i", os.path.join(HERE, "frames16", "f%05d.png"),
                    "-i", os.path.join(HERE, "audio16.wav"),
                    "-map", "0:v", "-map", "1:a",
                    "-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-tune", "stillimage", "-threads", "1",
                    "-profile:v", "high", "-color_range", "tv", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", "-shortest", OUT], check=True)
    print("готово:", OUT, os.path.getsize(OUT) // 1024, "КБ")
if __name__ == "__main__":
    build_audio(); encode()
