# Cannavaro motion test v1 — editable source

Short 2D motion-graphics test (8.7s, 1920x1080, 30fps, silent) built on 2026-11-17 so the
concept-a brand motion style can be judged before producing the full ad. This directory is
internal source retention: it is not linked from any site page and is not part of the preview site.

## Contents
- `render.py` — frame renderer (PIL). All timing, layout, colors and text live here.
- `anton-latin.woff2`, `cairo-arabic.woff2` — the same self-hosted fonts the site uses
  (copied from `concept-a/fonts/`).
- `cannavaro-motion-test-v1.mp4` — the rendered output (H.264, yuv420p, faststart; WhatsApp-safe).

## Re-render
```
pip install pillow arabic-reshaper python-bidi
python3 render.py frames            # writes 261 PNG frames (8.7s @ 30fps)
ffmpeg -y -framerate 30 -i frames/%04d.png -c:v libx264 -preset slow -crf 19 \
  -pix_fmt yuv420p -movflags +faststart cannavaro-motion-test-v1.mp4
```

## Brand constants (match concept-a)
cream #FFF6EC · ink #141414 · orange #FF4D00 · yellow #FFD23F · mint #9EE6B8 ·
lavender #C9BCFF · pink #FFB3C7. Wordmark Anton, Arabic Cairo. Brand shadow = orange at
.045em/.045em like `.brand` text-shadow on the site.

## Timeline map (seconds, all constants at top of render.py)
- 0.15–1.10 star pops in; 3 cards (social post / browser / phone voice waveform) pop in scattered
- 1.00–2.95 storefront draws itself (stroke reveal) then fills fade in
- 2.80–3.90 cards fly into organized slots (easeOutBack)
- 4.55–5.35 cluster scales to 0.5, drifts down, fades to 25% as backdrop
- 5.00–6.30 CANNAVARO rises; orange shadow trails 0.24s behind and settles to (10,10)
- 6.30–7.15 Arabic kicker + sub line fade in; mint scribble swash draws under the word
- 5.50–6.20 star flies to sit by the final O, keeps spinning
- 7.15–8.70 hold (star keeps rotating, backdrop keeps a slow bob)

## Notes
- Fonts are loaded from the local woff2 files, so there is no fallback-font flash.
- No audio by design (visual quality benchmark). Voice/music get added in the full ad pass.
- Render is deterministic (fixed random seeds); same inputs give the same video.
