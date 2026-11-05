"""Converts the rendered item pictures to PAA and draws the white action icons of the menus.

    blender -b --python tools/render_items.py -- RENDERS_FOLDER
    python tools/make_icons.py RENDERS_FOLDER

Without a folder it only draws the action icons.

Needs Pillow and the Arma 3 Tools' ImageToPAA (path below, or the environment variable IMAGETOPAA).
"""

import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "addons" / "items" / "data"
HANDLING = ROOT / "addons" / "handling" / "data"
TOOL = os.environ.get("IMAGETOPAA", r"D:\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe")

SIZE = 256
WHITE = (255, 255, 255, 255)


def cartridge(draw, cx, top, bottom, width, angle=0.0):
    """A round standing up: tip, shoulder, case and rim."""
    half = width / 2
    neck = top + (bottom - top) * 0.34
    shoulder = top + (bottom - top) * 0.44
    outline = [
        (cx - half * 0.20, top + 8), (cx + half * 0.20, top + 8), (cx + half * 0.58, neck), (cx + half * 0.58, neck + 3),
        (cx + half, shoulder), (cx + half, bottom - 10), (cx + half * 0.8, bottom - 7), (cx + half * 1.05, bottom - 4),
        (cx + half * 1.05, bottom), (cx - half * 1.05, bottom), (cx - half * 1.05, bottom - 4), (cx - half * 0.8, bottom - 7),
        (cx - half, bottom - 10), (cx - half, shoulder), (cx - half * 0.58, neck + 3), (cx - half * 0.58, neck),
    ]
    draw.polygon(rotated(outline, cx, (top + bottom) / 2, angle), fill=WHITE)


def rotated(points, cx, cy, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in points]


def magazine(draw, x, y, width, height, lean=26):
    """A curved rifle magazine seen from the side: feed lips on top, floor plate below."""
    steps = 14
    back = [(x + lean * (i / steps) ** 2, y + height * i / steps) for i in range(steps + 1)]
    front = [(px + width * (1 + 0.14 * i / steps), py) for i, (px, py) in enumerate(back)]
    draw.polygon(back + front[::-1], fill=WHITE)

    # Floor plate, with a gap above it, and the lips.
    draw.line([back[-2], front[-2]], fill=(0, 0, 0, 0), width=7)
    plate = back[-1][0] - 5, back[-1][1], front[-1][0] + 5, back[-1][1] + 13
    draw.rounded_rectangle(plate, 4, fill=WHITE)
    draw.rectangle([x + width * 0.16, y - 13, x + width * 0.84, y], fill=WHITE)

    # Two ribs down its side, the way a stamped body shows them.
    for share in (0.34, 0.66):
        rib = [(px + (fx - px) * share, py) for (px, py), (fx, _) in zip(back[2:-3], front[2:-3])]
        draw.line(rib, fill=(0, 0, 0, 0), width=7, joint="curve")


def arrow(draw, x, top, bottom, down=True, width=30, head=62, head_height=44):
    tip, tail = (bottom, top) if down else (top, bottom)
    base = tip - head_height if down else tip + head_height
    draw.rectangle([x - width / 2, min(tail, base), x + width / 2, max(tail, base)], fill=WHITE)
    draw.polygon([(x, tip), (x - head, base), (x + head, base)], fill=WHITE)


def carton(draw, x0, y0, x1, y1, open_lid):
    draw.rounded_rectangle([x0, y0, x1, y1], 8, outline=WHITE, width=16)

    if open_lid:
        draw.polygon([(x0, y0 + 8), (x0 - 34, y0 - 40), (x0 - 16, y0 - 50), (x0 + 22, y0 + 8)], fill=WHITE)
        draw.polygon([(x1, y0 + 8), (x1 + 34, y0 - 40), (x1 + 16, y0 - 50), (x1 - 22, y0 + 8)], fill=WHITE)
    else:
        draw.line([(x0, y0 + 42), (x1, y0 + 42)], fill=WHITE, width=12)
        draw.rectangle([(x0 + x1) / 2 - 18, y0 + 8, (x0 + x1) / 2 + 18, y0 + 60], fill=WHITE)


def belt(draw, x0, x1, y, rounds, gap_after=None):
    """Rounds side by side, held by links running across them."""
    step = (x1 - x0) / (rounds - 1)
    gap = 0

    for index in range(rounds):
        x = x0 + index * step + gap
        cartridge(draw, x, y - 72, y + 72, 25)
        draw.rounded_rectangle([x - 21, y - 2, x + 21, y + 21], 5, fill=(0, 0, 0, 0))
        draw.rounded_rectangle([x - 19, y + 1, x + 19, y + 18], 4, fill=WHITE)

        if index == gap_after:
            gap = 36


def action(kind):
    """White signs on nothing, the way the game's own menus draw theirs. Drawn large and scaled down for clean edges."""
    big = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(big)

    if kind == "fill":
        magazine(draw, 64, 104, 92, 120)
        cartridge(draw, 112, 2, 72, 22)
        arrow(draw, 196, 34, 138, True, 18, 30, 32)
    elif kind == "unload":
        magazine(draw, 64, 104, 92, 120)
        cartridge(draw, 112, 2, 72, 22)
        arrow(draw, 196, 34, 138, False, 18, 30, 32)
    elif kind == "unpack":
        carton(draw, 52, 132, 204, 240, True)

        for x, top, tilt in ((96, 28, -0.18), (128, 6, 0.0), (160, 28, 0.18)):
            cartridge(draw, x, top, top + 96, 24, tilt)
    elif kind == "pack":
        carton(draw, 40, 128, 216, 240, False)
        arrow(draw, 128, 10, 112, True, 28, 48, 36)
    elif kind == "ammo":
        for x in (72, 128, 184):
            cartridge(draw, x, 34, 222, 42)
    elif kind == "belt":
        belt(draw, 40, 216, 128, 5)
    elif kind == "split":
        belt(draw, 28, 192, 128, 5, 1)
    elif kind == "link":
        belt(draw, 28, 140, 128, 3)
        arrow_points = [(172, 128), (172, 98), (228, 128), (172, 158)]
        draw.polygon(arrow_points, fill=WHITE)
        draw.rectangle([150, 118, 176, 138], fill=WHITE)

    return big.resize((SIZE, SIZE), Image.LANCZOS)


def clean_edges(png, target):
    """Takes the light fringe off a picture: the edge pixel by pixel in, and the colour of what is solid pulled outward."""
    image = Image.open(png).convert("RGBA")
    alpha = image.getchannel("A").filter(ImageFilter.MinFilter(3))
    pixels = np.array(image, dtype=np.float32)
    solid = np.array(alpha, dtype=np.float32) > 200
    colour = pixels[:, :, :3] * solid[:, :, None]
    weight = solid.astype(np.float32)

    for _ in range(4):
        grown = sum(np.roll(np.roll(colour, y, 0), x, 1) for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        count = sum(np.roll(np.roll(weight, y, 0), x, 1) for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        fill = (weight == 0) & (count > 0)
        colour[fill] = grown[fill] / count[fill][:, None]
        weight[fill] = 1

    result = np.dstack((colour, np.array(alpha, dtype=np.float32))).clip(0, 255).astype(np.uint8)
    Image.fromarray(result, "RGBA").save(target)


def to_paa(png, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([TOOL, str(png), str(target)], check=True, capture_output=True)


def main():
    if not Path(TOOL).exists():
        sys.exit(f"ImageToPAA not found at {TOOL}")

    renders = sorted(Path(sys.argv[1]).glob("*.png")) if len(sys.argv) > 1 else []
    renders = [png for png in renders if not png.name.startswith("_")]

    with tempfile.TemporaryDirectory() as temp:
        ammo = Path(temp) / "action_ammo.png"
        action("ammo").save(ammo)
        to_paa(ammo, ROOT / "addons" / "compat_ace" / "data" / "action_ammo.paa")

        for png in renders:
            source = png

            # Thin bright edges show as a light rim at inventory size. The cartons are matte and keep theirs.
            if png.stem.startswith(("belt_", "round_", "speedloader")):
                source = Path(temp) / png.name
                clean_edges(png, source)

            to_paa(source, ITEMS / f"{png.stem}.paa")

        for kind in ("fill", "unload", "unpack", "pack", "belt", "split", "link"):
            png = Path(temp) / f"action_{kind}.png"
            action(kind).save(png)
            to_paa(png, HANDLING / f"{png.stem}.paa")

    print(f"{len(renders)} item pictures and the action icons written.")


if __name__ == "__main__":
    main()
