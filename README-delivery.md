# MARJON — пакет роликов (v2 и v3)

Три готовых файла, один движок, одна сетка. Всё собирается кодом и пересобирается за ~20 минут при правке цены/текста.

| Файл | Что это | Когда использовать |
|---|---|---|
| **`marjon_reel_v2_9x16.mp4`** | 40 с, 1080×1920, 30 fps, музыка + SFX, узбекские караоке-субтитры | «полная» версия: органика в Reels, сайт, презентация клиенту |
| **`marjon_reel_16s_9x16.mp4`** | 16 с, тот же стиль, плотнее монтаж, крупнее цена и CTA | **платный трафик** (Meta / TikTok / Telegram Ads): 15 с — оптимум по стоимости досмотра |
| **`marjon_reel_v2_silent.mp4`** | 40 с, без звука | **мастер под запись голоса**: накладываете диктора в CapCut/Premiere, музыка и SFX — отдельно или из v2 |

Дополнительно: `cover_1080x1920.png`, `poster_pain.png`, `cover16.png` (обложки), `storyboard.png` / `storyboard16.png` (раскадровка по кадрам), `README-v2.md` (разбор техники и источников).

---

## Как записать голос поверх `marjon_reel_v2_silent.mp4`

Реплики уже разбиты по таймингу — читайте в темпе, дорожка сама «подскажет»:

| Время | Реплика (uz) |
|---|---|
| 0.35–4.85 | *Qancha kirdi, qancha chiqdi — aniq bilasizmi? Kassada bitta raqam, daftarda boshqa.* |
| 5.10–9.85 | *Chek yopilmadi, go'sht tugadi, smena noma'lum. Va hisobot — faqat ertaga. Har oy takrorlanadi.* |
| 10.15–13.55 | *Endi hammasi — bitta joyda. Bu Marjon.* |
| 13.75–24.35 | *Kassa, ofitsiant, oshxona — bitta bazada. Ombor, dostavka, xodimlar — real vaqtda. Moliya va fiskal chek — soliq.uz konturida. Bitta tizim. Bitta hisobot.* |
| 24.60–28.50 | *Internet uzildi? Ish to'xtamaydi. O'zbek va rus tilida. Click, Payme, Uzum.* |
| 28.80–32.70 | *Oylik obuna — 500 ming so'mdan. Cheklovsiz kassa va foydalanuvchilar.* |
| 33.10–40.00 | *Restoranni bugundan boshqaring. +998 99 160 6477 — qo'ng'iroq yoki Direct. Bepul namoyish — 15 daqiqa.* |

Запись: тихая комната, микрофон в 15 см, 2 дубля (энергичный / спокойный), нормализация в редакторе до −14 LUFS.
После записи пришлите длительность каждой фразы — подгоним `CUES` в `promo.html` и пересоберём (субтитры и въезды кадров синхронизируются точно).

---

## Что уже закрыто в звуке

- музыка Mixkit `134.mp3` (123 BPM, бесплатно для коммерции), обрезка по биту, фейды;
- 19 SFX-акцентов, привязанных к монтажу: whoosh на стыки сцен, tick на карточки боли, click на смену модулей, check на «доехавшую» цену, pop на кнопку CTA;
- нормализация **−14 LUFS, TP −1.3**, AAC 192 kbps 48 kHz — проходит требования Meta/TikTok по громкости;
- цвета: BT.709, `yuv420p`, `+faststart` — файл играет сразу, без «подгрузки».

---

## Сетка (одна и та же во всех версиях)

```
поля 96 px · ритм 24 px · safe-top 176 px · safe-bottom 480 px
типографика: 123 / 99 / 80 / 56 / 36 / 27 / 23 px (7 ступеней)
субтитры: 2 строки, караоке-подсветка, 470 px от низа
```

Проверить визуально: открыть `promo.html`, клавиша **G** — показывает поля и безопасные зоны.

---

## Пересборка

```bash
# 40-секундная версия
python3 render.py full A && python3 render.py full B && python3 render.py full C
python3 build.py encode

# 16-секундная версия
python3 render16.py && python3 build16.py
```
Перед полным рендером — быстрая проверка кадров: `python3 render.py probe 5.2 12.0 20.5 31.0`.

---

## Что осталось от вас

1. **Цена**: 500 000 or 100 000 so'm — сейчас везде 500 000 (совпадает с озвучкой), меняется в `promo.html` (`data-count-num`) и в `cut16.html` (`data-num`).
2. **Голос**: запись по таблице выше (или скажите — соберу версию с TTS-узбекским для теста).
3. **5 живых клипов** с телефона (ваша касса, кухня, зал, владелец) — вставлю вместо стокового b-roll, и ролик станет «про вашего клиента».
4. Подтвердить формулировки про ОФД: сейчас «OFD konturiga tayyor» — потому что в `CLAUDE.md` провайдер ещё не подключён (`fiscal_enabled=False`).
