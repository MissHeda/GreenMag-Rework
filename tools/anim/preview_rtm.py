"""Renders an RTM on the Samples' male body with Blender, to look at an animation without the game.

    blender -b --factory-startup --python tools/anim/preview_rtm.py -- RTM OUTPUT_PNG [frame numbers ...]

Each frame comes out from the front and from the side, one row per frame. The rtm's own transforms and the mesh's own
weights are used, so what this shows is what the file contains.
"""

import json
import os
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from armaformats import read_p3d, read_rtm

SAMPLES = Path(os.environ.get("ARMA3_SAMPLES", r"C:\SteamLibrary\steamapps\common\Arma 3 Samples\Addons"))
PREVIEW_DATA = Path(__file__).resolve().parent / "load_preview.json"
CELL = 380

# Where the left hand holds the magazine, in Blender's axes, for the close views.
HAND = (0.06, -0.28, 1.24)


def to_blender(points):
    """RTM space (Y up, facing -Z) to Blender's (Z up, facing -Y)."""
    return np.column_stack((points[:, 0], points[:, 2], points[:, 1]))


def skin_setup():
    male = read_p3d(SAMPLES / "TemplateRTM" / "Male.p3d")[0]
    points = np.array(male.points)
    weights = np.zeros(len(points))
    groups = {}

    for name, members in male.selections.items():
        if name.startswith("-"):
            continue

        indices = np.fromiter(members.keys(), dtype=np.int32)
        values = np.fromiter(members.values(), dtype=np.float64)
        groups[name.lower()] = (indices, values)
        weights[indices] += values

    return male, points, weights, groups


def skinned(frame, points, weights, groups):
    out = np.zeros_like(points)

    for bone, (indices, values) in groups.items():
        matrix = frame.get(bone)

        if matrix is None:
            continue

        rotation = np.array(matrix[:9]).reshape(3, 3).T
        translation = np.array(matrix[9:])
        out[indices] += (points[indices] @ rotation.T + translation) * values[:, None]

    placed = weights > 0
    out[placed] /= weights[placed][:, None]
    out[~placed] = points[~placed]
    return out


def add_magazine(frame):
    if not PREVIEW_DATA.exists():
        return

    data = json.loads(PREVIEW_DATA.read_text(encoding="utf-8"))
    matrix = frame["lefthand"]
    rotation = np.array(matrix[:9]).reshape(3, 3).T
    translation = np.array(matrix[9:])
    pivots = read_p3d(SAMPLES / "TemplateRTM" / "ManSkeleton_Pivots.p3d")[0]
    wrist_bind = np.mean([pivots.points[i] for i in pivots.selections["LeftHand"]], axis=0)
    wrist = rotation @ wrist_bind + translation
    center = wrist + rotation @ np.array(data["center"])
    axes = rotation @ np.array(data["axes"])
    size = np.array(data["size"])
    corners = []

    for sx in (-0.5, 0.5):
        for sy in (-0.5, 0.5):
            for sz in (-0.5, 0.5):
                corners.append(center + axes @ (size * np.array([sx, sy, sz])))

    mesh = bpy.data.meshes.new("magazine")
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh.from_pydata(to_blender(np.array(corners)).tolist(), [], faces)
    mesh.update()
    item = bpy.data.objects.new("magazine", mesh)
    material = bpy.data.materials.new("magazine")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
    item.data.materials.append(material)
    bpy.context.collection.objects.link(item)


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    rtm = read_rtm(args[0])
    output = Path(args[1]).resolve()
    wanted = [int(v) for v in args[2:]] or [0, len(rtm.frames) // 2]

    male, points, weights, groups = skin_setup()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = CELL
    scene.render.resolution_y = CELL
    scene.display.shading.light = "STUDIO"
    scene.display.shading.show_shadows = True
    scene.display.shading.color_type = "MATERIAL"
    tiles = []

    for number in wanted:
        frame = rtm.frames[number]
        posed = skinned(frame, points, weights, groups)

        for name, direction, focus, scale in (
            ("front", (0.0, -1.0, 0.0), (0, 0, 1.25), 0.85),
            ("side", (1.0, 0.0, 0.0), (0, 0.0, 1.25), 0.85),
            ("eye", (0.05, -0.55, 0.85), (0, -0.2, 1.2), 0.75),
            ("hand_front", (0.0, -1.0, 0.0), HAND, 0.26),
            ("hand_near", (0.0, 1.0, 0.25), HAND, 0.26),
            ("hand_top", (0.0, 0.05, 1.0), HAND, 0.26),
        ):
            for item in list(bpy.context.collection.objects):
                bpy.data.objects.remove(item, do_unlink=True)

            mesh = bpy.data.meshes.new("body")
            mesh.from_pydata(to_blender(posed).tolist(), [], [tuple(reversed(face)) for face in male.faces])
            mesh.update()
            body = bpy.data.objects.new("body", mesh)
            bpy.context.collection.objects.link(body)
            add_magazine(frame)

            camera_data = bpy.data.cameras.new("camera")
            camera_data.type = "ORTHO"
            camera_data.ortho_scale = scale
            camera = bpy.data.objects.new("camera", camera_data)
            bpy.context.collection.objects.link(camera)
            view = Vector(direction).normalized()
            camera.location = Vector(focus) + view * 5
            camera.rotation_euler = (-view).to_track_quat("-Z", "Y").to_euler()
            scene.camera = camera

            tile = output.parent / f"_tile_{number}_{name}.png"
            scene.render.filepath = str(tile)
            bpy.ops.render.render(write_still=True)
            tiles.append(tile)

    # The tiles side by side, by Blender's own image handling.
    columns = 6
    rows = len(wanted)
    sheet = np.zeros((rows * CELL, columns * CELL, 4), dtype=np.float32)

    for index, tile in enumerate(tiles):
        image = bpy.data.images.load(str(tile))
        pixels = np.array(image.pixels[:], dtype=np.float32).reshape(CELL, CELL, 4)
        row = rows - 1 - index // columns
        column = index % columns
        sheet[row * CELL:(row + 1) * CELL, column * CELL:(column + 1) * CELL] = pixels
        bpy.data.images.remove(image)

    result = bpy.data.images.new("sheet", columns * CELL, rows * CELL, alpha=True)
    result.pixels = sheet.ravel().tolist()
    result.filepath_raw = str(output)
    result.file_format = "PNG"
    result.save()


main()
