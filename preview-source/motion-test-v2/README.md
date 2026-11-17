# Cannavaro motion test v2 (kinetic direction)

Silent 10.2s 1080p30 motion-graphics test in concept-a brand for Ahmed to judge
quality before a full ad. Direction approved by Ahmed after v1: fullscreen
closeups, big kinetic Arabic type (مواقع / محتوى / إعلانات), band-wipe
transitions, strong CANNAVARO finale with kicker وكالة دعاية وتسويق رقمي.

## Files
- render2.py — generates 306 PNG frames (PIL); run: python3 render2.py OUTDIR [start end]
- cannavaro-motion-test-v2.mp4 — encoded with: ffmpeg -framerate 30 -i frames/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart
- cairo-arabic-full.ttf — full Cairo variable font (weight axis 200-1000), OFL, from google/fonts
- cairo-arabic.woff2 — site subset, kept for reference only, NOT used by the renderer
- anton-latin.woff2 — Anton for Latin display

## Fix history
First v2 commit rendered Arabic via arabic_reshaper+get_display against the SITE
SUBSET woff2. The subset lacks many Arabic Presentation Forms-B glyphs, so several
letters (ا isolated, ى, إ, ك initial, ت isolated...) drew as hollow tofu boxes on
video. Fixed by switching the renderer to the full Cairo font + Pillow RAQM layout
engine (no manual reshaper; RAQM does shaping+bidi from raw logical Arabic). Every
Arabic word verified glyph-by-glyph from frames extracted from the encoded MP4.
