# Cannavaro motion test v3 (quiet luxury direction)

Silent 10.5s 1080p30 motion-graphics test in concept-a brand. Direction approved
by Ahmed 2026-11-17: chic and expressive ("عاوز حاجه شيك قوى ومعبره"), visuals
first, music chosen later to suit the picture, no voice yet. Charcoal stage, thin
cream linework, one orange thread connecting site -> content -> ads, star motif,
CANNAVARO finale with kicker وكالة دعاية وتسويق رقمي.

## Files
- render3.py — generates 315 PNG frames (PIL, 2x supersampled); run: python3 render3.py OUTDIR [start end]
- cannavaro-motion-test-v3.mp4 — encoded: ffmpeg -framerate 30 -i frames/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 21 -movflags +faststart
- cairo-arabic-full.ttf — full Cairo variable font (OFL, google/fonts); RAQM layout shapes Arabic (no reshaper; the site subset woff2 caused tofu, see motion-test-v2 README)
- anton-latin.woff2 — Anton for CANNAVARO

Every Arabic word verified glyph-by-glyph from frames extracted from the encoded MP4.
