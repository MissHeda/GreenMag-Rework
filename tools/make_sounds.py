"""Synthesizes every sound of the mod from what really makes it.

    python tools/make_sounds.py

Writes 16 bit mono WAVs to addons/handling/sounds. Needs numpy. Each sound is built from parts: a short hard transient for
the moment two things hit, the ringing partials of the metal, a low thump of the body they sit in, and shaped noise for
scraping, cardboard and cloth. A close room and a little saturation put it in the hand, and keep the attack hard.
"""

from pathlib import Path

import numpy as np

RATE = 44100
OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "sounds"


def buffer(seconds):
    return np.zeros(int(seconds * RATE))


def add(target, sound, at):
    first = int(at * RATE)
    end = min(len(target), first + len(sound))

    if first < len(target):
        target[first:end] += sound[:end - first]


def band(signal, low, high):
    """Keeps only what lies between two frequencies, with soft edges."""
    spectrum = np.fft.rfft(signal)
    frequency = np.fft.rfftfreq(len(signal), 1 / RATE)
    keep = np.clip((frequency - low * 0.7) / (low * 0.3 + 1), 0, 1) * np.clip((high * 1.3 - frequency) / (high * 0.3 + 1), 0, 1)
    return np.fft.irfft(spectrum * keep, len(signal))


def noise(seconds, low, high, rng, level=1.0, attack=0.0005, decay=None):
    """Band limited noise with a fast attack, falling away by decay if given."""
    t = np.arange(int(seconds * RATE)) / RATE
    signal = band(rng.standard_normal(len(t)), low, high)
    signal = signal / (np.max(np.abs(signal)) or 1)
    envelope = np.minimum(t / attack, 1.0)

    if decay:
        envelope = envelope * np.exp(-t / decay)

    return signal * envelope * level


def partial(frequency, level, decay, rng):
    t = np.arange(int(min(decay * 8, 0.8) * RATE)) / RATE
    return np.sin(2 * np.pi * frequency * t + rng.uniform(0, 6.28)) * np.exp(-t / decay) * level


def thump(frequency, level, decay, drop=0.35):
    """A hit body: the pitch falls right after the hit."""
    t = np.arange(int(min(decay * 8, 0.6) * RATE)) / RATE
    phase = 2 * np.pi * np.cumsum(frequency * (1 + drop * np.exp(-t / 0.006))) / RATE
    return np.sin(phase) * np.exp(-t / decay) * level * np.minimum(t / 0.0004, 1.0)


def hit(target, at, level, rng, modes, body, bright=(2500, 14000)):
    """Two hard things meeting: a click, the metal ringing, the body behind them."""
    add(target, noise(0.012, bright[0], bright[1], rng, level, decay=0.0013), at)

    for frequency, amount, decay in modes:
        add(target, partial(frequency * rng.uniform(0.985, 1.015), amount * level, decay, rng), at)

    for frequency, amount, decay in body:
        add(target, thump(frequency, amount * level, decay), at)


def save(name, signal, peak=0.9, drive=1.6):
    """A close room, some saturation for punch, level, and clean ends."""
    wet = signal.copy()

    for delay, gain in ((0.0029, 0.20), (0.0053, 0.15), (0.0091, 0.10), (0.0147, 0.06), (0.0233, 0.03)):
        offset = int(delay * RATE)
        wet[offset:] += signal[:-offset] * gain

    wet = wet / (np.max(np.abs(wet)) or 1)
    wet = np.tanh(wet * drive) / np.tanh(drive)
    fade = int(0.006 * RATE)
    wet[-fade:] *= np.linspace(1, 0, fade)
    samples = (wet / np.max(np.abs(wet)) * peak * 32767).astype(np.int16)

    import wave

    with wave.open(str(OUT / f"{name}.wav"), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(RATE)
        file.writeframes(samples.tobytes())


def round_in(step, steps, rng):
    """A round pressed past the feed lips. The fuller the magazine, the tighter the spring and the higher and harder the snap."""
    fill = step / (steps - 1)
    out = buffer(0.20)
    snap = 0.040 - 0.010 * fill + rng.uniform(-0.002, 0.002)

    # The rim touches down, it slides over the lips against the spring, and it snaps home.
    hit(out, 0.0, 0.28, rng, ((5200, 0.10, 0.004),), ((520, 0.14, 0.006),), (4000, 15000))
    add(out, noise(snap, 2200, 9000, rng, 0.11 + 0.08 * fill, attack=0.008), 0.002)

    pitch = 1.0 + 0.26 * fill
    hit(
        out, snap, 1.0, rng,
        ((2150 * pitch, 0.42, 0.013), (3420 * pitch, 0.34, 0.010), (5100 * pitch, 0.24, 0.007), (7600 * pitch, 0.12, 0.004)),
        ((215 * pitch, 0.62, 0.021), (430 * pitch, 0.30, 0.012)),
    )

    # The spring answers, and the rounds inside shift by a hair.
    add(out, partial(138 * pitch, 0.10, 0.03, rng), snap + 0.002)
    add(out, noise(0.012, 3000, 11000, rng, 0.10, decay=0.003), snap + 0.016)
    return out


def round_out(step, steps, rng):
    """A round thumbed out of the lips, and landing on the others: a slide, a tick, a bright tink of brass."""
    fill = step / (steps - 1)
    out = buffer(0.24)
    pitch = 0.92 + 0.20 * fill

    add(out, noise(0.030, 1800, 7000, rng, 0.20, attack=0.006), 0.0)
    hit(out, 0.028, 0.72, rng, ((2950 * pitch, 0.30, 0.009), (4500 * pitch, 0.22, 0.006)), ((300 * pitch, 0.30, 0.012),))

    for at, level, frequency in ((0.082, 0.42, 6100), (0.118, 0.20, 6900), (0.140, 0.09, 6400)):
        hit(out, at, level, rng, ((frequency, 0.40, 0.022), (frequency * 1.51, 0.22, 0.014), (frequency * 0.62, 0.16, 0.018)), (), (5000, 16000))

    return out


def belt_link(rng):
    """A link seating on the next round: a clipped metal clack with a touch of chain behind it."""
    out = buffer(0.16)
    hit(out, 0.0, 1.0, rng, ((1780, 0.26, 0.012), (2860, 0.28, 0.009), (4300, 0.18, 0.006)), ((190, 0.32, 0.016),))

    for at, level in ((0.034, 0.26), (0.058, 0.13)):
        hit(out, at + rng.uniform(-0.004, 0.004), level, rng, ((3300 * rng.uniform(0.9, 1.1), 0.20, 0.006),), ())

    return out


def magazine_done(rng):
    """The magazine is full: the last round settles, then two solid taps in the palm, and a small ring of the tight spring."""
    out = buffer(0.50)

    for at, level in ((0.0, 1.0), (0.120, 0.82)):
        hit(out, at, level, rng, ((1380, 0.14, 0.03), (2210, 0.14, 0.022), (3380, 0.09, 0.014)), ((128, 0.95, 0.052), (262, 0.42, 0.024)), (1500, 9000))
        add(out, noise(0.03, 300, 1800, rng, 0.30 * level, decay=0.008), at)

    # What makes it feel finished: a clean, bright ring after the taps.
    for frequency, level, decay in ((3520, 0.13, 0.09), (5280, 0.08, 0.07), (7040, 0.04, 0.05)):
        add(out, partial(frequency, level, decay, rng), 0.125)

    return out


def magazine_empty(rng):
    """The last round is out: the follower jumps up and the empty body rings hollow."""
    out = buffer(0.36)
    hit(out, 0.0, 0.9, rng, ((1120, 0.22, 0.06), (1760, 0.20, 0.05), (2840, 0.12, 0.03), (4200, 0.06, 0.02)), ((175, 0.55, 0.05),))
    hit(out, 0.085, 0.35, rng, ((1980, 0.16, 0.03),), ((240, 0.25, 0.02),))
    return out


def belt_done(rng):
    """The belt lies in the box: links settling, then the lid."""
    out = buffer(0.50)
    at = 0.0

    for step in range(5):
        hit(out, at, 0.34 + 0.05 * step, rng, ((2300 * rng.uniform(0.9, 1.1), 0.22, 0.010),), ((210, 0.16, 0.012),))
        at += 0.034 + 0.007 * step

    hit(out, at + 0.03, 1.0, rng, ((880, 0.24, 0.05), (1460, 0.20, 0.04), (2380, 0.12, 0.022)), ((112, 0.95, 0.06), (225, 0.42, 0.03)), (1200, 8000))
    return out


def grab(rng):
    """Taking the magazine in hand: cloth, then a light knock against the palm."""
    out = buffer(0.24)
    add(out, noise(0.11, 900, 6000, rng, 0.20, attack=0.03, decay=0.045), 0.0)
    hit(out, 0.085, 0.55, rng, ((1900, 0.10, 0.012),), ((170, 0.55, 0.03), (340, 0.20, 0.014)), (1500, 7000))
    return out


def cancel(rng):
    """Stopped halfway: the hand comes away, a dull pat."""
    out = buffer(0.18)
    add(out, noise(0.07, 700, 4000, rng, 0.14, attack=0.015, decay=0.03), 0.0)
    hit(out, 0.03, 0.42, rng, (), ((150, 0.45, 0.028),), (900, 4000))
    return out


def denied(rng):
    """It will not go in: two dull knocks of metal on metal, dead and short."""
    out = buffer(0.22)

    for at, level in ((0.0, 1.0), (0.095, 0.74)):
        hit(out, at, level, rng, ((640, 0.20, 0.012), (1040, 0.12, 0.008)), ((118, 0.72, 0.024),), (800, 3800))

    return out


def drop_item(rng):
    """Ammunition dropped on a magazine: it lands in the hand, ready."""
    out = buffer(0.20)
    hit(out, 0.0, 0.8, rng, ((2500, 0.14, 0.012), (3900, 0.10, 0.008)), ((190, 0.5, 0.026),))
    hit(out, 0.05, 0.3, rng, ((4700, 0.16, 0.012),), ())
    return out


def clatter(out, at, count, span, rng, level=0.6):
    """Rounds falling and rolling onto each other: brass tinks, thick at first and thinning out."""
    moments = np.sort(rng.uniform(0, 1, count) ** 1.6) * span

    for moment in moments:
        frequency = rng.uniform(4300, 7400)
        amount = level * rng.uniform(0.35, 1.0) * np.exp(-moment / span * 1.2)
        hit(out, at + moment, amount, rng, ((frequency, 0.34, 0.020), (frequency * 1.47, 0.20, 0.012), (frequency * 0.61, 0.14, 0.016)), ((360, 0.10, 0.008),), (5000, 16000))


def pack_open(rng):
    """The carton: the flap tears, then the rounds pour out into the hand."""
    out = buffer(0.95)
    t = np.arange(int(0.26 * RATE)) / RATE
    tear = noise(0.26, 900, 7500, rng, 0.55, attack=0.012)
    flutter = 0.45 + 0.55 * np.abs(band(rng.standard_normal(len(t)), 25, 180))
    add(out, tear * flutter / np.max(flutter) * np.minimum(1, (0.26 - t) / 0.06), 0.0)
    add(out, thump(190, 0.35, 0.03), 0.255)
    clatter(out, 0.285, 22, 0.52, rng)
    return out


def pack_close(rng):
    """Rounds slid into a carton, the flap tucked in."""
    out = buffer(0.55)
    clatter(out, 0.0, 10, 0.20, rng, 0.42)
    add(out, noise(0.13, 700, 5200, rng, 0.40, attack=0.02, decay=0.07), 0.20)
    add(out, thump(150, 0.85, 0.05), 0.325)
    add(out, noise(0.03, 500, 2600, rng, 0.40, decay=0.009), 0.325)
    return out


def belt_split(rng):
    """A link pulled apart: a little strain, the pin lets go, and the two ends drop."""
    out = buffer(0.42)
    add(out, noise(0.07, 2500, 7500, rng, 0.14, attack=0.04), 0.0)
    hit(out, 0.07, 1.0, rng, ((2420, 0.34, 0.03), (3950, 0.28, 0.022), (6100, 0.15, 0.012)), ((230, 0.30, 0.016),))
    clatter(out, 0.17, 6, 0.18, rng, 0.34)
    return out


def belt_combine(rng):
    """Two belts joined: a run of links zipping together, and the last one locks."""
    out = buffer(0.60)
    at = 0.0
    gap = 0.058

    for step in range(7):
        hit(out, at, 0.34 + 0.05 * step, rng, ((1900 + 170 * step, 0.26, 0.010), (3100 + 240 * step, 0.20, 0.008)), ((205, 0.15, 0.012),))
        at += gap
        gap *= 0.90

    hit(out, at + 0.025, 1.0, rng, ((1260, 0.24, 0.05), (2120, 0.24, 0.035), (3460, 0.16, 0.024)), ((130, 0.85, 0.05), (260, 0.34, 0.025)), (1500, 9000))
    return out


def belt_feed(rng):
    """A belt laid into a running gun: the feed tray takes it, the cover comes down, ka-chunk."""
    out = buffer(0.60)
    hit(out, 0.0, 0.62, rng, ((1680, 0.28, 0.022), (2750, 0.24, 0.014)), ((170, 0.34, 0.02),))

    for at in (0.075, 0.115):
        hit(out, at, 0.32, rng, ((2300, 0.22, 0.010),), ())

    hit(out, 0.20, 1.0, rng, ((720, 0.30, 0.07), (1190, 0.26, 0.05), (1970, 0.18, 0.03), (3230, 0.10, 0.018)), ((92, 1.0, 0.075), (186, 0.48, 0.035)), (1200, 8000))
    hit(out, 0.285, 0.46, rng, ((1500, 0.20, 0.02),), ((140, 0.30, 0.02),))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    for old in OUT.glob("*.wav"):
        old.unlink()

    rng = np.random.default_rng(1104)

    for step in range(8):
        save(f"round_in_{step + 1}", round_in(step, 8, rng), 0.85)

    for step in range(6):
        save(f"round_out_{step + 1}", round_out(step, 6, rng), 0.72)

    for index in range(1, 5):
        save(f"belt_link_{index}", belt_link(rng), 0.72)

    for name, build, peak in (
        ("magazine_done", magazine_done, 0.98),
        ("magazine_empty", magazine_empty, 0.85),
        ("belt_done", belt_done, 0.95),
        ("grab", grab, 0.60),
        ("cancel", cancel, 0.55),
        ("denied", denied, 0.80),
        ("drop_item", drop_item, 0.78),
        ("pack_open", pack_open, 0.90),
        ("pack_close", pack_close, 0.85),
        ("belt_split", belt_split, 0.90),
        ("belt_combine", belt_combine, 0.92),
        ("belt_feed", belt_feed, 0.98),
    ):
        save(name, build(rng), peak)

    print(f"{len(list(OUT.glob('*.wav')))} sounds written.")


if __name__ == "__main__":
    main()
