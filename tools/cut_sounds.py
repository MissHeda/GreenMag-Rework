"""Cuts this mod's sounds out of a CC0 recording and writes them as OGG to addons/handling/sounds.

    python tools/cut_sounds.py <recording.wav>

The recording is BigSoundBank's "Gun, loading #4" (sound 1991, CC0, https://bigsoundbank.com/gun-loading-4-s1991.html):
a pistol magazine being loaded, mono, 48 kHz, 24-bit. Its single clicks become the rounds going in (the game climbs
their pitch as the spring tightens, CfgSounds), its rattle the hand taking the magazine, its last clack a full
magazine. Each cut gets a short fade at both ends and is brought to the same loudness. Needs ffmpeg on the PATH.
"""

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "sounds"

# name: start and end in seconds, where the recording has it alone.
CUTS = {
    "click_1": (0.2520, 0.3000),
    "click_2": (0.4695, 0.4900),
    "click_3": (0.4895, 0.5175),
    "click_4": (0.5180, 0.5440),
    "rattle": (0.4650, 0.5440),
    "seat": (0.5420, 0.6800),
}


def read_24bit(path):
    w = wave.open(str(path))
    rate = w.getframerate()
    raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.uint8).reshape(-1, 3)
    value = raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16)
    value = np.where(value >= 1 << 23, value - (1 << 24), value)
    return value / float(1 << 23), rate


def main():
    source, rate = read_24bit(Path(sys.argv[1]))
    OUT.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp:
        for name, (start, end) in CUTS.items():
            part = source[int(start * rate):int(end * rate)].copy()
            part -= part.mean()
            fade_in = int(rate * 0.001)
            fade_out = min(int(rate * 0.006), len(part) // 3)
            part[:fade_in] *= np.linspace(0, 1, fade_in)
            part[-fade_out:] *= np.linspace(1, 0, fade_out)
            part *= 0.89 / max(np.abs(part).max(), 1e-6)

            wav = Path(temp) / f"{name}.wav"

            with wave.open(str(wav), "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(rate)
                out.writeframes((part * 32767).astype("<i2").tobytes())

            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "highpass=f=90",
                            "-c:a", "libvorbis", "-q:a", "7", str(OUT / f"{name}.ogg")], check=True)
            print(f"{name}.ogg  {end - start:.3f} s")


if __name__ == "__main__":
    main()
