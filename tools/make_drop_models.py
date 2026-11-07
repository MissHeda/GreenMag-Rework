"""Writes the models this mod's items show when they lie on the ground, as plain MLOD P3D, and their texture.

    python tools/make_drop_models.py [--faces FACES_FOLDER] [preview folder]

A loose round, a piece of linked belt and the speedloader, in real sizes, in metres, and every pack's carton: the
carton of its inventory picture, with its print, in three sizes (up to 20, up to 40 and up to 60 rounds). Its texture
is put together from the sides tools/render_pack_textures.py renders; without --faces the textures stay as they are.

How the game lays an item down, as its own (a3\\weapons_f\\ammo\\mag_firstaidkit.p3d, mag_map.p3d) show: centred on
the origin, flat along Z, which points up on the ground. Each model here is built standing (X across, Y up, Z along),
centred, and turned a quarter round X before it is written (lay_down).

The cartons' textures are put together here (Pillow) and made PAA with HEMTT. With a preview folder every model is also
written there as OBJ, mirrored the way the game shows it, with its texture as PNG.
"""

import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_mag_models import RVMAT, Model, normalise, texture, write_p3d  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "addons" / "items" / "data"
MATERIAL = "z\\gmr\\addons\\items\\data\\gmr_plain.rvmat"
MATERIAL_HANDLING = "z\\gmr\\addons\\handling\\data\\gmr_plain.rvmat"
PACKS = OUT / "packs"
PACKS_PATH = "z\\gmr\\addons\\items\\data\\packs"

import generate_items as ITEM_TABLE  # noqa: E402

# The carton of the inventory picture (render_items.CARTON), in metres: along, across, high. Bigger packs, same carton.
CARTON = (0.097, 0.0586, 0.0366)
CARTON_SCALES = {"s": 1.0, "m": 1.2, "l": 1.4}

BRASS = texture(0.78, 0.60, 0.26)
BRASS_DARK = texture(0.60, 0.44, 0.17)
COPPER = texture(0.72, 0.40, 0.20)
STEEL = texture(0.20, 0.21, 0.22)
POLYMER = texture(0.08, 0.08, 0.085)
POLYMER_LIGHT = texture(0.16, 0.16, 0.17)

# Where each side of the carton is on its texture: (left, top, width, height) in pixels; the plain board serves the
# sides without print (back, bottom, the end without the flap).
SIZE = 512
REGIONS = {
    "top": (0, 0, 349, 211),
    "front": (0, 211, 349, 132),
    "end": (0, 343, 211, 132),
    "plain": (360, 8, 144, 144),
}


# ----- Texture -----

def fibres(image, seed):
    """Fine grain of board and a slightly uneven colour, over print and all."""
    rng = random.Random(seed)
    grain = Image.effect_noise(image.size, 22).filter(ImageFilter.GaussianBlur(0.5)).load()
    patches = Image.effect_noise((image.width // 32, image.height // 32), 40).resize(image.size, Image.BICUBIC).load()
    out = image.convert("RGB")
    pixels = out.load()

    for y in range(out.height):
        for x in range(out.width):
            shift = (grain[x, y] - 128) * 0.05 + (patches[x, y] - 128) * 0.018 + rng.uniform(-1.5, 1.5)
            r, g, b = pixels[x, y]
            pixels[x, y] = (int(r + shift), int(g + shift * 0.9), int(b + shift * 0.7))

    return out


def carton_texture(faces, name):
    """The atlas of one pack's carton from the sides render_pack_textures.py rendered."""
    sides = {side: Image.open(faces / f"face_{name}_{side}.png").convert("RGBA") for side in ("top", "front", "end", "back")}
    back = sides["back"]
    # The board's own colour, from the middle of the plain back, also fills the round corners the bevel leaves open.
    board = back.getpixel((back.width // 2, back.height // 2))
    atlas = Image.new("RGBA", (SIZE, SIZE), board)

    for side in ("top", "front", "end"):
        left, top, w, h = REGIONS[side]
        flat = Image.new("RGBA", sides[side].size, board)
        flat.alpha_composite(sides[side])
        atlas.paste(flat.resize((w, h), Image.LANCZOS), (left, top))

    return fibres(atlas, sum(map(ord, name)))


def pack_names():
    for caliber, (_, _, _, _, variants) in ITEM_TABLE.CALIBERS.items():
        for variant in {"basic": None} | variants:
            yield f"{caliber}_{variant}"


def write_textures(faces, preview):
    """Every carton's PAA; the PNGs stay in the preview folder, else beside the faces."""
    PACKS.mkdir(parents=True, exist_ok=True)
    folder = preview or faces
    folder.mkdir(parents=True, exist_ok=True)

    for name in pack_names():
        png = folder / f"carton_{name}_co.png"
        carton_texture(faces, name).save(png)
        subprocess.run(["hemtt", "utils", "paa", "convert", str(png), str(PACKS / f"carton_{name}_co.paa")], check=True,
                       capture_output=True)

    print("carton textures written")
    return folder


# ----- Models -----

def lay_down(model):
    """Turns the model a quarter round X, so its Y (up while built) becomes the Z the game lays an item on."""
    model.points = [(x, -z, y) for x, y, z in model.points]
    return model


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mapped_box(model, size, surface, sides):
    """A box round the origin whose every side shows its region of the texture upright, seen from outside.
    sides: (outward normal, up, (left, top, width, height) as shares of the texture). The game's axes are left-handed,
    so seen from outside along -n with up U, right is U x (-n)."""
    half = [value / 2 for value in size]

    for normal, up, (left, top, rw, rh) in sides:
        right = cross(up, tuple(-value for value in normal))
        axis_n = [abs(value) for value in normal].index(1)
        axis_r = [abs(value) for value in right].index(1)
        axis_u = [abs(value) for value in up].index(1)
        corners = []
        uvs = []

        # Corners in the turning sense of Model.box: right then up, which with its winding faces outwards.
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            point = [0.0, 0.0, 0.0]
            point[axis_n] = half[axis_n] * normal[axis_n]
            point[axis_r] = right[axis_r] * su * half[axis_r]
            point[axis_u] = up[axis_u] * sv * half[axis_u]
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


def share(region):
    left, top, w, h = REGIONS[region]
    return left / SIZE, top / SIZE, w / SIZE, h / SIZE


def carton(surface, scale):
    """The picture's carton, standing: its length along Z, its front with the band towards +X, the flap's end at +Z.
    Blender's carton (render_items: length X, front -Y, lid +Z) becomes this one by (x, y, z) -> (-y, z, x), which
    mirrors it once: the game's left-handed axes mirror it back, so the print reads as in the picture."""
    model = Model()
    along, across, high = (value * scale for value in CARTON)
    sides = [
        ((0, 1, 0), (-1, 0, 0), share("top")),
        ((0, -1, 0), (1, 0, 0), share("plain")),
        ((1, 0, 0), (0, 1, 0), share("front")),
        ((-1, 0, 0), (0, 1, 0), share("plain")),
        ((0, 0, 1), (0, 1, 0), share("end")),
        ((0, 0, -1), (0, 1, 0), share("plain")),
    ]
    mapped_box(model, (across, high, along), surface, sides)
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
    args = sys.argv[1:]
    faces = None

    if "--faces" in args:
        at = args.index("--faces")
        faces = Path(args[at + 1])
        del args[at:at + 2]

    preview = Path(args[0]) if args else None
    OUT.mkdir(parents=True, exist_ok=True)
    PACKS.mkdir(parents=True, exist_ok=True)
    pngs = write_textures(faces, preview) if faces else None
    models = {
        "drop_round": round_model(),
        "drop_belt": belt_model(),
        "drop_speedloader": speedloader(),
    }

    (OUT / "gmr_plain.rvmat").write_text(RVMAT, encoding="utf-8", newline="\n")

    for name, model in models.items():
        if preview:
            write_preview(preview / f"{name}.obj", model, None)

        lay_down(model)
        write_p3d(OUT / f"{name}.p3d", model, MATERIAL)

    packs = []

    for name in pack_names():
        for size, scale in CARTON_SCALES.items():
            model = carton(f"{PACKS_PATH}\\carton_{name}_co.paa", scale)

            if preview and pngs and size == "s":
                write_preview(preview / f"pack_{name}.obj", model, pngs / f"carton_{name}_co.png")

            lay_down(model)
            write_p3d(PACKS / f"pack_{name}_{size}.p3d", model, MATERIAL)
            packs.append(f"pack_{name}_{size}")

    # The round in the right hand while loading (fnc_holdMagazine): along Z, the game's forward of a model, point first.
    held = Model()
    cartridge(held, (0, 0, 0), (0, 0, 1))
    write_p3d(ROOT / "addons" / "handling" / "data" / "round_hand.p3d", held, MATERIAL_HANDLING)

    def model_cfg(names):
        cfg = ["class CfgSkeletons {", "    class Default {", "        isDiscrete = 1;", '        skeletonInherit = "";',
               "        skeletonBones[] = {};", "    };", "};", "class CfgModels {", "    class Default {",
               '        sectionsInherit = "";', "        sections[] = {};", '        skeletonName = "";', "    };"]
        cfg += [f"    class {name}: Default {{}};" for name in names]
        cfg.append("};")
        return "\n".join(cfg) + "\n"

    (OUT / "model.cfg").write_text(model_cfg(models), encoding="utf-8", newline="\n")
    (PACKS / "model.cfg").write_text(model_cfg(packs), encoding="utf-8", newline="\n")
    print(f"{len(models)} drop models and {len(packs)} cartons written")


if __name__ == "__main__":
    main()
