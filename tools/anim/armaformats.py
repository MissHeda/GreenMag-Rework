"""Readers and a writer for the plain Arma 3 formats the animation tools need: MLOD P3D and RTM_0101."""

import struct
from dataclasses import dataclass, field


def read_z(data, at):
    end = data.index(b"\0", at)
    return data[at:end].decode("latin-1"), end + 1


@dataclass
class Lod:
    resolution: float = 0.0
    points: list = field(default_factory=list)
    faces: list = field(default_factory=list)
    selections: dict = field(default_factory=dict)


def weight_of(byte):
    """Selection weights as MLOD stores them: 0 none, 1 full, anything else counted down from 256."""
    if byte == 0:
        return 0.0
    if byte == 1:
        return 1.0
    return (256 - byte) / 255.0


def read_p3d(path, wanted_lods=1):
    """The first LODs of an MLOD: points, faces as point index tuples, and selections as {point: weight}."""
    data = open(path, "rb").read()
    if data[:4] != b"MLOD":
        raise ValueError(f"{path} is not an MLOD")

    count = struct.unpack_from("<i", data, 8)[0]
    at = 12
    lods = []

    for _ in range(min(count, wanted_lods)):
        if data[at:at + 4] != b"P3DM":
            raise ValueError(f"Expected P3DM at {at}")

        n_points, n_normals, n_faces = struct.unpack_from("<iii", data, at + 12)
        at += 28
        lod = Lod()

        for i in range(n_points):
            x, y, z, _flags = struct.unpack_from("<fffI", data, at + i * 16)
            lod.points.append((x, y, z))

        at += n_points * 16 + n_normals * 12

        for _ in range(n_faces):
            n_verts = struct.unpack_from("<i", data, at)[0]
            at += 4
            indices = []

            for v in range(4):
                point = struct.unpack_from("<i", data, at + v * 16)[0]
                if v < n_verts:
                    indices.append(point)

            at += 4 * 16 + 4
            _, at = read_z(data, at)
            _, at = read_z(data, at)
            lod.faces.append(tuple(indices))

        if data[at:at + 4] != b"TAGG":
            raise ValueError(f"Expected TAGG at {at}")

        at += 4

        while True:
            at += 1
            name, at = read_z(data, at)
            size = struct.unpack_from("<i", data, at)[0]
            at += 4
            body = data[at:at + size]
            at += size

            if name == "#EndOfFile#":
                break

            if not name.startswith("#"):
                lod.selections[name] = {i: weight_of(body[i]) for i in range(n_points) if body[i]}

        lod.resolution = struct.unpack_from("<f", data, at)[0]
        at += 4
        lods.append(lod)

    return lods


@dataclass
class Rtm:
    move: tuple
    bones: list
    phases: list
    frames: list  # per frame {lowercase bone: 12 floats}


def read_rtm(path):
    data = open(path, "rb").read()
    if data[:8] != b"RTM_0101":
        raise ValueError(f"{path} is not a plain RTM")

    move = struct.unpack_from("<fff", data, 8)
    n_frames, n_bones = struct.unpack_from("<ii", data, 20)
    at = 28
    bones = []

    for i in range(n_bones):
        bones.append(data[at:at + 32].split(b"\0")[0].decode("latin-1"))
        at += 32

    phases = []
    frames = []

    for _ in range(n_frames):
        phases.append(struct.unpack_from("<f", data, at)[0])
        at += 4
        frame = {}

        for _ in range(n_bones):
            name = data[at:at + 32].split(b"\0")[0].decode("latin-1").lower()
            at += 32
            frame[name] = struct.unpack_from("<12f", data, at)
            at += 48

        frames.append(frame)

    return Rtm(move, bones, phases, frames)


def write_rtm(path, bones, phases, frames, move=(0.0, 0.0, 0.0)):
    with open(path, "wb") as file:
        file.write(b"RTM_0101")
        file.write(struct.pack("<fff", *move))
        file.write(struct.pack("<ii", len(frames), len(bones)))

        for bone in bones:
            file.write(bone.encode("latin-1").ljust(32, b"\0"))

        for phase, frame in zip(phases, frames):
            file.write(struct.pack("<f", phase))

            for bone in bones:
                file.write(bone.encode("latin-1").ljust(32, b"\0"))
                file.write(struct.pack("<12f", *frame[bone.lower()]))
