#!/usr/bin/env python3
"""Cannavaro full ad - original synthesized music + SFX, timed to render4.py.
Everything generated from scratch (numpy): no samples, no licensing concerns.
Output: audio4.wav (44.1kHz stereo, 21s).
"""
import numpy as np, wave, struct

SR = 44100
DUR = 21.4
N = int(SR * DUR)
t = np.arange(N) / SR
mix = np.zeros(N)

def add(buf, start):
    i = int(start * SR)
    j = min(N, i + len(buf))
    if j > i:
        mix[i:j] += buf[:j - i]

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

def tri(f, n):
    """mellow triangle-ish tone via odd harmonics."""
    x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + 0.22*np.sin(2*np.pi*3*f*x)/3 + 0.1*np.sin(2*np.pi*5*f*x)/5)

def pad(freq, start, dur, amp=0.05, attack=0.8, release=0.9, detune=1.0015):
    n = int(dur * SR)
    env = np.ones(n)
    a = int(attack * SR); r = int(release * SR)
    env[:a] = np.linspace(0, 1, a) ** 1.5
    env[-r:] = np.linspace(1, 0, r) ** 1.5
    sig = (tri(freq, n) + tri(freq * detune, n) + tri(freq / detune, n)) / 3
    add(sig * env * amp, start)

def bell(freq, start, amp=0.06, decay=1.6):
    n = int(decay * 3 * SR)
    x = np.arange(n) / SR
    env = np.exp(-x / decay * 3)
    sig = np.sin(2*np.pi*freq*x) + 0.3*np.sin(2*np.pi*freq*2.01*x)*np.exp(-x/ (decay))
    add(sig * env * amp, start)

def whoosh(start, dur=0.8, amp=0.12, rise=True, lo=300, hi=3200):
    from scipy.signal import butter, lfilter
    n = int(dur * SR)
    noise = np.random.default_rng(7).standard_normal(n)
    b, a = butter(2, [lo/(SR/2), min(hi/(SR/2), 0.95)], btype="band")
    noise = lfilter(b, a, noise)
    x = np.linspace(0, 1, n)
    env = (x ** 2) if rise else ((1 - x) ** 2)
    env *= np.sin(np.pi * x) ** 0.5
    add(noise * env * amp * 8, start)

def thump(start, amp=0.5, decay=0.55):
    n = int(decay * 4 * SR)
    x = np.arange(n) / SR
    f = 58 * np.exp(-x * 3) + 38
    phase = np.cumsum(2*np.pi*f/SR)
    sig = np.sin(phase) * np.exp(-x / decay * 3)
    add(sig * amp, start)

def shimmer(start, amp=0.05, decay=1.1):
    for i, f in enumerate([1568, 2093, 2637]):
        n = int(decay * 3 * SR)
        x = np.arange(n) / SR
        gliss = f * (1 + x * 0.03)
        phase = np.cumsum(2*np.pi*gliss/SR)
        add(np.sin(phase) * np.exp(-x/decay*3) * amp * (1 - i*0.25), start + i*0.03)

def tick(start, freq=1174, amp=0.11, decay=0.09):
    n = int(decay * 6 * SR)
    x = np.arange(n) / SR
    add(np.sin(2*np.pi*freq*x) * np.exp(-x/decay*3) * amp, start)

# ---------------- music bed: Dm - Bb - F - C (x2), 2.55s per chord
CHORDS = [[50, 53, 57], [46, 50, 53], [45, 48, 53], [43, 48, 52],
          [50, 53, 57], [46, 50, 53], [45, 48, 53], [48, 52, 55]]
CS = 2.55
for ci, chord in enumerate(CHORDS):
    st = 0.4 + ci * CS
    for nnote in chord:
        pad(midi(nnote), st, CS + 1.2, amp=0.042)
    pad(midi(chord[0] - 12), st, CS + 1.2, amp=0.05, attack=0.5)   # sub root
    bell(midi(chord[0] + 24), st + 0.1, amp=0.028)                  # top bell
# outro chord lift under CTA
for nnote in [50, 53, 57, 62]:
    pad(midi(nnote), 17.6, 3.8, amp=0.045, attack=1.2, release=1.6)
bell(midi(74), 17.9, amp=0.05, decay=2.0)

# ---------------- SFX (timings mirror render4.py)
whoosh(0.15, dur=0.7, amp=0.10)                 # hairline
shimmer(0.9, amp=0.045)                          # star twinkle
tick(2.25, freq=880, amp=0.07)                   # window content lands
whoosh(2.85, dur=0.8, amp=0.08)                  # thread 1
tick(3.75, freq=988, amp=0.06)                   # cards land
whoosh(4.75, dur=0.8, amp=0.08)                  # thread 2
for i in range(5):                               # bars rise
    tick(5.35 + i*0.1, freq=660 + i*60, amp=0.045, decay=0.07)
whoosh(8.6, dur=0.7, amp=0.07)                   # wave line
for i in range(6):                               # wave bars pulse
    tick(8.95 + i*0.12, freq=520 + (i % 3)*130, amp=0.04, decay=0.09)
tick(11.15, freq=1046, amp=0.09)                 # quick card A
tick(12.2, freq=1046, amp=0.09)                  # quick card B
whoosh(13.3, dur=0.8, amp=0.14, rise=True, lo=200, hi=4200)  # riser into finale
thump(14.12, amp=0.5)                            # name impact
whoosh(14.15, dur=1.3, amp=0.11, rise=False, lo=800, hi=5000) # light sweep
shimmer(15.55, amp=0.06, decay=1.4)              # star by the O
bell(midi(69), 16.45, amp=0.04, decay=1.8)       # kicker
tick(18.0, freq=1318, amp=0.08, decay=0.25)      # CTA

# ---------------- master: soft clip + normalize
mix = np.tanh(mix * 1.1)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89
stereo = np.stack([mix, mix], axis=1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open("audio4.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("audio4.wav", len(pcm)/SR, "s, peak", round(float(peak), 3))
