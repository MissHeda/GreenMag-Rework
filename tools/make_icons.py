"""Converts the rendered item pictures to PAA and draws the white action icons of the menus.

    blender -b --python tools/render_items.py -- RENDERS_FOLDER
    python tools/make_icons.py RENDERS_FOLDER

Needs Pillow and the Arma 3 Tools' ImageToPAA (path below, or the environment variable IMAGETOPAA).
"""

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


def cartridge(draw, cx, top, bottom, width):
    half = width / 2
    neck = top + (bottom - top) * 0.38

    draw.polygon([(cx, top), (cx + half * 0.75, neck), (cx - half * 0.75, neck)], fill=WHITE)
    draw.rectangle([cx - half, neck, cx + half, bottom], fill=WHITE)


def action(kind):
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    if kind == "fill":
        draw.rectangle([72, 120, 184, 232], outline=WHITE, width=14)
        draw.polygon([(128, 106), (84, 54), (112, 54), (112, 18), (144, 18), (144, 54), (172, 54)], fill=WHITE)
    elif kind == "unload":
        draw.rectangle([72, 120, 184, 232], outline=WHITE, width=14)
        draw.polygon([(128, 18), (84, 70), (112, 70), (112, 106), (144, 106), (144, 70), (172, 70)], fill=WHITE)
    elif kind == "unpack":
        draw.rectangle([36, 104, 220, 226], outline=WHITE, width=14)
        draw.line([(36, 104), (10, 60)], fill=WHITE, width=14)
        draw.line([(220, 104), (246, 60)], fill=WHITE, width=14)
        cartridge(draw, 128, 18, 150, 30)
    elif kind == "pack":
        draw.rectangle([36, 104, 220, 226], outline=WHITE, width=14)
        draw.line([(36, 104), (128, 62), (220, 104)], fill=WHITE, width=14)
        draw.polygon([(128, 180), (96, 130), (160, 130)], fill=WHITE)
    elif kind == "ammo":
        for x in (72, 128, 184):
            cartridge(draw, x, 30, 226, 40)
    elif kind == "belt":
        for x in range(32, 225, 48):
            draw.rectangle([x - 10, 52, x + 10, 204], fill=WHITE)
        draw.rectangle([16, 112, 240, 138], fill=WHITE)

    return image


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
    if len(sys.argv) < 2:
        sys.exit("Usage: make_icons.py RENDERS_FOLDER")

    if not Path(TOOL).exists():
        sys.exit(f"ImageToPAA not found at {TOOL}")

    renders = sorted(Path(sys.argv[1]).glob("*.png"))
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

        for kind in ("fill", "unload", "unpack", "pack", "belt"):
            png = Path(temp) / f"action_{kind}.png"
            action(kind).save(png)
            to_paa(png, HANDLING / f"{png.stem}.paa")

    print(f"{len(renders)} item pictures and 5 action icons written.")


if __name__ == "__main__":
    main()
