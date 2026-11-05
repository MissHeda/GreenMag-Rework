"""Synthesizes the sounds of a round going into and out of a magazine, a belt link and a finished magazine.

    python tools/make_sounds.py

Writes 16 bit mono WAVs to addons/handling/sounds, standard library only. A click is made of what it is in real life:
the round scraping past the feed lips, the snap as it seats against the spring, the ring of the metal parts and a
short thump from the magazine's body.
"""

import array
import math
import random
import wave
from pathlib import Path

RATE = 44100
OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "sounds"


def silence(seconds):
    return [0.0] * int(seconds * RATE)


def noise_burst(buffer, start, length, level, decay, brightness, rng):
    """Filtered noise; brightness 0..1 sets how much of the low part is taken away."""
    first = int(start * RATE)
    previous = 0.0

    for i in range(int(length * RATE)):
        t = i / RATE
        white = rng.uniform(-1, 1)
        high = white - previous * (1 - brightness)
        previous = white
        at = first + i

        if at < len(buffer):
            buffer[at] += high * level * math.exp(-t / decay) * min(1.0, t / 0.0006)


def ring(buffer, start, frequency, level, decay):
    """A decaying partial of something metal."""
    first = int(start * RATE)
    phase = random.random() * 6.28

    for i in range(int(min(decay * 7, 0.4) * RATE)):
        t = i / RATE
        at = first + i

        if at < len(buffer):
            buffer[at] += math.sin(2 * math.pi * frequency * t + phase) * level * math.exp(-t / decay)


def thump(buffer, start, frequency, level, decay):
    first = int(start * RATE)

    for i in range(int(min(decay * 7, 0.4) * RATE)):
        t = i / RATE
        at = first + i

        if at < len(buffer):
            # The pitch drops a little, as a hit body does.
            buffer[at] += math.sin(2 * math.pi * frequency * t * (1 - t * 2.0)) * level * math.exp(-t / decay)


def room(buffer):
    """A very short, close space, so it does not sound like it is inside the head."""
    wet = list(buffer)

    for delay, gain in ((0.0037, 0.20), (0.0071, 0.14), (0.0113, 0.09), (0.0173, 0.05)):
        offset = int(delay * RATE)

        for i in range(offset, len(buffer)):
            wet[i] += buffer[i - offset] * gain

    return wet


def save(name, buffer, peak):
    buffer = room(buffer)
    top = max(abs(value) for value in buffer) or 1
    samples = array.array("h", (int(value / top * peak * 32767) for value in buffer))

    with wave.open(str(OUT / f"{name}.wav"), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(RATE)
        file.writeframes(samples.tobytes())


def round_in(seed, pitch):
    rng = random.Random(seed)
    random.seed(seed)
    buffer = silence(0.20)
    snap = 0.042 + rng.uniform(-0.004, 0.004)

    # Scrape past the feed lips, then the snap as it seats.
    noise_burst(buffer, 0.0, snap + 0.004, 0.16, 0.030, 0.9, rng)
    noise_burst(buffer, snap, 0.008, 1.0, 0.0016, 0.95, rng)

    for frequency, level, decay in ((2380, 0.34, 0.016), (3710, 0.28, 0.012), (5230, 0.20, 0.008), (7900, 0.10, 0.005)):
        ring(buffer, snap, frequency * pitch * rng.uniform(0.98, 1.02), level, decay)

    thump(buffer, snap, 235 * pitch, 0.55, 0.020)
    thump(buffer, snap, 470 * pitch, 0.22, 0.011)
    return buffer


def round_out(seed, pitch):
    rng = random.Random(seed)
    random.seed(seed)
    buffer = silence(0.18)

    # The round is pushed forward and springs free: a slide, then a lighter tick.
    noise_burst(buffer, 0.0, 0.03, 0.22, 0.012, 0.9, rng)
    noise_burst(buffer, 0.026, 0.006, 0.7, 0.0012, 0.95, rng)

    for frequency, level, decay in ((3050, 0.26, 0.010), (4620, 0.20, 0.008), (6800, 0.10, 0.005)):
        ring(buffer, 0.026, frequency * pitch * rng.uniform(0.98, 1.02), level, decay)

    thump(buffer, 0.026, 300 * pitch, 0.20, 0.012)
    return buffer


def belt_link(seed):
    rng = random.Random(seed)
    random.seed(seed)
    buffer = silence(0.26)

    # Links settling: a few quick metallic ticks in a row.
    moment = 0.0

    for step in range(4):
        level = 0.55 + 0.45 * (step == 2)
        noise_burst(buffer, moment, 0.006, level, 0.0014, 0.9, rng)

        for frequency in (1850, 2960, 4400):
            ring(buffer, moment, frequency * rng.uniform(0.94, 1.06), 0.20 * level, 0.012)

        moment += rng.uniform(0.028, 0.05)

    thump(buffer, 0.06, 165, 0.30, 0.03)
    return buffer


def magazine_done():
    rng = random.Random(7)
    random.seed(7)
    buffer = silence(0.34)

    # Two heavy steps: the magazine tapped in the palm.
    for moment, level in ((0.0, 1.0), (0.105, 0.72)):
        noise_burst(buffer, moment, 0.012, 0.8 * level, 0.0025, 0.8, rng)
        thump(buffer, moment, 150, 0.85 * level, 0.042)
        thump(buffer, moment, 310, 0.36 * level, 0.02)

        for frequency, partial, decay in ((1420, 0.14, 0.03), (2210, 0.12, 0.02), (3390, 0.08, 0.012)):
            ring(buffer, moment, frequency, partial * level, decay)

    return buffer


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    for index, pitch in enumerate((1.0, 0.96, 1.04, 0.92), 1):
        save(f"round_in_{index}", round_in(index, pitch), 0.80)

    for index, pitch in enumerate((1.0, 0.95, 1.05), 1):
        save(f"round_out_{index}", round_out(index + 10, pitch), 0.65)

    for index in range(1, 4):
        save(f"belt_link_{index}", belt_link(index + 20), 0.75)

    save("magazine_done", magazine_done(), 0.95)
    print("Sounds written.")


if __name__ == "__main__":
    main()
