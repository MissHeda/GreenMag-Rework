"""Generates the item configs of addons/items/cfg from the table below.

Run it after changing the table (no arguments):

    python tools/generate_items.py

Every caliber gets one loose round per variant and its packs in the sizes the real cartridges are sold or issued in; the belt types below get one class per
length (1-200 rounds), because an item's mass cannot change at runtime. Mass is config mass, a tenth
of a pound per unit.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "addons" / "items" / "cfg"

# The packs every caliber comes in: small, medium and large (drop models s, m and l).
PACKS = (10, 30, 60)

# The sizes before 1.2.0, the original's 10 to 60 and the real boxes below: their classes stay, hidden, so saved
# loadouts and missions that hold them keep working.
CLASSIC_PACKS = (10, 20, 30, 40, 50, 60)

# The boxes the real cartridges come in: pistol rounds in boxes of 50, rifle rounds in boxes of 20 (Soviet 5.45 in
# paper packs of 30, NATO 5.56 also issued as three 10-round stripper clips), German 7.92 as three 5-round clips, the
# large calibers in boxes of 10, shotgun shells by 5 and 25. Universal ammunition has no real box, 30 suits most magazines.
PACK_SIZES = {
    "universal": (30,),
    "9x19": (50,),
    "9x21": (50,),
    "9x18": (16,),
    "9x39": (20,),
    "762x25": (50,),
    "45acp": (50,),
    "46x30": (50,),
    "570x28": (50,),
    "545x39": (30,),
    "556x45": (20, 30),
    "580x42": (20,),
    "650x39": (20,),
    "762x39": (20,),
    "300blk": (20,),
    "762x51": (20,),
    "762x54": (20,),
    "792x57": (15,),
    "303": (20,),
    "50bw": (20,),
    "93x64": (20,),
    "338": (10,),
    "408": (10,),
    "127x54": (10,),
    "127x99": (10,),
    "127x108": (10,),
    "12g": (5, 25),
}
# The calibers issued on stripper clips, and the rounds on one clip: 10 for the intermediate rifle rounds, 5 for the
# full-power ones. Every variant of them comes as a clip and in cartons of clips.
CLIPS = {
    "universal": 10,
    "556x45": 10,
    "545x39": 10,
    "580x42": 10,
    "762x39": 10,
    "762x51": 5,
    "762x54": 5,
    "792x57": 5,
    "303": 5,
}

# The cartons of clips, in clips per carton: three everywhere, and NATO 5.56 also two to a box as in a bandoleer's pocket.
CLIP_BOXES = {caliber: (3,) for caliber in CLIPS} | {"556x45": (2, 3)}
CLIP_MASS_FACTOR = 1.05
ARSENAL_BELTS = (50, 100, 150, 200)
BELT_LENGTH = 200

# Packaging and links weigh a little on top of the rounds.
PACK_MASS_FACTOR = 1.1
BELT_MASS_FACTOR = 1.15

TRACER = ("Tracer", ("tracer",))
IR = ("IR Tracer", ("irtracer", "_ir_", "tracer_ir"))


def v(label, *tokens):
    return (label, tokens)


# id: label, picture family, mass of a round, tokens looked for in the magazine's class, its ammo's class and
# its description (lowercase, without dots and spaces), variants beside "basic".
CALIBERS = {
    # Fits every magazine of the game, of any mod, known or not: see fnc_ammoSource. It has no tokens to be detected by.
    "universal": ("Universal", "rifle", 0.17, (), {}),
    "9x19": ("9x19 mm", "pistol", 0.10, ("9x19", "9mm_para"), {"tracer": TRACER}),
    "9x21": ("9x21 mm", "pistol", 0.10, ("9x21",), {"tracer": TRACER}),
    "9x18": ("9x18 mm", "pistol", 0.09, ("9x18",), {}),
    "9x39": ("9x39 mm", "rifle", 0.20, ("9x39",), {}),
    "762x25": ("7.62x25 mm", "pistol", 0.10, ("762x25",), {}),
    "45acp": (".45 ACP", "pistol", 0.15, ("45acp", "45_acp", "11x23"), {"tracer": TRACER}),
    "46x30": ("4.6x30 mm", "pistol", 0.06, ("46x30",), {}),
    "570x28": ("5.7x28 mm", "pistol", 0.07, ("570x28", "57x28"), {}),
    "545x39": ("5.45x39 mm", "rifle", 0.12, ("545x39",), {"tracer": TRACER}),
    "556x45": ("5.56x45 mm", "rifle", 0.15, ("556x45", "baf_556", "_556_"), {
        "tracer": TRACER,
        "irtracer": IR,
        "m995ap": v("M995 AP", "m995"),
        "mk262": v("Mk 262", "mk262"),
        "mk318": v("Mk 318", "mk318"),
        "dual": v("Dual Purpose", "_uw", "dualpurpose"),
    }),
    "580x42": ("5.8x42 mm", "rifle", 0.15, ("580x42", "58x42"), {"tracer": TRACER}),
    "650x39": ("6.5x39 mm", "rifle", 0.17, ("650x39", "65x39"), {"tracer": TRACER, "irtracer": IR}),
    "762x39": ("7.62x39 mm", "rifle", 0.20, ("762x39",), {"tracer": TRACER}),
    "300blk": (".300 Blackout", "rifle", 0.17, ("300blk", "300aac", "_blk"), {}),
    "762x51": ("7.62x51 mm", "rifle", 0.25, ("762x51", "baf_762", "_762_"), {
        "tracer": TRACER,
        "irtracer": IR,
        "m118lr": v("M118 LR", "m118"),
        "m993ap": v("M993 AP", "m993"),
        "mk316": v("Mk 316", "mk316"),
        "mk319": v("Mk 319", "mk319"),
        "sd": v("Subsonic", "subsonic", "_sd"),
    }),
    "762x54": ("7.62x54 mmR", "rifle", 0.25, ("762x54",), {"tracer": TRACER}),
    "792x57": ("7.92x57 mm", "rifle", 0.27, ("792x57",), {}),
    "303": (".303 British", "rifle", 0.25, ("303br", "303_", "_303"), {}),
    "50bw": (".50 Beowulf", "rifle", 0.35, ("50bw", "50beowulf"), {}),
    "93x64": ("9.3x64 mm", "heavy", 0.40, ("93x64",), {}),
    "338": (".338", "heavy", 0.45, ("338", "86x70"), {
        "300gr": v("300 gr", "300gr"),
        "api526": v("API526", "api526"),
    }),
    "408": (".408", "heavy", 0.65, ("408",), {"205gr": v("205 gr", "205gr")}),
    "127x54": ("12.7x54 mm", "heavy", 0.70, ("127x54",), {}),
    "127x99": ("12.7x99 mm", "heavy", 1.20, ("127x99", "50bmg", "50cal"), {
        "amax": v("A-MAX", "amax"),
        "api": v("API", "_api"),
    }),
    "127x108": ("12.7x108 mm", "heavy", 1.30, ("127x108",), {"apds": v("APDS", "apds")}),
    "12g": ("12 Gauge", "shell", 0.40, ("12gauge", "12ga", "12g_", "_12g"), {"slug": v("Slug", "slug")}),
}

BELTS = (
    ("universal", "basic"),
    ("127x108", "basic"),
    ("127x99", "basic"),
    ("338", "basic"),
    ("556x45", "basic"),
    ("556x45", "tracer"),
    ("650x39", "basic"),
    ("650x39", "tracer"),
    ("650x39", "irtracer"),
    ("762x51", "basic"),
    ("762x51", "tracer"),
    ("762x54", "basic"),
    ("762x54", "tracer"),
    ("93x64", "basic"),
)

HEADER = "// Generated by tools/generate_items.py - change the table there, not this file.\n"


def pack_sizes(caliber):
    """Every pack class of a caliber, the hidden ones before 1.2.0 included, smallest first."""
    return sorted(set(PACK_SIZES[caliber]) | set(CLASSIC_PACKS) | set(PACKS))


def pack_model(size):
    """The carton a pack lies on the ground as: small, medium or large."""
    return "s" if size <= 20 else "m" if size <= 40 else "l"


def mass(value):
    return f"{max(value, 0.01):.3f}".rstrip("0").rstrip(".")


def array(items):
    return "{" + ",".join(f'"{item}"' for item in items) + "}"


def item_name(label, variant):
    return label if variant == "Basic" else f"{label} {variant}"


def variants_of(caliber):
    """Basic first, tracer last: the first variant whose token matches wins, and "irtracer" contains "tracer"."""
    variants = {"basic": ("Basic", ())} | CALIBERS[caliber][4]
    tracer = variants.pop("tracer", None)

    if tracer:
        variants["tracer"] = tracer

    return variants


def rounds_and_packs():
    lines = [HEADER]

    for caliber, (label, family, round_mass, _, _) in CALIBERS.items():
        for variant, (variant_label, _) in variants_of(caliber).items():
            name = item_name(label, variant_label)
            round_class = f"gmr_round_{caliber}_{variant}"

            lines.append(
                f'class {round_class}: gmr_round_base {{scope = 2; scopeArsenal = 2; scopeCurator = 2; displayName = "{name} Round"; '
                f'picture = "\\z\\gmr\\addons\\items\\data\\round_{caliber}_{variant}.paa"; '
                f'gmr_caliber = "{caliber}"; gmr_variant = "{variant}"; gmr_round = "{round_class}"; '
                f"class ItemInfo: CBA_MiscItem_ItemInfo {{mass = {mass(round_mass)};}};}};"
            )

            for size in pack_sizes(caliber):
                shown = 2 if size in PACKS else 0

                lines.append(
                    f"class gmr_pack_{caliber}_{variant}_{size}: gmr_pack_base {{"
                    f'displayName = "{name} Pack ({size} rds)"; '
                    f'picture = "\\z\\gmr\\addons\\items\\data\\pack_{caliber}_{variant}.paa"; '
                    f'model = "\\z\\gmr\\addons\\items\\data\\packs\\pack_{caliber}_{variant}_{pack_model(size)}.p3d"; '
                    f"scopeArsenal = {shown}; scopeCurator = {shown}; gmr_rounds = {size}; "
                    f'gmr_caliber = "{caliber}"; gmr_variant = "{variant}"; gmr_round = "{round_class}"; '
                    f"class ItemInfo: CBA_MiscItem_ItemInfo {{mass = {mass(round_mass * size * PACK_MASS_FACTOR)};}};}};"
                )

    (OUT / "rounds.hpp").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(lines) - 1


def clip_names():
    """(caliber, variant, clip class, rounds on a clip) of every clip."""
    for caliber, rounds in CLIPS.items():
        for variant in variants_of(caliber):
            yield caliber, variant, f"gmr_clip_{caliber}_{variant}", rounds


def clip_cartons():
    """(caliber, variant, clip class, carton class, clips in it, rounds on a clip) of every carton of clips."""
    for caliber, variant, clip, rounds in clip_names():
        for count in CLIP_BOXES[caliber]:
            yield caliber, variant, clip, f"gmr_clips_{caliber}_{variant}_{count}", count, rounds


def clips():
    """The stripper clips, and the cartons they come in: a carton's gmr_round is its clip, its gmr_rounds the clips."""
    lines = [HEADER]

    for caliber, variant, clip, rounds in clip_names():
        label, _, round_mass, _, _ = CALIBERS[caliber]
        name = item_name(label, variants_of(caliber)[variant][0])
        common = f'gmr_caliber = "{caliber}"; gmr_variant = "{variant}"; '

        lines.append(
            f'class {clip}: gmr_clip_base {{displayName = "{name} Stripper Clip ({rounds} rds)"; '
            f'picture = "\\z\\gmr\\addons\\items\\data\\clip_{caliber}_{variant}.paa"; '
            f'model = "\\z\\gmr\\addons\\items\\data\\drop_clip_{rounds}.p3d"; '
            f'{common}gmr_rounds = {rounds}; gmr_round = "gmr_round_{caliber}_{variant}"; '
            f"class ItemInfo: CBA_MiscItem_ItemInfo {{mass = {mass(round_mass * rounds * CLIP_MASS_FACTOR)};}};}};"
        )

    for caliber, variant, clip, carton, count, rounds in clip_cartons():
        label, _, round_mass, _, _ = CALIBERS[caliber]
        name = item_name(label, variants_of(caliber)[variant][0])
        lines.append(
            f'class {carton}: gmr_pack_base {{displayName = "{name} Pack on Clips ({count}x{rounds} rds)"; '
            f'picture = "\\z\\gmr\\addons\\items\\data\\packclips_{caliber}_{variant}_{count}.paa"; '
            f'model = "\\z\\gmr\\addons\\items\\data\\packs\\clips_{caliber}_{variant}_{count}.p3d"; '
            f'scopeArsenal = 2; scopeCurator = 2; gmr_caliber = "{caliber}"; gmr_variant = "{variant}"; '
            f'gmr_rounds = {count}; gmr_round = "{clip}"; '
            f"class ItemInfo: CBA_MiscItem_ItemInfo {{"
            f"mass = {mass(round_mass * rounds * count * CLIP_MASS_FACTOR * PACK_MASS_FACTOR)};}};}};"
        )

    (OUT / "clips.hpp").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(lines) - 1


def belts():
    lines = [HEADER]

    for caliber, variant in BELTS:
        label, _, round_mass, _, _ = CALIBERS[caliber]
        name = item_name(label, variants_of(caliber)[variant][0])
        base = f"gmr_belt_{caliber}_{variant}"

        lines.append(
            f'class {base}: gmr_belt_base {{displayName = "{name} Belt"; '
            f'picture = "\\z\\gmr\\addons\\items\\data\\belt_{caliber}_{variant}.paa"; '
            f'gmr_caliber = "{caliber}"; gmr_variant = "{variant}"; gmr_round = "gmr_round_{caliber}_{variant}"; '
            f'gmr_beltType = "{base}_";}};'
        )

        for length in range(1, BELT_LENGTH + 1):
            shown = 2 if length in ARSENAL_BELTS else 1

            lines.append(
                f'class {base}_{length}: {base} {{scope = 2; displayName = "{name} Belt ({length} rds)"; '
                f"scopeArsenal = {shown}; scopeCurator = {shown}; gmr_rounds = {length}; "
                f"class ItemInfo: CBA_MiscItem_ItemInfo {{mass = {mass(round_mass * length * BELT_MASS_FACTOR)};}};}};"
            )

    (OUT / "belts.hpp").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(lines) - 1


def calibers():
    lines = [HEADER, "class gmr_calibers {"]

    for caliber, (label, _, _, tokens, _) in CALIBERS.items():
        packs = ",".join(str(size) for size in sorted(PACKS, reverse=True))
        lines.append(f'    class {caliber} {{displayName = "{label}"; tokens[] = {array(tokens)}; packs[] = {{{packs}}};')
        lines.append("        class variants {")

        for variant, (variant_label, variant_tokens) in variants_of(caliber).items():
            lines.append(
                f'            class {variant} {{displayName = "{variant_label}"; tokens[] = {array(variant_tokens)};}};'
            )

        lines.append("        };")
        lines.append("    };")

    lines.append("};")
    (OUT / "calibers.hpp").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def public_classes():
    """The classes Zeus may offer, for CfgPatches."""
    names = ["gmr_speedloader"]

    for caliber in CALIBERS:
        for variant in variants_of(caliber):
            names.append(f"gmr_round_{caliber}_{variant}")
            names += [f"gmr_pack_{caliber}_{variant}_{size}" for size in PACKS]

    for caliber, variant in BELTS:
        names += [f"gmr_belt_{caliber}_{variant}_{length}" for length in ARSENAL_BELTS]

    names += [clip for _, _, clip, _ in clip_names()]
    names += [carton for _, _, _, carton, _, _ in clip_cartons()]

    text = HEADER + ",\n".join(f'"{name}"' for name in names) + "\n"
    (OUT / "public_classes.hpp").write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    calibers()
    public_classes()
    print(f"{rounds_and_packs()} round and pack classes, {clips()} clip classes, {belts()} belt classes")
