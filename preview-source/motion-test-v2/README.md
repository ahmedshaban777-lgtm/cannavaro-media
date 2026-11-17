# Cannavaro motion test v2 — editable source (stronger kinetic direction)

Second motion-graphics test (10.2s, 1920x1080, 30fps, silent), built 2026-11-17 after v1
was judged too simple for the agency's self-ad. Direction: fullscreen closeups, big kinetic
Arabic typography, band-wipe transitions, ink-background finale. Unlinked internal source
retention; not part of the preview site.

## Contents
- `render2.py` — frame renderer (PIL). All timing, layout, colors and text live here.
- `anton-latin.woff2`, `cairo-arabic.woff2` — site fonts (Cairo is variable; the big words
  use `set_variation_by_axes([900])`).
- `cannavaro-motion-test-v2.mp4` — rendered output (H.264, yuv420p, faststart; WhatsApp-safe).

## Re-render
```
pip install pillow arabic-reshaper python-bidi
python3 render2.py frames2            # 306 frames; accepts [start] [end] to split long runs
ffmpeg -y -framerate 30 -i frames2/%04d.png -c:v libx264 -preset slow -crf 19 \
  -pix_fmt yuv420p -movflags +faststart cannavaro-motion-test-v2.mp4
```

## Timeline map (constants S1..S4, T1..T3 at top of render2.py)
- 0.0–2.3  WEB: closeup browser (loading bar, sliding content), «مواقع» on mint block + WEBSITES
- 2.3–2.85 orange band wipe
- 2.85–5.05 CONTENT: three post cards snap-stack, «محتوى» on yellow block + CONTENT
- 5.05–5.6 mint band wipe (reverse direction)
- 5.6–7.5 ADS: closeup megaphone emitting star particles, growth chart bars, «إعلانات» on lavender
- 7.5–8.1 ink band wipe into finale
- 8.1–10.2 FINALE: ink bg; CANNAVARO cream letters drop one by one (stagger 55ms, easeOutBack),
  orange shadow trails each letter, impact shake on landings; star flies in and sticks by the O
  with a particle burst; orange scribble swash under the word; Arabic kicker + MEDIA•CONTENT•WEB.
  Camera holds a slow push-in throughout.

## Word/block system
`kinetic_word()` draws the colored block (expands with easeOutBack), then the word clip-reveals
from the bottom of its box, then the English caption slides up. Block is clamped inside margins;
words are shaped with arabic_reshaper + python-bidi.

## Notes
- Deterministic (fixed seeds); same inputs give the same video.
- Fonts loaded locally: no fallback-font flashes.
- No audio by design; voice/music belong to the full-ad pass.
- v1 (drawn-shop direction) is preserved in `preview-source/motion-test-v1/`.
