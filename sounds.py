# sounds.py — optional feedback (Termux-friendly)
# Uses termux-media-player if present; otherwise vibrate + terminal bell.
from __future__ import annotations
import os, sys, subprocess, wave, struct, math
from pathlib import Path

TONE_HZ = {
    "buy": 880.0,
    "sell": 440.0,
    "wait": 330.0,
    "done": 660.0,
    "error": 220.0,
}
DUR_MS = {
    "buy": 180,
    "sell": 180,
    "wait": 90,
    "done": 120,
    "error": 250,
}
CACHE = Path(".sfx_cache")

def _have(cmd: str) -> bool:
    from shutil import which
    return which(cmd) is not None

def ensure_sounds():
    CACHE.mkdir(exist_ok=True)
    for name, hz in TONE_HZ.items():
        p = CACHE / f"{name}.wav"
        if not p.exists():
            _make_tone(str(p), hz, DUR_MS[name])

def _make_tone(path: str, hz: float, ms: int):
    fr = 44100
    n = int(fr * ms / 1000.0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fr)
        for i in range(n):
            t = i / fr
            val = int(32767.0 * 0.35 * math.sin(2*math.pi*hz*t))
            w.writeframes(struct.pack("<h", val))

def _wav(name: str) -> str:
    return str((CACHE / f"{name}.wav").resolve())

def _vibrate(ms: int):
    if _have("termux-vibrate"):
        try:
            subprocess.run(["termux-vibrate","-d",str(ms)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def play_sound(event: str, extra_vibe: bool=False):
    evt = (event or "done").lower()
    if evt not in TONE_HZ:
        evt = "done"
    ensure_sounds()
    wav = _wav(evt)

    if _have("termux-media-player"):
        try:
            # stop any prior
            subprocess.run(["termux-media-player","stop"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["termux-media-player","play", wav], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if extra_vibe:
                _vibrate(60)
            return
        except Exception:
            pass

    # fallback: vibrate + ASCII bell
    _vibrate(120)
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass
    if extra_vibe:
        _vibrate(60)

# Convenience wrappers
def sfx_buy():  play_sound("buy", True)
def sfx_sell(): play_sound("sell", True)
def sfx_wait(): play_sound("wait")
def sfx_error():play_sound("error", True)
def sfx_done(): play_sound("done")
