"""Writes the models this mod's items show when they lie on the ground, as plain MLOD P3D.

    python tools/make_drop_models.py [preview folder]

A loose round, a carton of rounds in three sizes (up to 20, up to 40 and up to 60 rounds), a piece of linked belt and
the speedloader. Real sizes, in metres, standing on the origin: X across, Y up, Z along. An item on the ground lies
the way the game lays it: what its model has along Z points up. So every model is built standing, then turned a
quarter round X before it is written (lay_down), and loose rounds lie along X, which stays level either way. With a preview folder every
model is also written there as OBJ.

It shares the model writer with tools/make_mag_models.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_mag_models import BRASS, COPPER, RVMAT, STEEL, Model, texture, write_obj, write_p3d  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "addons" / "items" / "data"
MATERIAL = "z\\gmr\\addons\\items\\data\\gmr_plain.rvmat"

CARDBOARD = texture(0.72, 0.58, 0.40)
CARDBOARD_DARK = texture(0.62, 0.49, 0.33)
LABEL = texture(0.86, 0.84, 0.76)
STRIPE = texture(0.18, 0.32, 0.16)
POLYMER = texture(0.08, 0.08, 0.085)


def lay_down(model):
    """Turns the model a quarter round X, so its Y (up while built) becomes the Z the game stands an item on."""
    model.points = [(x, -z, y) for x, y, z in model.points]
    return model


def cartridge(model, x, y, z, length=0.057, radius=0.0048, along="z"):
    """A round lying along Z (or X) with its middle at x, y, z."""
    half = length / 2

    if along == "z":
        start, end = (x, y, z - half), (x, y, z + half)
    else:
        start, end = (x - half, y, z), (x + half, y, z)

    model.cylinder(start, end, radius, BRASS, sides=10, tip=(COPPER, length * 0.32))


def round_model():
    model = Model()
    cartridge(model, 0, 0.0048, 0, along="x")
    return model


def carton(width, height, length):
    """A cardboard carton with its flaps, a label all round and a coloured stripe on the label."""
    model = Model()
    model.box((0, height / 2, 0), (width, height, length), CARDBOARD)
    # The end flaps stand out a hair, darker where they fold.
    for side in (-1, 1):
        model.box((0, height / 2, side * (length / 2 + 0.0005)), (width * 0.96, height * 0.94, 0.001), CARDBOARD_DARK)

    model.box((0, height * 0.5, 0), (width + 0.0012, height * 0.46, length * 0.62), LABEL)
    model.box((0, height * 0.5, 0), (width + 0.0016, height * 0.1, length * 0.62), STRIPE)
    return model


def belt_model(rounds=10):
    """A short piece of belt lying flat: rounds side by side along X, each in its link."""
    model = Model()
    pitch = 0.0125

    for index in range(rounds):
        x = (index - (rounds - 1) / 2) * pitch
        model.box((x, 0.0012, -0.004), (0.010, 0.0024, 0.020), STEEL)
        cartridge(model, x, 0.0055, 0, length=0.071, radius=0.0055)

    return model


def speedloader():
    """A rifle magazine loader: a sleeve that fits over the magazine's top, with its thumb plunger."""
    model = Model()
    model.box((0, 0.035, 0), (0.030, 0.07, 0.066), POLYMER)
    model.box((0, 0.074, -0.01), (0.014, 0.008, 0.03), POLYMER)
    return model


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    preview = Path(sys.argv[1]) if len(sys.argv) > 1 else None
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
        lay_down(model)
        write_p3d(OUT / f"{name}.p3d", model, MATERIAL)

        if preview:
            preview.mkdir(parents=True, exist_ok=True)
            write_obj(preview / f"{name}.obj", model)

    cfg = ["class CfgSkeletons {", "    class Default {", "        isDiscrete = 1;", '        skeletonInherit = "";',
           "        skeletonBones[] = {};", "    };", "};", "class CfgModels {", "    class Default {",
           '        sectionsInherit = "";', "        sections[] = {};", '        skeletonName = "";', "    };"]
    cfg += [f"    class {name}: Default {{}};" for name in models]
    cfg.append("};")
    (OUT / "model.cfg").write_text("\n".join(cfg) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(models)} drop models written: {', '.join(models)}")


if __name__ == "__main__":
    main()
