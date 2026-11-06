"""Writes the magazine models shown in the hand while loading, as plain MLOD P3D.

    python tools/make_mag_models.py [preview folder]

Most magazines of the game and of mods only name a generic pouch as their model, so these stand in for them. There is a
family per kind of weapon (pistol, rifle, AK, battle rifle, heavy sniper, .50, shotgun) and a model per size within it,
from the length of the rounds stacked inside. Every one has a body bent the way its family's are, side ribs, a floor
plate, feed lips with the top round showing, and the AK's locking lugs.

Coordinates in metres, centred on the body: X across, Y up, Z along the curve's bulge (to the front). With a preview
folder, every model is also written there as OBJ for a quick look in Blender. It also writes
addons/handling/mag_backs.hpp, where the back of each lies, for fnc_holdMagazine.
"""

import math
import struct
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "data"
MATERIAL = "z\\gmr\\addons\\handling\\data\\gmr_plain.rvmat"

# A plain material: lit like the game's own models, a little shine, a flat normal map.
RVMAT = """ambient[] = {1, 1, 1, 1};
diffuse[] = {1, 1, 1, 1};
forcedDiffuse[] = {0, 0, 0, 0};
emmisive[] = {0, 0, 0, 1};
specular[] = {0.12, 0.12, 0.12, 1};
specularPower = 40;
PixelShaderID = "Normal";
VertexShaderID = "Basic";
class Stage1 {
    texture = "#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)";
    uvSource = "tex";
    class uvTransform {
        aside[] = {1, 0, 0};
        up[] = {0, 1, 0};
        dir[] = {0, 0, 0};
        pos[] = {0, 0, 0};
    };
};
"""


def texture(red, green, blue):
    return f"#(argb,8,8,3)color({red},{green},{blue},1,co)"


POLYMER = texture(0.05, 0.05, 0.055)
POLYMER_PLATE = texture(0.075, 0.075, 0.08)
STEEL = texture(0.09, 0.095, 0.10)
STEEL_PLATE = texture(0.13, 0.135, 0.14)
BAKELITE = texture(0.20, 0.07, 0.03)
BRASS = texture(0.66, 0.48, 0.18)
COPPER = texture(0.55, 0.27, 0.12)
SHELL = texture(0.45, 0.06, 0.05)
OLIVE = texture(0.17, 0.19, 0.12)


class Model:
    def __init__(self):
        self.points = []
        self.faces = []

    def face(self, corners, surface):
        start = len(self.points)
        self.points += list(corners)
        self.faces.append((tuple(range(start, start + len(corners))), surface))

    def sweep(self, rings, surface, caps=True):
        """Closes a body from rings of corners, listed from the bottom up, all in the same turning sense."""
        for low, high in zip(rings, rings[1:]):
            count = len(low)

            for i in range(count):
                j = (i + 1) % count
                self.face((low[i], low[j], high[j], high[i]), surface)

        if caps:
            self.cap(rings[0], surface, bottom=True)
            self.cap(rings[-1], surface, bottom=False)

    def cap(self, ring, surface, bottom):
        if len(ring) == 4:
            self.face(tuple(reversed(ring)) if bottom else tuple(ring), surface)
            return

        centre = tuple(sum(p[k] for p in ring) / len(ring) for k in range(3))

        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            self.face((centre, b, a) if bottom else (centre, a, b), surface)

    def box(self, centre, size, surface, frame=None):
        """A box, in the frame (origin, right, up, forward) when given, else along the axes."""
        hx, hy, hz = (value / 2 for value in size)
        origin, right, up, forward = frame or ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        cx, cy, cz = centre

        def at(x, y, z):
            return tuple(origin[k] + right[k] * x + up[k] * y + forward[k] * z for k in range(3))

        rings = []

        for y in (cy - hy, cy + hy):
            rings.append([at(cx - hx, y, cz - hz), at(cx + hx, y, cz - hz), at(cx + hx, y, cz + hz), at(cx - hx, y, cz + hz)])

        self.sweep(rings, surface)

    def cylinder(self, start, end, radius, surface, sides=10, tip=None):
        """A round along a line, with a pointed or flat end at `end`."""
        axis = [end[k] - start[k] for k in range(3)]
        length = math.sqrt(sum(value * value for value in axis))
        axis = [value / length for value in axis]
        helper = (1, 0, 0) if abs(axis[0]) < 0.9 else (0, 1, 0)
        u = cross(axis, helper)
        u = normalise(u)
        v = cross(axis, u)

        def ring(centre, r):
            # The turning sense must match sweep(): seen from the start, counter-clockwise.
            return [tuple(centre[k] + (u[k] * math.cos(a) + v[k] * math.sin(a)) * r for k in range(3))
                    for a in (2 * math.pi * i / sides for i in range(sides))][::-1]

        if tip is None:
            self.sweep([ring(start, radius), ring(end, radius)], surface)
            return

        tip_surface, tip_length = tip
        neck = tuple(end[k] - axis[k] * tip_length for k in range(3))
        self.sweep([ring(start, radius), ring(neck, radius)], surface)
        point = tuple(end[k] for k in range(3))
        rings = [ring(neck, radius), ring(tuple(neck[k] + axis[k] * tip_length * 0.6 for k in range(3)), radius * 0.62)]
        self.sweep(rings, tip_surface, caps=False)
        self.cap(rings[0], tip_surface, bottom=True)

        top = rings[-1]

        for i in range(len(top)):
            self.face((top[i], top[(i + 1) % len(top)], point), tip_surface)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def normalise(a):
    size = math.sqrt(sum(value * value for value in a)) or 1
    return tuple(value / size for value in a)


# family: body, plate and rib surfaces, width, depth, length per round, length beside the rounds, bend of a 30, the sizes
# made, the round (radius, length, tip surface or None for a shell), whether it has AK lugs.
FAMILIES = {
    "pistol": (STEEL, STEEL_PLATE, 0.022, 0.034, 0.0059, 0.026, 0.0, (7, 15, 30), (0.0048, 0.029, COPPER), False),
    "rifle": (POLYMER, POLYMER_PLATE, 0.024, 0.062, 0.0052, 0.028, 0.013, (10, 20, 30, 40), (0.0048, 0.057, COPPER), False),
    "ak": (STEEL, STEEL_PLATE, 0.027, 0.066, 0.0058, 0.030, 0.050, (10, 20, 30, 45), (0.0056, 0.056, COPPER), True),
    "battle": (STEEL, STEEL_PLATE, 0.030, 0.078, 0.0066, 0.030, 0.008, (5, 10, 20, 30), (0.0060, 0.071, COPPER), False),
    "heavy": (POLYMER, POLYMER_PLATE, 0.036, 0.100, 0.0085, 0.034, 0.0, (5, 10), (0.0075, 0.093, COPPER), False),
    "fifty": (STEEL, STEEL_PLATE, 0.042, 0.145, 0.0110, 0.036, 0.0, (5, 10), (0.0100, 0.138, COPPER), False),
    "shell": (POLYMER, POLYMER_PLATE, 0.034, 0.078, 0.0105, 0.030, 0.020, (5, 10), (0.0100, 0.070, None), False),
}


def centre_line(length, bend):
    """Points and forward directions up the magazine, bottom first; the bend is steepest at the bottom."""
    steps = 14
    line = []

    for step in range(steps + 1):
        t = step / steps
        y = -length / 2 + length * t
        z = bend * (1 - t) ** 2
        # The way up the curve and the way forward across it.
        up = normalise((0, length, -2 * bend * (1 - t)))
        forward = normalise(cross((1, 0, 0), up))
        line.append(((0, y, z), up, forward))

    return line


def magazine(family, capacity):
    body, plate, width, depth, per_round, extra, bend30, _, round_shape, lugs = FAMILIES[family]
    length = extra + per_round * capacity
    bend = bend30 * (length / (extra + per_round * 30)) ** 2
    model = Model()
    line = centre_line(length, bend)
    hw, hd = width / 2, depth / 2
    chamfer = min(width, depth) * 0.18

    def section(point, forward, half_w, half_d, cut):
        # Eight corners, chamfered, turning the same way as Model.box rings.
        right = (1, 0, 0)
        corners = [(-half_w + cut, -half_d), (half_w - cut, -half_d), (half_w, -half_d + cut), (half_w, half_d - cut),
                   (half_w - cut, half_d), (-half_w + cut, half_d), (-half_w, half_d - cut), (-half_w, -half_d + cut)]
        return [tuple(point[k] + right[k] * x + forward[k] * z for k in range(3)) for x, z in corners]

    # The body narrows a little towards the top, where the feed lips are.
    rings = []

    for index, (point, _up, forward) in enumerate(line):
        t = index / (len(line) - 1)
        rings.append(section(point, forward, hw * (1 - 0.04 * t), hd, chamfer))

    model.sweep(rings, body)

    # Two ribs down each side, standing out a millimetre, from a little below the top to above the floor plate.
    for side in (-1, 1):
        for rib_z in (-hd * 0.45, hd * 0.35):
            rib = []

            for index, (point, _up, forward) in enumerate(line):
                t = index / (len(line) - 1)

                if 0.10 <= t <= 0.82:
                    x = side * (hw * (1 - 0.04 * t))
                    centre = tuple(point[k] + forward[k] * rib_z for k in range(3))
                    inner, outer = x - side * 0.0005, x + side * 0.0016
                    lo, hi = (inner, outer) if side > 0 else (outer, inner)
                    rib.append([(lo, centre[1] - forward[1] * 0.0028, centre[2] - forward[2] * 0.0028),
                                (hi, centre[1] - forward[1] * 0.0028, centre[2] - forward[2] * 0.0028),
                                (hi, centre[1] + forward[1] * 0.0028, centre[2] + forward[2] * 0.0028),
                                (lo, centre[1] + forward[1] * 0.0028, centre[2] + forward[2] * 0.0028)])

            model.sweep(rib, plate)

    # Polymer magazines have grip ridges across the lower sides.
    if body == POLYMER:
        for index in (2, 3, 4):
            point, up, forward = line[index]
            frame = (point, (1, 0, 0), up, forward)
            t = index / (len(line) - 1)
            half = hw * (1 - 0.04 * t)

            for side in (-1, 1):
                model.box((side * (half + 0.0006), 0, 0), (0.0022, 0.0025, depth * 0.7), plate, frame)

    # The floor plate: a little larger than the body, with a lip at the front.
    point, up, forward = line[0]
    frame = (point, (1, 0, 0), up, forward)
    model.box((0, -0.004, 0), (width + 0.005, 0.008, depth + 0.006), plate, frame)
    model.box((0, -0.006, hd + 0.004), (width + 0.002, 0.005, 0.004), plate, frame)

    # The feed lips at the top, and the top round lying in them, off to one side as rounds of a double stack sit.
    point, up, forward = line[-1]
    frame = (point, (1, 0, 0), up, forward)
    model.box((0, 0.002, -hd * 0.05), (width * 0.82, 0.004, depth * 0.86), body, frame)

    radius, round_length, tip = round_shape
    side = 0.0 if family in ("heavy", "fifty") else width * 0.12
    base = [point[k] + up[k] * (0.004 + radius * 0.6) + (1, 0, 0)[k] * side for k in range(3)]
    start = tuple(base[k] - forward[k] * (round_length / 2 - 0.001) for k in range(3))
    end = tuple(base[k] + forward[k] * (round_length / 2 - 0.001) for k in range(3))

    if tip is None:
        # A shotgun shell: red hull, brass head at the back.
        head = tuple(start[k] + forward[k] * 0.012 for k in range(3))
        model.cylinder(start, head, radius * 1.04, BRASS)
        model.cylinder(head, end, radius, SHELL)
    else:
        model.cylinder(start, end, radius, BRASS, tip=(tip, round_length * 0.32))

    if lugs:
        # The AK's front locking lug and its rear catch.
        model.box((0, -0.008, hd + 0.003), (width * 0.5, 0.010, 0.006), body, frame)
        model.box((0, -0.012, -hd - 0.002), (width * 0.55, 0.006, 0.004), body, frame)

    return model


def ammo_box():
    """A machine gun's ammunition box with its lid, latch and handle, and the start of the belt coming out at the top."""
    model = Model()
    model.box((0, -0.006, 0), (0.075, 0.108, 0.120), OLIVE)
    model.box((0, 0.052, 0), (0.079, 0.012, 0.124), OLIVE)
    model.box((0.0395, 0.030, 0), (0.004, 0.026, 0.020), STEEL)
    model.box((0, 0.062, 0), (0.012, 0.006, 0.070), STEEL)

    for index in range(5):
        x = -0.020 + 0.010 * index
        y = 0.064 + 0.004 * index
        model.box((x, y - 0.006, -0.040), (0.006, 0.004, 0.020), STEEL)
        model.cylinder((x, y, -0.072), (x, y, -0.022), 0.0045, BRASS, sides=8, tip=(COPPER, 0.016))

    return model


def write_p3d(path, model, material=""):
    """One visual LOD: points, flat normals and faces, the winding as the game's models have it. Every face gets the
    material, without which the game lights a face flat and dark."""
    normals = []

    for corners, _surface in model.faces:
        pa, pb, pc = (model.points[i] for i in corners[:3])
        u = [pb[i] - pa[i] for i in range(3)]
        v = [pc[i] - pa[i] for i in range(3)]
        # Faces wind the other way round here, so the outward normal is the reversed cross product.
        n = (u[2] * v[1] - u[1] * v[2], u[0] * v[2] - u[2] * v[0], u[1] * v[0] - u[0] * v[1])
        normals.append(normalise(n))

    data = bytearray(b"MLOD" + struct.pack("<ii", 257, 1))
    data += b"P3DM" + struct.pack("<iiiiiI", 0x1C, 0x100, len(model.points), len(normals), len(model.faces), 0)

    for x, y, z in model.points:
        data += struct.pack("<fffI", x, y, z, 0)

    for normal in normals:
        data += struct.pack("<fff", *normal)

    uv4 = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

    for index, (corners, surface) in enumerate(model.faces):
        data += struct.pack("<i", len(corners))

        for slot in range(4):
            if slot < len(corners):
                u, v = uv4[slot]
                data += struct.pack("<iiff", corners[slot], index, u, v)
            else:
                data += struct.pack("<iiff", 0, 0, 0.0, 0.0)

        data += struct.pack("<I", 0)
        data += surface.encode("ascii") + b"\0" + material.encode("ascii") + b"\0"

    data += b"TAGG"
    data += b"\x01" + b"#EndOfFile#\0" + struct.pack("<i", 0)
    data += struct.pack("<f", 1.0)
    path.write_bytes(bytes(data))


def write_obj(path, model):
    """The same model as OBJ (Y up), its faces turned to the counter-clockwise winding OBJ expects."""
    surfaces = sorted({surface for _, surface in model.faces})
    lines = [f"mtllib {path.stem}.mtl"]
    lines += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in model.points]

    for surface in surfaces:
        lines.append(f"usemtl m{surfaces.index(surface)}")
        lines += ["f " + " ".join(str(i + 1) for i in reversed(corners)) for corners, s in model.faces if s == surface]

    path.write_text("\n".join(lines) + "\n")
    mtl = []

    for index, surface in enumerate(surfaces):
        r, g, b = surface.split("color(")[1].split(",")[:3]
        mtl += [f"newmtl m{index}", f"Kd {r} {g} {b}"]

    path.with_suffix(".mtl").write_text("\n".join(mtl) + "\n")


def back_at_middle(family, capacity):
    """Where the back of the body is at half its height, along Z: what fnc_holdMagazine lays into the palm."""
    _, _, _, depth, per_round, extra, bend30, *_ = FAMILIES[family]
    length = extra + per_round * capacity
    bend = bend30 * (length / (extra + per_round * 30)) ** 2
    return bend * 0.25 - depth / 2


def models():
    yield "mag_box", ammo_box(), -0.062

    for family, values in FAMILIES.items():
        for capacity in values[7]:
            yield f"mag_{family}_{capacity}", magazine(family, capacity), back_at_middle(family, capacity)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gmr_plain.rvmat").write_text(RVMAT, encoding="utf-8", newline="\n")
    preview = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    names = []
    backs = []

    for name, model, back in models():
        write_p3d(OUT / f"{name}.p3d", model, MATERIAL)
        names.append(name)
        backs.append(f'["{name}", {back:.4f}]')

        if preview:
            preview.mkdir(parents=True, exist_ok=True)
            write_obj(preview / f"{name}.obj", model)

    # The game's model coordinates have Y where the P3D has Z, so this is the back along the model's Y.
    (OUT.parent / "mag_backs.hpp").write_text(
        "// Generated by tools/make_mag_models.py: where the back of each of this mod's magazines is, at half its height.\n"
        f"#define MAG_BACKS [{', '.join(backs)}]\n", encoding="utf-8", newline="\n")
    print(f"{len(names)} magazine models written: {', '.join(names)}")


if __name__ == "__main__":
    main()
