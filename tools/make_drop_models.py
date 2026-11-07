"""Writes the models this mod's items show when they lie on the ground, as plain MLOD P3D, and their texture.

    python tools/make_drop_models.py [--faces FACES_FOLDER] [preview folder]

A loose round, a piece of linked belt and the speedloader, in real sizes, in metres, and every pack's carton: the
carton of its inventory picture, with its print, in three sizes (up to 20, up to 40 and up to 60 rounds). Its texture
is put together from the sides tools/render_pack_textures.py renders, made into worn, printed paperboard with a
normal map; without --faces the textures stay as they are. Every carton has a shadow volume LOD.

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

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_mag_models import RVMAT, Model, hull_box, normalise, texture, welded, write_p3d  # noqa: E402

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
# What the geometry LODs weigh, in kg, for the game to rest them on the ground: the small carton full, the rest.
CARTON_MASS = 0.35
DROP_MASS = {"drop_round": 0.05, "drop_belt": 0.3, "drop_speedloader": 0.1, "drop_clip_10": 0.15, "drop_clip_5": 0.15}

BRASS = texture(0.78, 0.60, 0.26)
BRASS_DARK = texture(0.60, 0.44, 0.17)
COPPER = texture(0.72, 0.40, 0.20)
STEEL = texture(0.20, 0.21, 0.22)
POLYMER = texture(0.08, 0.08, 0.085)
POLYMER_LIGHT = texture(0.16, 0.16, 0.17)
CLIP_STEEL = texture(0.56, 0.57, 0.58)
GUIDE_STEEL = texture(0.34, 0.35, 0.36)

# Where each side of the carton is on its texture: (left, top, width, height) in pixels, 5 px per mm. Both ends show
# the tuck flap, as a real carton has one at each end.
W, H = 1024, 512
REGIONS = {
    "top": (0, 0, 485, 293),
    "front": (0, 293, 485, 183),
    "back": (512, 0, 485, 183),
    "end": (512, 183, 293, 183),
    "bottom": (512, 366, 485, 146),
}
# The end's tuck flap and its tab, as shares of the end (render_items.pack_carton: flap 94 % wide from 25 to 95 % of
# the height, tab 40 % wide from 6 to 26 %); y counts down from the lid.
FLAP = (0.03, 0.05, 0.97, 0.75)
TAB = (0.30, 0.74, 0.70, 0.94)
# The pale core of the board, where an edge is worn through the printed skin.
CORE = np.array([0.80, 0.73, 0.62], dtype=np.float32)
FONTS = Path("C:/Windows/Fonts")
NOHQ = f"{PACKS_PATH}\\carton_nohq.paa"
CARTON_RVMAT = f"{PACKS_PATH}\\gmr_carton.rvmat"


# ----- Texture -----

def noise(rng, height, width, scale, stretch=1.0):
    """Smooth noise in -1..1: random values on a grid scale pixels apart (stretch times that across), scaled up."""
    grid = rng.random((max(2, int(height / scale)), max(2, int(width / (scale * stretch)))))
    image = Image.fromarray((grid * 255).astype(np.uint8)).resize((width, height), Image.BICUBIC)
    return np.asarray(image, dtype=np.float32) / 127.5 - 1


def border_distance(w, h):
    """Per pixel of a side: the distance to its nearest edge and to its nearest corner, in pixels."""
    x = np.minimum(np.arange(w), np.arange(w)[::-1]).astype(np.float32)
    y = np.minimum(np.arange(h), np.arange(h)[::-1]).astype(np.float32)
    edge = np.minimum(x[None, :], y[:, None])
    corner = np.hypot(x[None, :], y[:, None])
    return edge, corner


def line_mask(size, lines, width=1, blur=0.6):
    image = Image.new("L", size, 0)
    draw = ImageDraw.Draw(image)

    for points in lines:
        draw.line(points, fill=255, width=width)

    return np.asarray(image.filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32) / 255


_LAYERS = None


def layers():
    """What every carton shares, as they all come off the same die and wear the same way: the worn edges, dirt, board
    grain and the relief for the normal map. Made once, from a fixed seed."""
    global _LAYERS

    if _LAYERS is not None:
        return _LAYERS

    rng = np.random.default_rng(1107)
    wear = np.zeros((H, W), np.float32)
    shade = np.ones((H, W), np.float32)
    height = np.zeros((H, W), np.float32)

    # Board: fibres running along the sheet, a finer grain, and a few flecks of recycled board.
    streaks = noise(rng, H, W, 1.4, 7.0)
    grain = noise(rng, H, W, 2.5)
    shade *= 1 + 0.035 * streaks + 0.025 * grain + 0.02 * noise(rng, H, W, 40)
    flecks = rng.random((H, W))
    shade[flecks < 0.0012] *= 0.72
    shade[flecks > 0.9994] *= 1.12
    height += 0.25 * streaks + 0.2 * grain + 1.2 * noise(rng, H, W, 90)

    for side, (left, top, w, h) in REGIONS.items():
        edge, corner = border_distance(w, h)
        area = (slice(top, top + h), slice(left, left + w))

        # Edges and corners rubbed through to the core, more at the corners, in ragged patches.
        ragged = noise(rng, h, w, 2.0) * 0.5 + 0.5
        patches = noise(rng, h, w, 14.0) * 0.5 + 0.5
        band = np.clip(1 - edge / 3.5, 0, 1) ** 1.5
        knock = np.clip(1 - corner / 16, 0, 1)
        wear[area] = np.clip((band * (0.25 + patches * 0.75) + knock * 0.8 + ragged * 0.45 - 1.1) * 2.5, 0, 1)

        # Rounded edges of the fold, a few dents where it was knocked.
        height[area] -= 3.0 * np.clip(1 - edge / 5, 0, 1) ** 2 + 0.9 * wear[area]

        # The sides carry dirt towards the ground, and every side some soft smudges.
        dirt = 1 - 0.05 * np.clip(noise(rng, h, w, 55), 0, 1)

        if side in ("front", "back", "end"):
            fall = (np.arange(h, dtype=np.float32) / h)[:, None] ** 3
            dirt *= 1 - 0.08 * fall * (0.6 + 0.4 * noise(rng, h, w, 12))

        shade[area] *= dirt

        # Scuffs: a few thin light scratches on the large sides.
        if side in ("top", "front", "back", "bottom"):
            strokes = []

            for _ in range(int(rng.integers(1, 4))):
                x0, y0 = rng.random() * w, rng.random() * h
                angle = rng.random() * math.pi
                length = 10 + rng.random() * 45
                strokes.append([(x0, y0), (x0 + math.cos(angle) * length, y0 + math.sin(angle) * length)])

            scuff = line_mask((w, h), strokes, 1, 0.5)
            wear[area] = np.maximum(wear[area], scuff * 0.16)
            height[area] -= 0.6 * scuff

    # The end's tuck flap: folded down from the lid, lying on the end with a dark gap round its free edges.
    left, top, w, h = REGIONS["end"]
    fx0, fy0, fx1, fy1 = (FLAP[0] * w, FLAP[1] * h, FLAP[2] * w, FLAP[3] * h)
    tx0, ty0, tx1, ty1 = (TAB[0] * w, TAB[1] * h, TAB[2] * w, TAB[3] * h)
    outline = [(fx0, fy0), (fx0, fy1), (tx0, fy1), (tx0, ty1), (tx1, ty1), (tx1, fy1), (fx1, fy1), (fx1, fy0)]
    gap = line_mask((w, h), [outline], 1, 0.5)
    fold = line_mask((w, h), [[(fx0, fy0), (fx1, fy0)]], 2, 0.8)
    raised = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(raised)
    draw.rectangle([fx0, fy0, fx1, fy1], fill=255)
    draw.rectangle([tx0, fy1, tx1, ty1], fill=255)
    raised = np.asarray(raised.filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32) / 255
    area = (slice(top, top + h), slice(left, left + w))
    shade[area] *= (1 - 0.45 * gap) * (1 - 0.25 * fold)
    height[area] += 1.4 * raised - 2.2 * fold

    _LAYERS = wear, shade, height
    return _LAYERS


def normal_map():
    """The relief as a DirectX normal map, the way the game reads it: green is down the texture."""
    height = layers()[2]
    dy, dx = np.gradient(height)
    strength = 0.55
    n = np.dstack((-dx * strength, -dy * strength, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).round().astype(np.uint8), "RGB")


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def barcode(draw, left, top, width, height, ink, seed):
    rng = random.Random(seed)
    x = left

    while x < left + width:
        bar = rng.choice((1, 1, 2, 3))

        if rng.random() < 0.55:
            draw.rectangle([x, top, x + bar - 1, top + height], fill=ink)

        x += bar

    digits = "".join(str(rng.randrange(10)) for _ in range(12))
    draw.text((left + width / 2, top + height + 2), digits, font=font("consola.ttf", 11), fill=ink, anchor="mt")


def small_print(atlas, label, variant_label, ink, seed):
    """What a carton carries on its back and stamped on its flaps: barcode, what is inside, how to keep it, the lot."""
    draw = ImageDraw.Draw(atlas)
    left, top, w, h = REGIONS["back"]
    barcode(draw, left + 22, top + 52, 120, 60, ink, seed)
    lines = (
        (f"{label.upper()}  -  {'BALL' if variant_label == 'Basic' else variant_label.upper()}", font("bahnschrift.ttf", 19)),
        ("CARTRIDGES FOR SMALL ARMS", font("bahnschrift.ttf", 14)),
        ("KEEP DRY  -  STORE AWAY FROM HEAT", font("bahnschrift.ttf", 12)),
        ("LOT GMR-26-1107", font("consolab.ttf", 13)),
    )
    y = top + 48

    for text, face in lines:
        draw.text((left + 172, y), text, font=face, fill=ink)
        y += face.size + 9

    # The lot stamped on the flap, a little uneven.
    left, top, w, h = REGIONS["end"]
    stamp = Image.new("L", (w, h), 0)
    ImageDraw.Draw(stamp).text((w / 2, h * 0.52), "26-1107  A", font=font("consolab.ttf", 14), fill=170, anchor="mm")
    atlas.paste(Image.new("RGB", (w, h), ink), (left, top), stamp)


def carton_texture(faces, name, label, variant_label):
    """The atlas of one pack's carton: the sides render_pack_textures.py rendered, made into printed paperboard."""
    sides = {side: Image.open(faces / f"face_{name}_{side}.png").convert("RGBA") for side in ("top", "front", "end", "back")}
    back = sides["back"]
    board = back.getpixel((back.width // 2, back.height // 2))
    universal = name.startswith("universal")
    ink = (214, 208, 190) if universal else (22, 21, 20)
    atlas = Image.new("RGBA", (W, H), board)

    for side in ("top", "front", "end", "back"):
        left, top, w, h = REGIONS[side]
        flat = Image.new("RGBA", sides[side].size, board)
        flat.alpha_composite(sides[side])
        atlas.paste(flat.resize((w, h), Image.LANCZOS), (left, top))

    atlas = atlas.convert("RGB")
    small_print(atlas, label, variant_label, ink, sum(map(ord, name)))

    # The picture's white studio light takes a little colour out of everything; so does this.
    rgb = np.asarray(atlas, dtype=np.float32) / 255
    rgb = rgb * 0.82 + rgb.mean(axis=2, keepdims=True) * 0.18
    paper = np.array(board[:3], dtype=np.float32) / 255
    paper = paper * 0.82 + paper.mean() * 0.18
    wear, shade, _ = layers()
    rng = np.random.default_rng(sum(map(ord, name)))

    # Print on board: unevenly taken up, a little thinner in patches.
    printed = np.clip((np.linalg.norm(rgb - paper, axis=2) - 0.04) / 0.10, 0, 1)
    fade = np.clip(0.08 + 0.10 * noise(rng, H, W, 4) + 0.06 * noise(rng, H, W, 30), 0, 0.3)
    rgb += (paper - rgb) * (printed * fade)[..., None]

    rgb *= shade[..., None]
    rgb = rgb * (1 - wear[..., None]) + CORE * wear[..., None]
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).round().astype(np.uint8), "RGB")


def pack_names():
    """(file name, label, variant label) of every pack."""
    for caliber, (label, _, _, _, variants) in ITEM_TABLE.CALIBERS.items():
        for variant, (variant_label, _) in ({"basic": ("Basic", ())} | variants).items():
            yield f"{caliber}_{variant}", label, variant_label


def clip_carton_names():
    """(file name, label, variant label) of every carton of stripper clips."""
    for caliber, variant, _, _, count, _ in ITEM_TABLE.clip_cartons():
        label = ITEM_TABLE.CALIBERS[caliber][0]
        yield f"clips_{caliber}_{variant}_{count}", label, ITEM_TABLE.variants_of(caliber)[variant][0]


def paa(png, target):
    """PNG to PAA. HEMTT will not write over a PAA that exists (it says so and still exits 0), so the old one goes first,
    and a run that leaves no new file fails loudly."""
    target = Path(target)
    target.unlink(missing_ok=True)
    result = subprocess.run(["hemtt", "utils", "paa", "convert", str(png), str(target)], capture_output=True, text=True)

    if result.returncode != 0 or not target.exists():
        raise RuntimeError(f"PAA conversion failed for {png}: {result.stdout} {result.stderr}")


def write_textures(faces, preview):
    """Every carton's PAA, their shared normal map and material; the PNGs stay in the preview folder, else beside the
    faces."""
    PACKS.mkdir(parents=True, exist_ok=True)
    folder = preview or faces
    folder.mkdir(parents=True, exist_ok=True)

    for name, label, variant_label in [*pack_names(), *clip_carton_names()]:
        png = folder / f"carton_{name}_co.png"
        carton_texture(faces, name, label, variant_label).save(png)
        paa(png, PACKS / f"carton_{name}_co.paa")

    png = folder / "carton_nohq.png"
    normal_map().save(png)
    paa(png, PACKS / "carton_nohq.paa")
    (PACKS / "gmr_carton.rvmat").write_text(carton_rvmat(), encoding="utf-8", newline="\n")
    print("carton textures written")
    return folder


def carton_rvmat():
    """Matte paperboard: the shared normal map, barely any shine, no environment to speak of."""
    stages = (
        NOHQ,
        "#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)",
        "#(argb,8,8,3)color(0.5,0.5,0.5,0,MC)",
        "#(argb,8,8,3)color(1,1,1,1,AS)",
        "#(argb,8,8,3)color(1,0.16,0.22,1,SMDI)",
        "#(ai,64,64,1)fresnel(1.4,0.2)",
        "a3\\data_f\\env_land_co.paa",
    )
    lines = [
        "ambient[] = {1, 1, 1, 1};", "diffuse[] = {1, 1, 1, 1};", "forcedDiffuse[] = {0, 0, 0, 0};",
        "emmisive[] = {0, 0, 0, 1};", "specular[] = {0.35, 0.35, 0.35, 1};", "specularPower = 14;",
        'PixelShaderID = "Super";', 'VertexShaderID = "Super";',
    ]

    for index, texture_path in enumerate(stages, 1):
        lines += [
            f"class Stage{index} {{", f'    texture = "{texture_path}";', '    uvSource = "tex";', "    class uvTransform {",
            "        aside[] = {1, 0, 0};", "        up[] = {0, 1, 0};", "        dir[] = {0, 0, 0};", "        pos[] = {0, 0, 0};",
            "    };", "};",
        ]

    return "\n".join(lines) + "\n"


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
    return left / W, top / H, w / W, h / H


def carton(surface, scale):
    """The picture's carton, standing: its length along Z, its front with the band towards +X, the flap's end at +Z.
    Blender's carton (render_items: length X, front -Y, lid +Z) becomes this one by (x, y, z) -> (-y, z, x), which
    mirrors it once: the game's left-handed axes mirror it back, so the print reads as in the picture."""
    model = Model()
    along, across, high = (value * scale for value in CARTON)
    sides = [
        ((0, 1, 0), (-1, 0, 0), share("top")),
        ((0, -1, 0), (1, 0, 0), share("bottom")),
        ((1, 0, 0), (0, 1, 0), share("front")),
        ((-1, 0, 0), (0, 1, 0), share("back")),
        ((0, 0, 1), (0, 1, 0), share("end")),
        ((0, 0, -1), (0, 1, 0), share("end")),
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


def clip_model(rounds):
    """A stripper clip lying on the ground: its rounds side by side along X, held at their bases by the steel strip.
    The ten-round clip carries 5.56 mm, the five-round one 7.62x51 mm."""
    model = Model()
    length, radius = (0.0574, 0.0048) if rounds == 10 else (0.0711, 0.006)
    pitch = radius * 2.12

    for index in range(rounds):
        x = (index - (rounds - 1) / 2) * pitch
        cartridge(model, (x, 0, 0), (0, 0, 1), length, radius)

    # The strip and its folded edges stay within the rounds' height, so the clip lies flat on its rounds, and they are
    # bright stamped steel as in its picture.
    strip = pitch * rounds + 0.003
    base = -length / 2
    model.box((0, 0, base + 0.0012), (strip, radius * 1.9, 0.0024), CLIP_STEEL)
    model.box((0, radius * 0.92, base + 0.0035), (strip, 0.0012, 0.006), CLIP_STEEL)
    model.box((0, -radius * 0.92, base + 0.0035), (strip, 0.0012, 0.006), CLIP_STEEL)
    return model


def speedloader():
    """The stripper clip guide of its picture, lying on its back: a steel channel the clip slides down, its walls with
    their lips folded in, and at one end the foot that sits on the magazine and the tab to hold it by."""
    model = Model()
    model.box((0, 0.00075, 0), (0.022, 0.0015, 0.05), GUIDE_STEEL)

    for side in (-1, 1):
        model.box((side * 0.0105, 0.005, 0), (0.002, 0.008, 0.05), GUIDE_STEEL)
        model.box((side * 0.0082, 0.0085, 0), (0.0045, 0.0012, 0.05), GUIDE_STEEL)

    model.box((0, 0.007, -0.029), (0.03, 0.014, 0.008), GUIDE_STEEL)
    model.box((0, 0.001, -0.041), (0.012, 0.002, 0.016), GUIDE_STEEL)
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
        "drop_clip_10": clip_model(10),
        "drop_clip_5": clip_model(5),
    }

    (OUT / "gmr_plain.rvmat").write_text(RVMAT, encoding="utf-8", newline="\n")

    for name, model in models.items():
        if preview:
            write_preview(preview / f"{name}.obj", model, None)

        lay_down(model)
        write_p3d(OUT / f"{name}.p3d", model, MATERIAL, geometry=hull_box(model), mass=DROP_MASS[name])

    packs = []

    # The cartons of stripper clips come in one size.
    for name, _, _ in clip_carton_names():
        model = carton(f"{PACKS_PATH}\\carton_{name}_co.paa", 1.0)

        if preview and pngs:
            write_preview(preview / f"pack_{name}.obj", model, pngs / f"carton_{name}_co.png")

        lay_down(model)
        write_p3d(PACKS / f"{name}.p3d", model, CARTON_RVMAT, welded(model, 0.98), welded(model), CARTON_MASS)
        packs.append(name)

    for name, _, _ in pack_names():
        for size, scale in CARTON_SCALES.items():
            model = carton(f"{PACKS_PATH}\\carton_{name}_co.paa", scale)

            if preview and pngs and size == "s":
                write_preview(preview / f"pack_{name}.obj", model, pngs / f"carton_{name}_co.png")

            lay_down(model)
            write_p3d(PACKS / f"pack_{name}_{size}.p3d", model, CARTON_RVMAT, welded(model, 0.98), welded(model),
                      CARTON_MASS * scale ** 3)
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
