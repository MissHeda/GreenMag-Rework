"""Renders the sides of every pack's carton, straight on and unlit, for the model the pack lies on the ground as.

    blender -b --factory-startup --python tools/render_pack_textures.py -- OUTPUT_FOLDER [name filter]
    python tools/make_drop_models.py --faces OUTPUT_FOLDER

The carton is the one of the inventory picture (render_items.pack_carton): same size, colour, print, band and flap.
Every material shows its plain colour, so the picture on the ground model is the carton's own and the game lights it.
Writes face_<caliber>_<variant>_<side>.png for the sides top, front, end (with the flap) and back.
"""

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_items as ITEM_TABLE  # noqa: E402
import render_items as ITEMS  # noqa: E402

# Pixels per mm of the finished texture; rendered at twice that and scaled down by make_drop_models.
DENSITY = 8

# How much light the picture's lid gets: with it, the unlit board under the picture's grading matches the lit lid.
LIGHT = float(__import__("os").environ.get("GMR_CARTON_LIGHT", "2.7"))

WIDTH, DEPTH, HEIGHT = ITEMS.CARTON

# side: (centre, outward normal, up, width, height); right is up x normal, as seen from outside.
SIDES = {
    "top": ((0, 0, HEIGHT), (0, 0, 1), (0, 1, 0), WIDTH, DEPTH),
    "front": ((0, -DEPTH / 2, HEIGHT / 2), (0, -1, 0), (0, 0, 1), WIDTH, HEIGHT),
    "end": ((WIDTH / 2, 0, HEIGHT / 2), (1, 0, 0), (0, 0, 1), DEPTH, HEIGHT),
    "back": ((0, DEPTH / 2, HEIGHT / 2), (0, 1, 0), (0, 0, 1), WIDTH, HEIGHT),
}


def unlit():
    """Every material its base colour as emission, as bright as the picture's light makes the lid."""
    for mat in bpy.data.materials:
        nodes = mat.node_tree.nodes
        shader = nodes.get("Principled BSDF")
        output = nodes.get("Material Output")

        if not shader or not output:
            continue

        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = shader.inputs["Base Color"].default_value
        emission.inputs["Strength"].default_value = LIGHT
        mat.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])


def setup(camera_data):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.cycles.device = "CPU"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    # The picture's grading (render_items.setup_scene), so print, band and board come out in its colours.
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.35
    world = bpy.data.worlds.get("black") or bpy.data.worlds.new("black")
    world.color = (0, 0, 0)
    scene.world = world

    camera = bpy.data.objects.new("camera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    return scene, camera


def render_sides(name, caliber, variant, label, variant_label, folder, second=None):
    for item in list(bpy.data.objects):
        bpy.data.objects.remove(item, do_unlink=True)

    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    ITEMS.pack_carton(caliber, variant, label, variant_label, second)

    # A real tuck flap is the same board as the carton; the picture's darker flap only reads as its shadow.
    for item in bpy.data.objects:
        if item.name.startswith("flap"):
            item.data.materials[0] = bpy.data.materials[f"kraft_{caliber}"]

    unlit()
    camera_data = bpy.data.cameras.new("camera")
    camera_data.type = "ORTHO"
    camera_data.clip_end = 5000
    scene, camera = setup(camera_data)

    for side, (centre, normal, up, width, height) in SIDES.items():
        n = Vector(normal)
        u = Vector(up)
        right = u.cross(n)
        camera.matrix_world = Matrix.Translation(Vector(centre) + n * 500) @ Matrix((
            (right.x, u.x, n.x, 0), (right.y, u.y, n.y, 0), (right.z, u.z, n.z, 0), (0, 0, 0, 1)))
        camera_data.ortho_scale = max(width, height)
        scene.render.resolution_x = round(width * DENSITY * 2)
        scene.render.resolution_y = round(height * DENSITY * 2)
        scene.render.filepath = str(folder / f"face_{name}_{side}.png")
        bpy.ops.render.render(write_still=True)

    print("rendered", name, flush=True)


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    folder = Path(args[0]).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    name_filter = args[1] if len(args) > 1 else ""

    for caliber, (label, _, _, _, variants) in ITEM_TABLE.CALIBERS.items():
        for variant, (variant_label, _) in ({"basic": ("Basic", ())} | variants).items():
            name = f"{caliber}_{variant}"

            if not name_filter or name_filter in name:
                render_sides(name, caliber, variant, label, variant_label, folder)

    # The cartons of stripper clips, with their own second line.
    for caliber, rounds in ITEM_TABLE.CLIPS.items():
        label = ITEM_TABLE.CALIBERS[caliber][0]

        for variant, (variant_label, _) in ITEM_TABLE.variants_of(caliber).items():
            name = f"clips_{caliber}_{variant}"

            if not name_filter or name_filter in name:
                second = ITEMS.clip_line(variant, variant_label, rounds)
                render_sides(name, caliber, variant, label, variant_label, folder, second)


main()
