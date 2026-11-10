# Marjon — рекламный ролик (Instagram Reels, 9:16)

Ролик собран кодом: детерминированный движок (`seek(t)`) → покадровый рендер Playwright → ffmpeg.
Ничего не нужно перерисовывать руками: поменяли цену/текст — пересобрали за ~20 минут.

## Готовые файлы

| Файл | Что это |
|---|---|
| `marjon_reel_16s_9x16.mp4` | **16 с**, 1080×1920, 30 fps, музыка + SFX, караоке-субтитры (uz) — для платного трафика |
| `marjon_reel_v2_9x16.mp4` | **40 с**, тот же стиль — органика, сайт, презентация |
| `marjon_reel_v2_silent.mp4` | 40 с без звука — мастер под запись диктора |
| `preview_16s.mp4` / `preview_40s.mp4` | лёгкие превью (540×960) для быстрого просмотра |
| `cover16.png`, `cover_1080x1920.png`, `poster_pain.png` | обложки |
| `storyboard.png`, `storyboard16.png` | раскадровка (каждый N-й кадр) |

## Структура

```
promo.html      # 40 с: 7 сцен, сетка, субтитры (правки текста — здесь: SCENES, CUES)
cut16.html      # 16 с: та же сетка, плотнее монтаж
render.py       # probe / draft / full A|B|C  (покадровый рендер)
render16.py     # рендер 16-секундной версии
build.py        # музыка + SFX (loudnorm -14 LUFS) → mp4
build16.py      # то же для 16 с
source_assets.py# сбор b-roll/музыки/SFX (Mixkit) + замер BPM/дропа
assets/         # b-roll 720p, музыка, SFX, брендовые макеты модулей, шрифты Onest/JetBrains Mono
```

## Сборка

```bash
python3 render.py full A && python3 render.py full B && python3 render.py full C
python3 build.py encode

python3 render16.py && python3 build16.py
```

Проверка кадров без полного рендера: `python3 render.py probe 5.2 12.0 20.5 31.0`.

## Сетка

поля 96 px · ритм 24 px · safe-top 176 px · safe-bottom 480 px ·
типографика 123 / 99 / 80 / 56 / 36 / 27 / 23 px · субтитры 470 px от низа.

## Открытые вопросы

1. Цена: 500 000 or 100 000 so'm (сейчас 500 000 во всех версиях).
2. Запись узбекского голоса — тайминги реплик в `README-delivery.md`.
3. 5 живых клипов с телефона (касса, кухня, зал, владелец) вместо стокового b-roll.
4. Формулировка про ОФД: сейчас «OFD konturiga tayyor» (в проекте `fiscal_enabled=False`).

Аддитив: аудио/видео-ассеты — Mixkit (бесплатно для коммерческого использования, без атрибуции).
