"""
sound_fx.py — minimal sound/vibrate helpers for Termux.

- Generates tiny WAV tones on first run (no 3rd‑party libs).
- Plays with `termux-media-player` if present; otherwise falls back to:
  - short vibration (termux-vibrate), or
  - ASCII bell + print (last‑ditch).
"""

from __future__ import annotations
import os, sys, math, wave, struct, shutil, subprocess
from typing import Optional

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

# Map logical events -> (frequency Hz, duration ms)
TONE_MAP = {
    "buy":   (880, 180),   # A5 short
    "sell":  (494, 180),   # B4 short
    "wait":  (660, 120),   # E5 very short
    "error": (196, 350),   # G3 longer + low
    "done":  (1046, 220),  # C6
}

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _wav_path(name: str) -> str:
    return os.path.join(SOUNDS_DIR, f"{name}.wav")

def _generate_tone_wav(path: str, freq_hz: int, dur_ms: int, vol: float=0.35, rate: int=22050) -> None:
    """Write a mono 16-bit PCM sine tone WAV."""
    samples = int(rate * (dur_ms/1000.0))
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        for n in range(samples):
            s = vol * math.sin(2*math.pi*freq_hz*n/rate)
            w.writeframes(struct.pack('<h', int(max(-1.0, min(1.0, s)) * 32767)))

def ensure_sounds() -> None:
    _ensure_dir(SOUNDS_DIR)
    for name, (f, d) in TONE_MAP.items():
        p = _wav_path(name)
        if not os.path.exists(p):
            _generate_tone_wav(p, f, d)

def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def _vibrate(ms: int=80) -> None:
    if _have("termux-vibrate"):
        try:
            subprocess.run(["termux-vibrate", "-d", str(ms)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def play_sound(event: str, extra_vibe: bool=False) -> None:
    """
    event ∈ {'buy','sell','wait','error','done'}
    Best effort: termux-media-player -> vibrate -> ASCII bell.
    """
    evt = event.lower().strip()
    if evt not in TONE_MAP:
        evt = "done"

    ensure_sounds()
    wav = _wav_path(evt)

    if _have("termux-media-player"):
        try:
            # stop any prior playback channel to avoid overlap
            subprocess.run(["termux-media-player", "stop"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["termux-media-player", "play", wav], check=False)
        except Exception:
            # fall through to vibrate
            pass
    else:
        # No media player — make a short buzz
        _vibrate(120)
        # and ring terminal bell (often silent on phones, but harmless)
        try:
            sys.stdout.write("\a")
            sys.stdout.flush()
        except Exception:
            pass

    if extra_vibe:
        _vibrate(60)

# Tiny convenience wrappers
def sfx_buy():  play_sound("buy",  True)
def sfx_sell(): play_sound("sell", True)
def sfx_wait(): play_sound("wait")
def sfx_error():play_sound("error", True)
def sfx_done(): play_sound("done")
