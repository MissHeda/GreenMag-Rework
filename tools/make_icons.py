"""Draws the mod's own inventory and action icons and converts them to PAA.

    python tools/make_icons.py

Needs Pillow and the Arma 3 Tools' ImageToPAA (path below, or the environment variable IMAGETOPAA).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "addons" / "items" / "data"
HANDLING = ROOT / "addons" / "handling" / "data"
TOOL = os.environ.get("IMAGETOPAA", r"D:\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe")

SIZE = 256
BRASS = (205, 165, 80, 255)
BRASS_DARK = (150, 115, 50, 255)
COPPER = (180, 105, 65, 255)
GREEN = (85, 110, 65, 255)
GREEN_DARK = (55, 75, 45, 255)
RED = (165, 50, 40, 255)
WHITE = (255, 255, 255, 255)
GRAY = (70, 70, 70, 255)


def canvas():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def cartridge(draw, cx, top, bottom, width, tip=COPPER):
    """An upright cartridge: bullet, brass case, rim."""
    half = width / 2
    neck = top + (bottom - top) * 0.38

    draw.polygon([(cx, top), (cx + half * 0.75, neck), (cx - half * 0.75, neck)], fill=tip)
    draw.rectangle([cx - half, neck, cx + half, bottom], fill=BRASS)
    draw.rectangle([cx - half, neck, cx - half * 0.4, bottom], fill=BRASS_DARK)
    draw.rectangle([cx - half * 1.1, bottom - 8, cx + half * 1.1, bottom], fill=BRASS_DARK)


def round_icon(width, top, bottom):
    image, draw = canvas()
    cartridge(draw, SIZE / 2, top, bottom, width)
    return image


def shell_icon():
    image, draw = canvas()
    draw.rectangle([92, 40, 164, 170], fill=RED)
    draw.rectangle([92, 40, 112, 170], fill=(125, 35, 30, 255))
    draw.rectangle([92, 170, 164, 222], fill=BRASS)
    draw.rectangle([84, 212, 172, 222], fill=BRASS_DARK)
    return image


def pack_icon(size):
    image, draw = canvas()
    draw.rectangle([28, 72, 228, 214], fill=GREEN)
    draw.polygon([(28, 72), (64, 36), (228, 36), (228, 72)], fill=GREEN_DARK)
    draw.rectangle([28, 118, 228, 170], fill=(225, 220, 195, 255))
    font = ImageFont.load_default(size=48)
    text = str(size)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((128 - (box[2] - box[0]) / 2, 144 - (box[3] - box[1]) / 2 - box[1]), text, fill=GRAY, font=font)
    return image


def belt_icon():
    image, draw = canvas()

    for at, x in enumerate(range(32, 225, 32)):
        y = 58 + (at % 2) * 10
        cartridge(draw, x, y, y + 124, 18)
        draw.rectangle([x - 16, y + 62, x + 16, y + 80], fill=GRAY)

    return image


def speedloader_icon():
    image, draw = canvas()
    draw.rectangle([84, 30, 172, 150], fill=GRAY)
    draw.rectangle([104, 150, 152, 226], fill=(45, 45, 45, 255))
    cartridge(draw, 128, 62, 136, 28)
    return image


def action(kind):
    """White on transparent, for the ACE menu and the hold action."""
    image, draw = canvas()

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
        cartridge(draw, 128, 18, 150, 30, WHITE)
    elif kind == "pack":
        draw.rectangle([36, 104, 220, 226], outline=WHITE, width=14)
        draw.line([(36, 104), (128, 62), (220, 104)], fill=WHITE, width=14)
        draw.polygon([(128, 180), (96, 130), (160, 130)], fill=WHITE)
    elif kind == "belt":
        for x in range(32, 225, 48):
            draw.rectangle([x - 10, 52, x + 10, 204], fill=WHITE)
        draw.rectangle([16, 112, 240, 138], fill=WHITE)

    return image


def save(image, folder, name, tool, work):
    folder.mkdir(parents=True, exist_ok=True)
    png = work / f"{name}.png"
    image.save(png)
    subprocess.run([tool, str(png), str(folder / f"{name}.paa")], check=True, capture_output=True)


def main():
    if not Path(TOOL).exists():
        sys.exit(f"ImageToPAA not found at {TOOL}")

    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        items = {
            "round_pistol": round_icon(46, 72, 196),
            "round_rifle": round_icon(36, 20, 236),
            "round_heavy": round_icon(62, 12, 244),
            "round_shell": shell_icon(),
            "belt": belt_icon(),
            "speedloader": speedloader_icon(),
        } | {f"pack_{size}": pack_icon(size) for size in (10, 20, 30, 40, 50, 60)}

        for name, image in items.items():
            save(image, ITEMS, name, TOOL, work)

        for kind in ("fill", "unload", "unpack", "pack", "belt"):
            save(action(kind), HANDLING, f"action_{kind}", TOOL, work)

    print("Icons written.")


if __name__ == "__main__":
    main()
