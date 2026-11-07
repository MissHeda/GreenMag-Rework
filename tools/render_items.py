"""Renders the inventory pictures of the items with Blender's Cycles, lit like a product photo.

    blender -b --factory-startup --python tools/render_items.py -- OUTPUT_FOLDER [name filter]

Writes 512x512 PNGs with transparency; tools/make_icons.py turns them into PAA. The light is mostly the world: strips
of bright and dark around the object, which is what makes metal read as metal.
"""

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

RESOLUTION = 512
SAMPLES = 96
SEGMENTS = 128
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_items as ITEM_TABLE  # noqa: E402

FONT = r"C:\Windows\Fonts\arialbd.ttf"

BRASS = ((0.78, 0.47, 0.13), 1.0, 0.20)
LACQUERED_STEEL = ((0.085, 0.095, 0.05), 0.7, 0.30)
COPPER = ((0.80, 0.33, 0.14), 1.0, 0.17)
PARKERIZED = ((0.035, 0.037, 0.04), 0.85, 0.42)
BLUED = ((0.13, 0.13, 0.145), 1.0, 0.30)
BASE_STAMP = ((0.36, 0.21, 0.06), 1.0, 0.42)
NICKEL = ((0.62, 0.63, 0.65), 1.0, 0.22)

# Paint on the bullet's tip per variant.
TIPS = {
    "tracer": (0.70, 0.07, 0.02),
    "irtracer": (0.72, 0.18, 0.42),
    "m995ap": (0.015, 0.015, 0.015),
    "m993ap": (0.015, 0.015, 0.015),
    "dual": (0.03, 0.26, 0.08),
    "mk318": (0.55, 0.56, 0.60),
    "sd": (0.03, 0.10, 0.45),
    "api": (0.55, 0.56, 0.60),
    "apds": (0.03, 0.26, 0.08),
}

# The lacquer ring military cartridges carry at the case mouth.
SEALANT = (0.32, 0.04, 0.05)

# id: base diameter, shoulder diameter, neck diameter, shoulder at, neck starts at, case length, overall length (mm),
# case material, rim ("groove" or "rim"), variants beside basic.
CARTRIDGES = {
    "universal": (9.6, 9.0, 6.4, 36.5, 38.5, 44.7, 57.4, NICKEL, "groove", ()),
    "9x19": (9.9, 9.7, 9.65, 19.15, 19.15, 19.15, 29.7, BRASS, "groove", ("tracer",)),
    "9x21": (9.9, 9.7, 9.65, 21.15, 21.15, 21.15, 31.0, BRASS, "groove", ("tracer",)),
    "9x18": (9.9, 9.7, 9.6, 18.1, 18.1, 18.1, 25.0, LACQUERED_STEEL, "groove", ()),
    "9x39": (11.3, 10.9, 9.9, 28.0, 31.0, 38.7, 56.0, LACQUERED_STEEL, "groove", ()),
    "762x25": (9.8, 9.4, 8.5, 16.0, 17.5, 24.6, 34.5, BRASS, "groove", ()),
    "45acp": (12.0, 11.9, 11.9, 22.8, 22.8, 22.8, 32.4, BRASS, "groove", ("tracer",)),
    "46x30": (7.8, 7.6, 5.2, 21.0, 23.0, 30.0, 38.5, BRASS, "groove", ()),
    "570x28": (7.9, 7.7, 6.3, 19.0, 21.0, 28.9, 40.5, BRASS, "groove", ()),
    "545x39": (10.0, 9.2, 6.3, 28.0, 31.0, 39.8, 57.0, LACQUERED_STEEL, "groove", ("tracer",)),
    "556x45": (9.6, 9.0, 6.4, 36.5, 38.5, 44.7, 57.4, BRASS, "groove", ("tracer", "irtracer", "m995ap", "mk262", "mk318", "dual")),
    "580x42": (10.4, 9.5, 6.4, 33.0, 35.5, 42.0, 58.0, BRASS, "groove", ("tracer",)),
    "650x39": (11.9, 10.9, 7.4, 28.0, 30.5, 38.7, 56.0, BRASS, "groove", ("tracer", "irtracer")),
    "762x39": (11.3, 10.1, 8.6, 30.0, 32.0, 38.7, 56.0, LACQUERED_STEEL, "groove", ("tracer",)),
    "300blk": (9.6, 9.1, 8.6, 28.0, 29.5, 35.0, 57.0, BRASS, "groove", ()),
    "762x51": (11.9, 11.2, 8.7, 39.0, 42.0, 51.2, 71.1, BRASS, "groove", ("tracer", "irtracer", "m118lr", "m993ap", "mk316", "mk319", "sd")),
    "762x54": (12.4, 11.5, 8.5, 41.0, 44.0, 53.7, 77.0, LACQUERED_STEEL, "rim", ("tracer",)),
    "792x57": (11.9, 11.0, 9.0, 45.0, 48.0, 57.0, 80.0, BRASS, "groove", ()),
    "303": (11.6, 10.3, 8.5, 45.0, 47.5, 56.4, 78.0, BRASS, "rim", ()),
    "50bw": (13.9, 13.8, 13.5, 42.0, 42.0, 42.0, 55.0, BRASS, "groove", ()),
    "93x64": (12.9, 12.0, 10.3, 50.0, 53.0, 64.0, 93.0, BRASS, "groove", ()),
    "338": (14.9, 14.0, 9.3, 55.0, 59.0, 69.2, 93.5, BRASS, "groove", ("300gr", "api526")),
    "408": (16.5, 15.5, 10.9, 62.0, 66.0, 77.0, 115.0, BRASS, "groove", ("205gr",)),
    "127x54": (15.5, 14.5, 13.3, 38.0, 41.0, 54.0, 74.0, LACQUERED_STEEL, "groove", ()),
    "127x99": (20.4, 18.0, 14.0, 72.0, 78.0, 99.0, 138.0, BRASS, "groove", ("amax", "api")),
    "127x108": (21.8, 19.0, 14.0, 80.0, 86.0, 108.0, 147.0, LACQUERED_STEEL, "groove", ("apds",)),
}

SHELL_VARIANTS = {"basic": (0.20, 0.008, 0.006), "slug": (0.012, 0.075, 0.02)}


def material(name, base, metal=0.0, rough=0.5, wear=0.0, bump=0.0, bump_scale=120.0):
    """A principled material; wear varies its roughness a little, bump gives the surface fine grain."""
    existing = bpy.data.materials.get(name)

    if existing:
        return existing

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (*base, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = rough

    if wear or bump:
        coords = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = bump_scale
        noise.inputs["Detail"].default_value = 10
        links.new(coords.outputs["Object"], noise.inputs["Vector"])

        if wear:
            remap = nodes.new("ShaderNodeMapRange")
            remap.inputs["To Min"].default_value = max(0.02, rough - wear)
            remap.inputs["To Max"].default_value = rough + wear
            links.new(noise.outputs[0], remap.inputs["Value"])
            links.new(remap.outputs[0], shader.inputs["Roughness"])

        if bump:
            height = nodes.new("ShaderNodeBump")
            height.inputs["Strength"].default_value = bump
            height.inputs["Distance"].default_value = 0.2
            links.new(noise.outputs[0], height.inputs["Height"])
            links.new(height.outputs[0], shader.inputs["Normal"])

    return mat


def metal(spec):
    """Metal as it comes from a drawing die: fine lines along the part, and a little tarnish in patches."""
    base, metallic, rough = spec
    name = f"metal_{base}"
    existing = bpy.data.materials.get(name)

    if existing:
        return existing

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    shader = nodes["Principled BSDF"]
    shader.inputs["Metallic"].default_value = metallic
    coords = nodes.new("ShaderNodeTexCoord")

    # Lines along the length: the noise is stretched along Z, the axis of the part.
    stretch = nodes.new("ShaderNodeMapping")
    stretch.inputs["Scale"].default_value = (9.0, 9.0, 0.18)
    links.new(coords.outputs["Object"], stretch.inputs["Vector"])
    lines = nodes.new("ShaderNodeTexNoise")
    lines.inputs["Scale"].default_value = 1.0
    lines.inputs["Detail"].default_value = 6
    links.new(stretch.outputs[0], lines.inputs["Vector"])

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.inputs["To Min"].default_value = max(0.05, rough - 0.05)
    rough_map.inputs["To Max"].default_value = rough + 0.07
    links.new(lines.outputs[0], rough_map.inputs["Value"])
    links.new(rough_map.outputs[0], shader.inputs["Roughness"])

    height = nodes.new("ShaderNodeBump")
    height.inputs["Strength"].default_value = 0.03
    height.inputs["Distance"].default_value = 0.05
    links.new(lines.outputs[0], height.inputs["Height"])
    links.new(height.outputs[0], shader.inputs["Normal"])

    # Tarnish in soft patches.
    patches = nodes.new("ShaderNodeTexNoise")
    patches.inputs["Scale"].default_value = 0.16
    patches.inputs["Detail"].default_value = 4
    links.new(coords.outputs["Object"], patches.inputs["Vector"])
    tone = nodes.new("ShaderNodeValToRGB")
    tone.color_ramp.elements[0].position = 0.36
    tone.color_ramp.elements[0].color = (base[0] * 0.70, base[1] * 0.64, base[2] * 0.58, 1)
    tone.color_ramp.elements[1].position = 0.66
    tone.color_ramp.elements[1].color = (*base, 1)
    links.new(patches.outputs[0], tone.inputs["Fac"])
    links.new(tone.outputs[0], shader.inputs["Base Color"])
    return mat


def lathe(name, profile, mat, parent=None):
    """A body of revolution around Z from (radius, height) points."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []

    for radius, height in profile:
        ring = []

        for step in range(SEGMENTS):
            angle = 2 * math.pi * step / SEGMENTS
            ring.append(bm.verts.new((max(radius, 0.001) * math.cos(angle), max(radius, 0.001) * math.sin(angle), height)))

        rings.append(ring)

    for lower, upper in zip(rings, rings[1:]):
        for step in range(SEGMENTS):
            following = (step + 1) % SEGMENTS
            bm.faces.new((lower[step], lower[following], upper[following], upper[step]))

    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bm.to_mesh(mesh)
    bm.free()
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()

    item = bpy.data.objects.new(name, mesh)
    item.data.materials.append(mat)
    bpy.context.collection.objects.link(item)

    # Keep the hard edges of grooves and shoulders while the round parts stay smooth.
    if hasattr(item.data, "set_sharp_from_angle"):
        item.data.set_sharp_from_angle(angle=math.radians(28))

    if parent:
        item.parent = parent

    return item


def block(name, size, location, mat, bevel=0.0, rotation=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    item = bpy.context.object
    item.name = name
    item.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if bevel:
        modifier = item.modifiers.new("bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 5
        modifier.limit_method = "ANGLE"
        bpy.ops.object.shade_smooth()

    item.data.materials.append(mat)

    if parent:
        item.parent = parent

    return item


def cartridge(caliber, variant="basic", scale=1.0, location=(0, 0, 0), rotation=(0, 0, 0)):
    """A cartridge standing on its base: head, extractor groove, tapered body, shoulder, neck, sealant, jacket, tip."""
    base_d, shoulder_d, neck_d, shoulder_at, neck_at, case_len, overall, case_spec, rim, _ = CARTRIDGES[caliber]
    root = bpy.data.objects.new("cartridge", None)
    bpy.context.collection.objects.link(root)
    root.location = location
    root.rotation_euler = rotation
    root.scale = (scale, scale, scale)

    r_base = base_d / 2
    r_shoulder = shoulder_d / 2
    r_neck = neck_d / 2
    r_bullet = r_neck * 0.90
    head = base_d * 0.135

    if rim == "rim":
        foot = [
            (r_base * 1.13, head * 0.05), (r_base * 1.16, head * 0.15), (r_base * 1.16, head * 0.75),
            (r_base * 1.08, head), (r_base, head * 1.15),
        ]
    else:
        foot = [
            (r_base * 0.95, 0), (r_base, head * 0.15), (r_base, head),
            (r_base * 0.97, head * 1.05), (r_base * 0.80, head * 1.5), (r_base * 0.80, head * 2.0),
            (r_base * 0.97, head * 2.7), (r_base, head * 2.9),
        ]

    straight = shoulder_at >= case_len - 0.01
    body = [(r_shoulder, shoulder_at * (0.985 if not straight else 1))]

    if not straight:
        body += [(r_shoulder * 0.992, shoulder_at), (r_neck * 1.02, neck_at * 0.995), (r_neck, neck_at), (r_neck, case_len - 0.25)]

    mouth = [(r_neck * 0.985, case_len), (r_bullet * 1.05, case_len + 0.02)]
    lathe("case", foot + body + mouth, metal(case_spec), root)

    # Primer in the base, seen when a round lies down.
    lathe("base", [(r_base * 0.90, -0.02), (r_base * 0.90, 0.01)], metal(BASE_STAMP), root)
    lathe("primer", [(base_d * 0.145, -0.05), (base_d * 0.145, 0.01)], metal(COPPER), root)
    lathe("primer_ring", [(base_d * 0.165, -0.04), (base_d * 0.165, 0.01)], material("primer_seal", SEALANT, 0.0, 0.35), root)

    # Sealant ring at the mouth.
    lathe(
        "sealant",
        [(r_bullet * 1.0, case_len - 0.02), (r_bullet * 1.06, case_len + 0.01), (r_bullet * 1.04, case_len + 0.16), (r_bullet * 0.99, case_len + 0.18)],
        material("sealant", SEALANT, 0.0, 0.30),
        root,
    )

    # The bullet: a straight bearing part with a cannelure, then a secant ogive with a small flat tip.
    length = overall - case_len
    bearing = length * 0.30
    start = case_len + 0.1
    profile = [(r_bullet * 0.99, start), (r_bullet, start + bearing * 0.25), (r_bullet * 0.965, start + bearing * 0.33), (r_bullet, start + bearing * 0.42), (r_bullet, start + bearing)]
    points = 26
    tip_radius = r_bullet * 0.14

    for step in range(1, points + 1):
        t = step / points
        radius = tip_radius + (r_bullet - tip_radius) * math.sqrt(max(0.0, 1 - t ** 1.75))
        profile.append((radius, start + bearing + (length - bearing - 0.1) * t))

    paint = TIPS.get(variant)

    if paint:
        cut = len(profile) - int(points * 0.34)
        lathe("jacket", profile[:cut + 1], metal(COPPER), root)
        lathe("tip", profile[cut:], material(f"tip_{variant}", paint, 0.0, 0.32), root)
    else:
        lathe("jacket", profile, metal(COPPER), root)

    return root


def shell(variant, location=(0, 0, 0)):
    root = bpy.data.objects.new("shell", None)
    bpy.context.collection.objects.link(root)
    root.location = location
    hull = material(f"hull_{variant}", SHELL_VARIANTS[variant], 0.0, 0.30, wear=0.05)
    r = 9.3
    head = [(r * 1.12, 0), (r * 1.14, 0.3), (r * 1.14, 1.3), (r * 1.03, 1.6), (r * 1.03, 16), (r * 1.015, 16.3)]
    lathe("head", head, metal(BRASS), root)
    lathe("base", [(r * 1.0, -0.02), (r * 1.0, 0.01)], metal(BASE_STAMP), root)
    lathe("primer", [(r * 0.36, -0.05), (r * 0.36, 0.01)], metal(COPPER), root)

    # Ribbed hull, closed by a crimp that folds in at the top.
    ribs = [(r, 16.2)]

    for step in range(1, 64):
        height = 16.2 + step * 0.72

        ribs.append((r + 0.05 * math.sin(step * 1.6), height))

    ribs += [(r * 0.99, 62.3), (r * 0.93, 63.6), (r * 0.74, 64.5), (r * 0.35, 63.9)]
    lathe("hull", ribs, hull, root)
    return root


def setup_scene(output):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.render.resolution_x = RESOLUTION
    scene.render.resolution_y = RESOLUTION
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(output)
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.35

    # The studio: seen across, from dark through a soft fill to a hot strip and back to dark.
    world = bpy.data.worlds.get("studio") or bpy.data.worlds.new("studio")
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output_node = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    coords = nodes.new("ShaderNodeTexCoord")
    split = nodes.new("ShaderNodeSeparateXYZ")
    to_ramp = nodes.new("ShaderNodeMapRange")
    to_ramp.inputs["From Min"].default_value = -1
    to_ramp.inputs["From Max"].default_value = 1
    ramp = nodes.new("ShaderNodeValToRGB")
    elements = ramp.color_ramp.elements

    for position, value in ((0.08, 0.05), (0.30, 0.30), (0.50, 0.75), (0.66, 7.0), (0.74, 7.0), (0.84, 0.25), (0.97, 0.03)):
        element = elements.new(position)
        element.color = (value, value, value * 0.98, 1)

    elements.remove(elements[0])
    elements.remove(elements[-1])
    ramp.color_ramp.interpolation = "EASE"
    links.new(coords.outputs["Generated"], split.inputs[0])
    links.new(split.outputs["X"], to_ramp.inputs["Value"])
    links.new(to_ramp.outputs[0], ramp.inputs["Fac"])
    links.new(ramp.outputs[0], background.inputs["Color"])
    links.new(background.outputs[0], output_node.inputs["Surface"])
    scene.world = world

    camera_data = bpy.data.cameras.new("camera")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new("camera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    return camera


def add_key_light(energy=1.0):
    """For what is not metal: a soft sun from the upper left."""
    data = bpy.data.lights.new("key", "SUN")
    data.energy = energy
    data.angle = math.radians(25)
    item = bpy.data.objects.new("key", data)
    item.rotation_euler = (math.radians(50), 0, math.radians(-35))
    bpy.context.collection.objects.link(item)


def frame(camera, focus, extent, view=(0.0, -1.0, 0.0), roll=0.0, lens=0.0):
    """Looks at focus along view. roll turns the picture, which keeps the light on the object; lens makes it perspective."""
    direction = Vector(view).normalized()
    distance = 500.0

    if lens:
        camera.data.type = "PERSP"
        camera.data.lens = lens
        camera.data.sensor_width = 36
        distance = extent * lens / 36
    else:
        camera.data.ortho_scale = extent

    camera.location = Vector(focus) + direction * distance
    camera.rotation_euler = ((-direction).to_track_quat("-Z", "Y").to_matrix() @ Matrix.Rotation(roll, 3, "Z")).to_euler()
    camera.data.clip_end = 5000


def clear():
    for item in list(bpy.context.collection.objects):
        bpy.data.objects.remove(item, do_unlink=True)


def render(name, build, folder, name_filter):
    if name_filter and name_filter not in name:
        return

    clear()
    camera = setup_scene(folder / name)
    build(camera)
    bpy.ops.render.render(write_still=True)
    print("rendered", name, flush=True)


def diagonal_extent(length, width):
    """The square a part of this length and width needs when it lies corner to corner at 42 degrees."""
    angle = math.radians(42)
    return (length * math.cos(angle) + width * math.sin(angle)) * 1.32


def build_round(caliber, variant):
    def build(camera):
        overall = CARTRIDGES[caliber][6]
        cartridge(caliber, variant)
        # Corner to corner, seen a little from below so the base shows; as big as its length and width allow.
        extent = diagonal_extent(overall, CARTRIDGES[caliber][0] * (1.16 if CARTRIDGES[caliber][8] == "rim" else 1.0))
        frame(camera, (0, 0, overall / 2), extent, (0.0, -1.0, -0.30), math.radians(-42), 180)

    return build


def build_shell(variant):
    def build(camera):
        shell(variant)
        frame(camera, (0, 0, 32), diagonal_extent(64.5, 21.2), (0.0, -1.0, -0.30), math.radians(-42), 180)

    return build


# The carton the packs come in, in mm: tools/render_pack_textures.py builds the ground model's texture from it.
CARTON = (97, 58.6, 36.6)


def pack_carton(caliber, variant, label, variant_label, second=None):
    """The printed carton, lid up, its front (with the band) towards -Y and the tuck flap on +X."""
    universal = caliber == "universal"
    base = (0.045, 0.06, 0.03) if universal else (0.13, 0.07, 0.028)
    kraft = material(f"kraft_{caliber}", base, 0.0, 0.72, wear=0.06, bump=0.10, bump_scale=9.0)
    flap = material(f"kraft_flap_{caliber}", tuple(v * 0.72 for v in base), 0.0, 0.72, wear=0.06, bump=0.10, bump_scale=9.0)
    ink = material(f"ink_{caliber}", (0.82, 0.80, 0.72) if universal else (0.002, 0.002, 0.002), 0.0, 0.9)

    width, depth, height = CARTON
    top = height

    block("carton", (width, depth, height), (0, 0, height / 2), kraft, 1.1)
    block("flap", (0.7, depth * 0.94, height * 0.70), (width / 2 + 0.25, 0, height * 0.60), flap, 0.25)
    block("flap_tuck", (0.5, depth * 0.40, height * 0.20), (width / 2 + 0.55, 0, height * 0.16), flap, 0.15)

    # A printed frame on the lid, and a band in the colour of the rounds' tips along its front.
    inset_x = width * 0.44
    inset_y = depth * 0.40
    line = 0.9

    for x, y, sx, sy in (
        (0, inset_y, inset_x * 2, line), (0, -inset_y, inset_x * 2, line),
        (inset_x, 0, line, inset_y * 2), (-inset_x, 0, line, inset_y * 2),
    ):
        block("rule", (sx, sy, 0.06), (x, y, top + 0.03), ink)

    if variant in TIPS:
        colour = material(f"band_{variant}", TIPS[variant], 0.0, 0.6)
        block("band", (inset_x * 2, depth * 0.16, 0.08), (0, -inset_y + depth * 0.09, top + 0.04), colour)
        block("band_side", (width * 0.98, 0.25, height * 0.18), (0, -depth / 2 - 0.05, height * 0.72), colour)

    font = bpy.data.fonts.load(FONT) if Path(FONT).exists() else None

    def lid_text(body, y, text_size):
        bpy.ops.object.text_add(location=(0, y, top + 0.1))
        text = bpy.context.object
        text.data.body = body
        text.data.align_x = "CENTER"
        text.data.align_y = "CENTER"
        text.data.size = text_size
        text.data.extrude = 0.015

        if font:
            text.data.font = font

        text.data.materials.append(ink)

    lid_text(label.upper(), depth * 0.14, width * (0.125 if len(label) <= 10 else 0.095))
    lid_text(second or ("BALL" if variant == "basic" else variant_label.upper()), -depth * 0.10, width * 0.062)


def clip_line(variant, variant_label, rounds):
    """The second line on a carton of stripper clips: what is inside and how it is clipped."""
    kind = "BALL" if variant == "basic" else variant_label.upper()
    return f"{kind}  -  {ITEM_TABLE.CLIPS_PER_PACK} X {rounds} ON CLIPS"


def build_pack(caliber, variant, label, variant_label, line=None):
    def build(camera):
        add_key_light()
        pack_carton(caliber, variant, label, variant_label, line)
        width, depth, height = CARTON

        # A carton of stripper clips shows one of its clips lying in front of it.
        if line:
            before = set(bpy.context.collection.objects)
            stripper_clip(caliber, variant, ITEM_TABLE.CLIPS[caliber])
            holder = bpy.data.objects.new("clip_holder", None)
            bpy.context.collection.objects.link(holder)

            for item in set(bpy.context.collection.objects) - before - {holder}:
                if item.parent is None:
                    item.parent = holder

            length = CARTRIDGES[caliber][6]
            # Small enough that the whole clip stays in the picture, whatever its length.
            scale = min(70.0 / (CARTRIDGES[caliber][0] * 1.06 * ITEM_TABLE.CLIPS[caliber]), 62.0 / length, 0.95)
            holder.scale = (scale, scale, scale)
            # Tips towards the viewer, the clip's back against the carton.
            holder.rotation_euler = (math.radians(90), 0, math.radians(-8))
            holder.location = (width * 0.02, -depth * 0.56, CARTRIDGES[caliber][0] * scale * 0.62)
        # Two of its own rounds in front of it, as big as they are next to the same carton: only very long ones shrink.
        elif caliber == "12g":
            shell(variant, (-width * 0.30, -depth * 0.86, 0))
            shell(variant, (width * 0.26, -depth * 0.98, 0))
        else:
            length = CARTRIDGES[caliber][6]
            scale = min(62.0 / length, 0.95) if length > 60 else 0.95
            lying = CARTRIDGES[caliber][0] * scale / 2

            cartridge(caliber, variant, scale, (-width * 0.30, -depth * 0.78, lying), (math.radians(90), 0, math.radians(102)))
            cartridge(caliber, variant, scale, (width * 0.28, -depth * 0.92, lying), (math.radians(90), 0, math.radians(84)))

        frame(camera, (0, -depth * 0.20, height * 0.40), width * 1.34, (0.42, -0.85, 0.72))

    return build


def build_belt(caliber, variant):
    def build(camera):
        band = metal(PARKERIZED)
        hole = material("link_hole", (0.015, 0.012, 0.01), 0.0, 0.6)
        diameter = CARTRIDGES[caliber][0]
        case = CARTRIDGES[caliber][5]
        overall = CARTRIDGES[caliber][6]
        radius = diameter / 2
        count = 7
        pitch = diameter * 1.11
        start = -pitch * (count - 1) / 2

        def link(x, y, low, high, r):
            ring = lathe("link", [(r - 0.05, low), (r + radius * 0.07, low + 0.2), (r + radius * 0.07, high - 0.2), (r - 0.05, high)], band)
            ring.location = (x, y, 0)

        for index in range(count):
            x = start + index * pitch
            # A slight sag, so it reads as a flexible belt rather than a row.
            t = (index - (count - 1) / 2) / count
            y = 2.0 * diameter * t * t
            turn = -t * 0.42
            kind = variant if variant != "basic" and index % 3 == 1 else "basic"
            cartridge(caliber, kind, 1.0, (x, y, 0), (0, 0, turn))

            # M13 style links: a wide band around one round, two narrow ones around the next, joined by a pin behind.
            if index % 2 == 0:
                link(x, y, case * 0.30, case * 0.64, radius * 1.01)
                pin = lathe("hole", [(radius * 0.32, 0), (radius * 0.32, 0.3)], hole)
                pin.location = (x, y - radius * 1.09, case * 0.47)
                pin.rotation_euler = (math.radians(90), 0, 0)
            else:
                link(x, y, case * 0.25, case * 0.38, radius * 1.02)
                link(x, y, case * 0.54, case * 0.67, radius)

            if index < count - 1:
                spine = block("spine", (pitch, radius * 0.22, case * 0.086), (x + pitch / 2, y + radius * 1.08, case * 0.47), band, 0.2)
                spine.rotation_euler = (0, 0, turn)

        extent = max(pitch * count * 1.45, overall * 1.75)
        frame(camera, (0, diameter * 0.2, overall * 0.49), extent, (0.10, -1.0, 0.30), math.radians(12), 200)

    return build


def stripper_clip(caliber, variant, rounds):
    """Rounds standing side by side in a stripper clip: a strip under their bases, its edges folded over their rims."""
    strip = metal(((0.20, 0.205, 0.20), 1.0, 0.34))
    base_d = CARTRIDGES[caliber][0] * (1.16 if CARTRIDGES[caliber][8] == "rim" else 1.0)
    pitch = base_d * 1.06
    length = pitch * rounds + 3

    for index in range(rounds):
        cartridge(caliber, variant, 1.0, (-pitch * (rounds - 1) / 2 + index * pitch, 0, 2.0))

    block("clip", (length, base_d * 1.25, 0.9), (0, 0, 1.1), strip, 0.15)

    for side in (-1, 1):
        block("clip_edge", (length, 0.9, 3.4), (0, side * base_d * 0.62, 2.5), strip, 0.15)
        block("clip_lip", (length, base_d * 0.16, 0.8), (0, side * base_d * 0.54, 4.0), strip, 0.12)

    return length


def build_clip(caliber, variant, rounds):
    def build(camera):
        add_key_light(0.8)
        length = stripper_clip(caliber, variant, rounds)
        overall = CARTRIDGES[caliber][6]
        # Lying across the picture, seen a little from the side, as the speedloader's clip is.
        frame(camera, (0, 0, overall * 0.5), max(length, overall) * 1.3, (0.34, -1.0, 0.20), math.radians(-90), 200)

    return build


def build_speedloader(camera):
    """As in the field: a thin steel guide on the magazine's lips, a stripper clip of rounds sliding down through it."""
    add_key_light(0.8)
    steel = metal(PARKERIZED)
    strip = metal(((0.20, 0.205, 0.20), 1.0, 0.34))

    # Built with the rounds standing and the clip lying along X; the camera's roll lays them down in the picture.
    pitch = 10.2

    for index in range(5):
        x = -pitch * 2 + index * pitch
        offset = 2.4 if index % 2 else -2.4
        cartridge("556x45", "dual", 1.0, (x, offset, 2.0))

    # The clip: a flat strip under the rounds' bases, with its edges folded up over their rims.
    block("clip", (pitch * 5 + 7, 13.5, 0.9), (0, 0, 1.1), strip, 0.15)

    for side in (-1, 1):
        block("clip_edge", (pitch * 5 + 7, 0.9, 3.4), (0, side * 6.9, 2.5), strip, 0.15)
        block("clip_lip", (pitch * 5 + 7, 1.9, 0.8), (0, side * 6.0, 4.0), strip, 0.12)

    # The guide below the clip's end: a narrow channel with a flared foot that sits on the magazine.
    guide_x = -(pitch * 2.5 + 13)
    block("guide_back", (26, 1.2, 12), (guide_x, 0, 0.6), steel, 0.25)

    for side in (-1, 1):
        block("guide_cheek", (26, 2.6, 1.3), (guide_x, side * 1.9, 6.0), steel, 0.25)
        block("guide_cheek", (26, 2.6, 1.3), (guide_x, side * 1.9, -4.8), steel, 0.25)

    block("guide_foot", (4, 13, 18), (guide_x - 14, 0, 0.6), steel, 0.5)
    block("guide_tab", (9, 2.0, 9), (guide_x - 19, 0, 0.6), steel, 0.3)

    frame(camera, (-16, 0, 22), 128, (0.34, -1.0, 0.20), math.radians(-90), 200)


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    folder = Path(args[0]).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    name_filter = args[1] if len(args) > 1 else ""

    for caliber, entry in CARTRIDGES.items():
        for variant in ("basic",) + entry[9]:
            render(f"round_{caliber}_{variant}", build_round(caliber, variant), folder, name_filter)

    for variant in SHELL_VARIANTS:
        render(f"round_12g_{variant}", build_shell(variant), folder, name_filter)

    for caliber, (label, _, _, _, variants) in ITEM_TABLE.CALIBERS.items():
        for variant, (variant_label, _) in ({"basic": ("Basic", ())} | variants).items():
            render(f"pack_{caliber}_{variant}", build_pack(caliber, variant, label, variant_label), folder, name_filter)

    for caliber, rounds in ITEM_TABLE.CLIPS.items():
        label = ITEM_TABLE.CALIBERS[caliber][0]

        for variant, (variant_label, _) in ITEM_TABLE.variants_of(caliber).items():
            render(f"clip_{caliber}_{variant}", build_clip(caliber, variant, rounds), folder, name_filter)
            line = clip_line(variant, variant_label, rounds)
            render(f"packclips_{caliber}_{variant}", build_pack(caliber, variant, label, variant_label, line), folder, name_filter)

    for caliber, variant in ITEM_TABLE.BELTS:
        render(f"belt_{caliber}_{variant}", build_belt(caliber, variant), folder, name_filter)

    render("speedloader", build_speedloader, folder, name_filter)


if __name__ == "__main__":
    main()
