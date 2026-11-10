# Marjon — рекламный ролик (Reels 9:16)

Вертикальный рекламный ролик для ресторанной ОС **Marjon** (`marjon.tech`). Собран кодом, не в After Effects:
детерминированный HTML-движок сцены (`seek(t)`) → покадровый рендер через Playwright → ffmpeg.

## С чего начать

| Хочу | Файл |
|---|---|
| **просто посмотреть ролик** | `preview_16s.mp4` (0.8 МБ) или `preview_40s.mp4` (1.9 МБ) |
| публиковать в Instagram/TikTok | `marjon_reel_16s_9x16.mp4` (16 с) / `marjon_reel_v2_9x16.mp4` (40 с) |
| записать голос диктора | `marjon_reel_v2_silent.mp4` + тайминги в `README-delivery.md` |
| понять, как это сделано | `START-HERE.md` (структура и сборка), `README-v2.md` (техника, источники, сетка) |
| увидеть все кадры | `storyboard16.png`, `storyboard.png` |
| поставить обложку | `cover16.png`, `cover_1080x1920.png`, `poster_pain.png` |

## Технические параметры

- 1080×1920, 30 fps, H.264 High, BT.709, `yuv420p`, `+faststart`
- звук: AAC 192 kbps 48 kHz, нормализация **−14 LUFS / TP −1.3** (норматив Meta/TikTok)
- субтитры: узбекские, караоке-подсветка, вшиты в кадр
- хронометраж: 40 с (органика) и 16 с (платный трафик)

## Пересборка

```bash
python3 render.py full A && python3 render.py full B && python3 render.py full C
python3 build.py encode          # 40 с
python3 render16.py && python3 build16.py   # 16 с
```

Зависимости: `playwright` (+ Chromium), `imageio-ffmpeg`, `Pillow`. Шрифты и UI-кадры — из репозитория `examerxx/Marjon` (`landing/`, `landing/assets/fonts/`).

## Ассеты

B-roll, музыка и SFX — **Mixkit** (бесплатно для коммерческого использования, без атрибуции). Собраны скриптом `source_assets.py` с замером BPM и поиском дропа.

## Открытые вопросы

1. Цена в ролике: 500 000 или 100 000 so'm (сейчас 500 000).
2. Запись узбекского голоса — тайминги в `README-delivery.md`.
3. 5 живых клипов с телефона (касса, кухня, зал, владелец) вместо стокового b-roll.
4. ОФД: сказано «OFD konturiga tayyor», потому что в проекте `fiscal_enabled=False`.
