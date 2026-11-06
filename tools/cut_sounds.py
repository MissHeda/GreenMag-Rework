"""Cuts this mod's sounds out of CC0 recordings and writes them as OGG to addons/handling/sounds.

    python tools/cut_sounds.py <loading recording> [<drop recording> ...]

The loading recording is BigSoundBank's "Gun, loading #4" (sound 1991): a pistol magazine being loaded. Its single
clicks become the rounds going in (the game climbs their pitch as the spring tightens, CfgSounds), its rattle the hand
taking the magazine, its last clack a full magazine.

The drop recordings are BigSoundBank's cartridge cases falling on concrete, in this order: 9 mm #1 (1355), 5.56 mm #2
(1362), 5.56 mm #6 (1366), 7.62 mm #1 (1367), 7.62 mm #5 (1371). Each becomes a round falling out while unloading,
from just before its first hit until its bounces die away.

All of BigSoundBank's sounds are CC0 (https://bigsoundbank.com). Each cut gets a short fade at both ends and is brought
to the same loudness. Reads any format ffmpeg reads; needs ffmpeg on the PATH.
"""

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "sounds"
RATE = 48000

# name: start and end in seconds in the loading recording, where it has each alone.
CUTS = {
    "click_1": (0.2520, 0.3000),
    "click_2": (0.4695, 0.4900),
    "click_3": (0.4895, 0.5175),
    "click_4": (0.5180, 0.5440),
    "rattle": (0.4650, 0.5440),
    "seat": (0.5420, 0.6800),
}


def read(path):
    """Mono float samples at RATE."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def drop_span(samples):
    """From 5 ms before the first hit until the sound has fallen 50 dB below its loudest."""
    win = int(RATE * 0.005)
    env = np.sqrt(np.convolve(samples ** 2, np.ones(win) / win, mode="same"))
    loud = env.max()
    start = max(0, int(np.argmax(env > loud * 0.05)) - win)
    above = np.nonzero(env > loud * 10 ** (-50 / 20))[0]
    end = min(len(samples), int(above[-1]) + win)
    return start, end


def write(part, name, temp, fade_out_seconds):
    part = part - part.mean()
    fade_in = int(RATE * 0.001)
    fade_out = min(int(RATE * fade_out_seconds), len(part) // 3)
    part[:fade_in] *= np.linspace(0, 1, fade_in)
    part[-fade_out:] *= np.linspace(1, 0, fade_out)
    part *= 0.89 / max(np.abs(part).max(), 1e-6)

    wav = Path(temp) / f"{name}.wav"

    with wave.open(str(wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes((part * 32767).astype("<i2").tobytes())

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "highpass=f=90",
                    "-c:a", "libvorbis", "-q:a", "7", str(OUT / f"{name}.ogg")], check=True)
    print(f"{name}.ogg  {len(part) / RATE:.3f} s")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    loading = read(sys.argv[1])

    with tempfile.TemporaryDirectory() as temp:
        for name, (start, end) in CUTS.items():
            write(loading[int(start * RATE):int(end * RATE)].copy(), name, temp, 0.006)

        for index, path in enumerate(sys.argv[2:], 1):
            samples = read(path)
            start, end = drop_span(samples)
            write(samples[start:end].copy(), f"drop_{index}", temp, 0.08)


if __name__ == "__main__":
    main()
