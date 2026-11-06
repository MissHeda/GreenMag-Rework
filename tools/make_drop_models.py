"""Writes the models this mod's items show when they lie on the ground, as plain MLOD P3D, and their texture.

    python tools/make_drop_models.py [preview folder]

A loose round, a printed carton of rounds in three sizes (up to 20, up to 40 and up to 60 rounds), a piece of linked
belt and the speedloader, all in real sizes, in metres.

How the game lays an item down, as its own (a3\\weapons_f\\ammo\\mag_firstaidkit.p3d, mag_map.p3d) show: centred on
the origin, flat along Z, which points up on the ground. Each model here is built standing (X across, Y up, Z along),
centred, and turned a quarter round X before it is written (lay_down).

The carton's texture is drawn here (Pillow) and made a PAA with HEMTT. With a preview folder every model is also
written there as OBJ, mirrored the way the game shows it, with its texture as PNG.
"""

import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_mag_models import RVMAT, Model, normalise, texture, write_p3d  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "addons" / "items" / "data"
MATERIAL = "z\\gmr\\addons\\items\\data\\gmr_plain.rvmat"
CARTON = "z\\gmr\\addons\\items\\data\\drop_carton_co.paa"

BRASS = texture(0.78, 0.60, 0.26)
BRASS_DARK = texture(0.60, 0.44, 0.17)
COPPER = texture(0.72, 0.40, 0.20)
STEEL = texture(0.20, 0.21, 0.22)
POLYMER = texture(0.08, 0.08, 0.085)
POLYMER_LIGHT = texture(0.16, 0.16, 0.17)

# Where each side of the carton is on its texture: (left, top, width, height), as shares of it.
ATLAS = {
    "top": (0.0, 0.0, 0.5, 1.0),
    "side": (0.5, 0.0, 0.5, 0.5),
    "end": (0.5, 0.5, 0.25, 0.5),
    "bottom": (0.75, 0.5, 0.25, 0.5),
}
SIZE = 1024


# ----- Texture -----

def font(name, size):
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def cardboard(width, height, seed):
    """Brown board with its fibres, a little uneven."""
    rng = random.Random(seed)
    image = Image.new("RGB", (width, height), (176, 138, 92))
    pixels = image.load()

    for y in range(height):
        row = rng.uniform(-6, 6)

        for x in range(width):
            grain = rng.uniform(-9, 9) + row
            r, g, b = pixels[x, y]
            pixels[x, y] = (int(r + grain), int(g + grain * 0.85), int(b + grain * 0.6))

    return image.filter(ImageFilter.GaussianBlur(0.6))


def draw_carton():
    atlas = Image.new("RGB", (SIZE, SIZE))

    def region(name):
        left, top, w, h = ATLAS[name]
        return int(left * SIZE), int(top * SIZE), int(w * SIZE), int(h * SIZE)

    # Top: the printed label, a band in olive, the tape over the lid's seam.
    x, y, w, h = region("top")
    top = cardboard(w, h, 1)
    d = ImageDraw.Draw(top)
    d.rectangle([int(w * 0.43), 0, int(w * 0.57), h], fill=(150, 112, 70))
    d.line([(w // 2, 0), (w // 2, h)], fill=(110, 80, 48), width=2)
    lx0, ly0, lx1, ly1 = int(w * 0.12), int(h * 0.2), int(w * 0.88), int(h * 0.8)
    d.rectangle([lx0, ly0, lx1, ly1], fill=(232, 228, 214), outline=(40, 40, 36), width=4)
    d.rectangle([lx0, int(h * 0.27), lx1, int(h * 0.33)], fill=(54, 84, 46))
    d.rectangle([lx0, int(h * 0.67), lx1, int(h * 0.73)], fill=(54, 84, 46))
    big = font("impact.ttf", 58)
    small = font("bahnschrift.ttf", 30)
    mono = font("consolab.ttf", 24)

    for text, face, at in (("CARTRIDGES", big, 0.40), ("BALL  -  LINKED OR LOOSE", small, 0.50), ("LOT GMR-26-1107", mono, 0.58)):
        d.text((w // 2, int(h * at)), text, font=face, fill=(28, 28, 26), anchor="mm")

    atlas.paste(top, (x, y))

    # Long side: stencilled print and the arrows that say which way is up.
    x, y, w, h = region("side")
    side = cardboard(w, h, 2)
    d = ImageDraw.Draw(side)
    d.text((w // 2, int(h * 0.46)), "AMMUNITION", font=font("impact.ttf", 60), fill=(44, 34, 24), anchor="mm")
    d.text((w // 2, int(h * 0.7)), "KEEP DRY  -  THIS SIDE UP", font=font("bahnschrift.ttf", 22), fill=(60, 46, 32), anchor="mm")
    d.line([(0, int(h * 0.12)), (w, int(h * 0.12))], fill=(120, 88, 54), width=3)
    d.line([(0, int(h * 0.88)), (w, int(h * 0.88))], fill=(120, 88, 54), width=3)
    atlas.paste(side, (x, y))

    # End: the flap with its fold and a small mark.
    x, y, w, h = region("end")
    end = cardboard(w, h, 3)
    d = ImageDraw.Draw(end)
    d.line([(0, int(h * 0.5)), (w, int(h * 0.5))], fill=(112, 82, 50), width=3)
    d.rectangle([int(w * 0.3), int(h * 0.18), int(w * 0.7), int(h * 0.38)], outline=(44, 34, 24), width=3)
    d.text((w // 2, int(h * 0.28)), "GM", font=font("impact.ttf", 40), fill=(44, 34, 24), anchor="mm")
    atlas.paste(end, (x, y))

    # Bottom: plain board.
    x, y, w, h = region("bottom")
    atlas.paste(cardboard(w, h, 4), (x, y))
    return atlas


def write_texture(preview):
    png = (preview or OUT) / "drop_carton_co.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    draw_carton().save(png)
    subprocess.run(["hemtt", "utils", "paa", "convert", str(png), str(OUT / "drop_carton_co.paa")], check=True,
                   capture_output=True)

    if preview is None:
        png.unlink()

    return png


# ----- Models -----

def lay_down(model):
    """Turns the model a quarter round X, so its Y (up while built) becomes the Z the game lays an item on."""
    model.points = [(x, -z, y) for x, y, z in model.points]
    return model


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mapped_box(model, centre, size, surface, regions):
    """A box whose every side shows its region of the texture upright, seen from outside. The game's axes are
    left-handed, so seen from outside along -n with up U, right is U x (-n)."""
    hx, hy, hz = (value / 2 for value in size)
    cx, cy, cz = centre
    sides = {
        "top": ((0, 1, 0), (0, 0, 1)),
        "bottom": ((0, -1, 0), (0, 0, -1)),
        "front": ((0, 0, 1), (0, 1, 0)),
        "back": ((0, 0, -1), (0, 1, 0)),
        "left": ((-1, 0, 0), (0, 1, 0)),
        "right": ((1, 0, 0), (0, 1, 0)),
    }

    for name, (normal, up) in sides.items():
        right = cross(up, tuple(-value for value in normal))
        half = {0: hx, 1: hy, 2: hz}
        axis_n = [abs(value) for value in normal].index(1)
        axis_r = [abs(value) for value in right].index(1)
        axis_u = [abs(value) for value in up].index(1)
        depth = half[axis_n] * normal[axis_n]
        w, h = half[axis_r], half[axis_u]
        corners = []
        uvs = []
        left, top, rw, rh = regions[name]

        # Corners in the turning sense of Model.box: right then up, which with its winding faces outwards.
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            point = [cx, cy, cz]
            point[axis_n] += depth
            point[axis_r] += right[axis_r] * su * w
            point[axis_u] += up[axis_u] * sv * h
            corners.append(tuple(point))
            uvs.append((left + (su + 1) / 2 * rw, top + (1 - (sv + 1) / 2) * rh))

        # Model.box's sides wind (low[i], low[j], high[j], high[i]); check against the outward normal and turn if not.
        a, b, c = corners[0], corners[1], corners[2]
        u = [b[k] - a[k] for k in range(3)]
        v = [c[k] - a[k] for k in range(3)]
        reversed_n = (u[2] * v[1] - u[1] * v[2], u[0] * v[2] - u[2] * v[0], u[1] * v[0] - u[0] * v[1])

        if sum(reversed_n[k] * normal[k] for k in range(3)) < 0:
            corners.reverse()
            uvs.reverse()

        model.face(tuple(corners), surface, uvs)


def carton(width, height, length):
    model = Model()
    regions = {
        "top": ATLAS["top"],
        "bottom": ATLAS["bottom"],
        "front": ATLAS["end"],
        "back": ATLAS["end"],
        "left": ATLAS["side"],
        "right": ATLAS["side"],
    }
    mapped_box(model, (0, 0, 0), (width, height, length), CARTON, regions)
    return model


def lathe(model, start, axis, profile, sides=14):
    """A round body along axis from start: profile is (distance, radius, surface) from the base to the tip."""
    axis = normalise(axis)
    helper = (1, 0, 0) if abs(axis[0]) < 0.9 else (0, 1, 0)
    u = normalise(cross(axis, helper))
    v = cross(axis, u)

    def ring(distance, radius):
        centre = [start[k] + axis[k] * distance for k in range(3)]
        return [tuple(centre[k] + (u[k] * math.cos(a) + v[k] * math.sin(a)) * radius for k in range(3))
                for a in (2 * math.pi * i / sides for i in range(sides))][::-1]

    rings = [ring(distance, radius) for distance, radius, _ in profile]

    for (low, high), (_, _, surface) in zip(zip(rings, rings[1:]), profile[1:]):
        model.sweep([low, high], surface, caps=False)

    model.cap(rings[0], profile[0][2], bottom=True)

    if profile[-1][1] > 0.0002:
        model.cap(rings[-1], profile[-1][2], bottom=False)


def cartridge(model, middle, along, length=0.057, radius=0.0048):
    """A rifle round: rim, extractor groove, case, shoulder, neck, and the bullet's ogive to its point."""
    start = tuple(middle[k] - along[k] * length / 2 for k in range(3))
    r = radius
    profile = [
        (0.0, r * 0.98, BRASS_DARK),
        (length * 0.022, r * 0.98, BRASS_DARK),
        (length * 0.03, r * 0.8, BRASS_DARK),
        (length * 0.05, r * 0.8, BRASS_DARK),
        (length * 0.06, r, BRASS),
        (length * 0.56, r * 0.94, BRASS),
        (length * 0.62, r * 0.66, BRASS),
        (length * 0.68, r * 0.62, BRASS),
        (length * 0.70, r * 0.6, COPPER),
        (length * 0.82, r * 0.52, COPPER),
        (length * 0.92, r * 0.32, COPPER),
        (length * 0.98, r * 0.1, COPPER),
        (length, 0.0, COPPER),
    ]
    lathe(model, start, along, profile)


def round_model():
    model = Model()
    cartridge(model, (0, 0, 0), (1, 0, 0))
    return model


def belt_model(rounds=9):
    """A short piece of 7.62 belt: rounds side by side, each held by its steel link, the links overlapping."""
    model = Model()
    pitch = 0.0125
    length = 0.071
    radius = 0.0055

    for index in range(rounds):
        x = (index - (rounds - 1) / 2) * pitch
        cartridge(model, (x, 0, 0.004), (0, 0, 1), length, radius)
        # The link: a loop round the case and a tab reaching to the next round.
        lathe(model, (x, 0, -0.016), (0, 0, 1), [
            (0.0, radius * 1.18, STEEL), (0.014, radius * 1.18, STEEL), (0.014, radius * 1.02, STEEL),
        ], sides=12)
        model.box((x + pitch / 2, -radius * 0.9, -0.008), (pitch * 0.55, 0.0012, 0.006), STEEL)

    return model


def speedloader():
    """A rifle magazine loader: a sleeve over the magazine's top, its thumb plunger and grip ribs."""
    model = Model()
    model.box((0, 0, 0), (0.030, 0.07, 0.066), POLYMER)
    model.box((0, 0.039, -0.008), (0.014, 0.008, 0.03), POLYMER_LIGHT)

    for index in range(5):
        model.box((0.0155, -0.02 + index * 0.009, 0), (0.0012, 0.004, 0.05), POLYMER_LIGHT)
        model.box((-0.0155, -0.02 + index * 0.009, 0), (0.0012, 0.004, 0.05), POLYMER_LIGHT)

    return model


def write_preview(path, model, png):
    """OBJ mirrored in X as the game's left-handed axes show it, with its texture; v flipped for OBJ."""
    surfaces = sorted({surface for _, surface in model.faces})
    lines = [f"mtllib {path.stem}.mtl"]
    lines += [f"v {-x:.5f} {y:.5f} {z:.5f}" for x, y, z in model.points]
    count = 0

    for surface in surfaces:
        lines.append(f"usemtl m{surfaces.index(surface)}")

        for index, (corners, s) in enumerate(model.faces):
            if s != surface:
                continue

            uvs = model.uvs.get(index)

            if uvs:
                for u, v in uvs:
                    lines.append(f"vt {u:.5f} {1 - v:.5f}")

                refs = [f"{i + 1}/{count + n + 1}" for n, i in enumerate(corners)]
                count += len(uvs)
            else:
                refs = [str(i + 1) for i in corners]

            lines.append("f " + " ".join(refs))

    path.write_text("\n".join(lines) + "\n")
    mtl = []

    for index, surface in enumerate(surfaces):
        mtl.append(f"newmtl m{index}")

        if surface.endswith(".paa"):
            mtl += ["Kd 1 1 1", f"map_Kd {png.as_posix()}"]
        else:
            r, g, b = surface.split("color(")[1].split(",")[:3]
            mtl.append(f"Kd {r} {g} {b}")

    path.with_suffix(".mtl").write_text("\n".join(mtl) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    preview = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    png = write_texture(preview)
    models = {
        "drop_round": round_model(),
        "drop_pack_s": carton(0.052, 0.030, 0.068),
        "drop_pack_m": carton(0.060, 0.045, 0.078),
        "drop_pack_l": carton(0.068, 0.060, 0.090),
        "drop_belt": belt_model(),
        "drop_speedloader": speedloader(),
    }

    (OUT / "gmr_plain.rvmat").write_text(RVMAT, encoding="utf-8", newline="\n")

    for name, model in models.items():
        if preview:
            write_preview(preview / f"{name}.obj", model, png)

        lay_down(model)
        write_p3d(OUT / f"{name}.p3d", model, MATERIAL)

    cfg = ["class CfgSkeletons {", "    class Default {", "        isDiscrete = 1;", '        skeletonInherit = "";',
           "        skeletonBones[] = {};", "    };", "};", "class CfgModels {", "    class Default {",
           '        sectionsInherit = "";', "        sections[] = {};", '        skeletonName = "";', "    };"]
    cfg += [f"    class {name}: Default {{}};" for name in models]
    cfg.append("};")
    (OUT / "model.cfg").write_text("\n".join(cfg) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(models)} drop models and their texture written: {', '.join(models)}")


if __name__ == "__main__":
    main()
