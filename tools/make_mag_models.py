"""Writes the magazine models shown in the hand while loading, as plain MLOD P3D.

    python tools/make_mag_models.py

Most magazines of the game and of mods only name a generic pouch as their model, so these stand in for them: a curved
rifle magazine, a stronger curved one, a straight pistol magazine and a machine gun box. Coordinates in metres, centred
on the magazine: X across, Y up, Z along the curve's bulge.
"""

import math
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "addons" / "handling" / "data"


def texture(red, green, blue):
    return f"#(argb,8,8,3)color({red},{green},{blue},1,co)"


POLYMER = texture(0.055, 0.055, 0.06)
STEEL = texture(0.12, 0.125, 0.11)
BRASS = texture(0.62, 0.46, 0.16)


class Model:
    def __init__(self):
        self.points = []
        self.faces = []

    def quad(self, a, b, c, d, surface):
        start = len(self.points)
        self.points += [a, b, c, d]
        self.faces.append(((start, start + 1, start + 2, start + 3), surface))

    def section(self, rings, surface):
        """Closes a body from rings of four corners, listed from the bottom up."""
        for low, high in zip(rings, rings[1:]):
            for i in range(4):
                j = (i + 1) % 4
                self.quad(low[i], low[j], high[j], high[i], surface)

        self.quad(*reversed(rings[0]), surface)
        self.quad(*rings[-1], surface)

    def box(self, center, size, surface):
        cx, cy, cz = center
        sx, sy, sz = (value / 2 for value in size)
        low = [(cx - sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz + sz), (cx - sx, cy - sy, cz + sz)]
        high = [(x, cy + sy, z) for x, _, z in low]
        self.section([low, high], surface)


def curved(length, width, depth, bend, surface):
    """A magazine body bending along Z as it goes down, with a floor plate and rounds showing at the top."""
    model = Model()
    rings = []
    steps = 10

    for step in range(steps + 1):
        t = step / steps
        y = -length / 2 + length * t
        # The bend is steepest at the bottom.
        z = bend * (1 - t) ** 2
        angle = math.atan2(2 * bend * (1 - t), length)
        half_w = width / 2
        half_d = depth / 2
        dz = half_d * math.cos(angle)
        dy = half_d * math.sin(angle)
        rings.append([
            (-half_w, y + dy, z - dz), (half_w, y + dy, z - dz), (half_w, y - dy, z + dz), (-half_w, y - dy, z + dz),
        ])

    model.section(rings, surface)

    bottom_z = bend
    model.box((0, -length / 2 - 0.004, bottom_z), (width + 0.004, 0.008, depth + 0.006), surface)
    model.box((0, length / 2 + 0.002, 0.004), (width * 0.62, 0.006, depth * 0.72), BRASS)
    return model


def write_p3d(path, model):
    """One visual LOD: points, flat normals and faces, the winding as the game's models have it."""
    normals = []

    for (a, b, c, _), _surface in model.faces:
        pa, pb, pc = model.points[a], model.points[b], model.points[c]
        u = [pb[i] - pa[i] for i in range(3)]
        v = [pc[i] - pa[i] for i in range(3)]
        # Faces wind the other way round here, so the outward normal is the reversed cross product.
        n = (u[2] * v[1] - u[1] * v[2], u[0] * v[2] - u[2] * v[0], u[1] * v[0] - u[0] * v[1])
        size = math.sqrt(sum(value * value for value in n)) or 1
        normals.append(tuple(value / size for value in n))

    data = bytearray(b"MLOD" + struct.pack("<ii", 257, 1))
    data += b"P3DM" + struct.pack("<iiiiiI", 0x1C, 0x100, len(model.points), len(normals), len(model.faces), 0)

    for x, y, z in model.points:
        data += struct.pack("<fffI", x, y, z, 0)

    for normal in normals:
        data += struct.pack("<fff", *normal)

    corner_uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

    for index, (corners, surface) in enumerate(model.faces):
        data += struct.pack("<i", 4)

        for corner, (u, v) in zip(corners, corner_uv):
            data += struct.pack("<iiff", corner, index, u, v)

        data += struct.pack("<I", 0)
        data += surface.encode("ascii") + b"\0" + b"\0"

    data += b"TAGG"
    data += b"\x01" + b"#EndOfFile#\0" + struct.pack("<i", 0)
    data += struct.pack("<f", 1.0)
    path.write_bytes(bytes(data))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write_p3d(OUT / "mag_rifle.p3d", curved(0.165, 0.024, 0.062, 0.014, POLYMER))
    write_p3d(OUT / "mag_ak.p3d", curved(0.190, 0.027, 0.066, 0.040, STEEL))
    write_p3d(OUT / "mag_pistol.p3d", curved(0.125, 0.021, 0.036, 0.0, STEEL))

    box = Model()
    box.box((0, 0, 0), (0.075, 0.120, 0.120), STEEL)
    box.box((0.0, 0.066, 0.0), (0.040, 0.012, 0.095), BRASS)
    write_p3d(OUT / "mag_box.p3d", box)
    print("Magazine models written.")


if __name__ == "__main__":
    main()
