"""Builds the compat addons of the Second World War mods (addons/compat_ifa3, _fow, _nf, _csa38, _ifa3lib, _jmssa).

Like tools/generate_compat.py: every bullet magazine of a caliber this mod knows gets gmr_caliber and gmr_belt, each
mod in its own addon that is skipped when the mod is not loaded. These mods need more than the name of a magazine
tells, so there are tables below: CALIBER names the round of magazines whose class or ammo says something else
(CSA38 fires its Mosin with ".70 British" ammo), BELT says which machine gun magazines are belts and which are pans,
drums and strips of loose rounds, and DISABLED lists what is no ammunition at all (flamethrower fuel, blades, the
placeholders of scripted reloads).

Every magazine also gets its gmr_variant, for the advanced ammunition: "tracer" where the name says tracer and every
round is one, "ap" where its ammo is armour-piercing (AP_AMMO), "basic" for all else, so the game does not guess from
tracersEvery (armour-piercing magazines set it too) or from the ammo's name (Northern Fronts' Maxim belts). A tracer
or armour-piercing magazine gets gmr_family where the game could not pair it with its ball version by their names:
from BALL_NAME, which turns its class name into the ball magazine's, or from FAMILY. The magazines left without a ball
version are listed at the end.

The configs are read straight from the PBOs (tools/pbo_config.py), the game's own for the base classes included.
    python tools/generate_compat_ww2.py [workshop folder] [Arma 3 folder] [more folders of mods ...]
Defaults: C:/SteamLibrary/steamapps/workshop/content/107410 and the "common/Arma 3" beside it.

A mod is found by its Workshop item or, where it has none of its own, by one of its PBOs: JM's Second Assault and
the IFA3 Liberation ModPack (ifa3.ru) are released as downloads and put on the Workshop by whoever plays them, so
every copy has another number, and not every copy is the same version. Such a mod is looked for in the further folders given, and failing that in the Workshop
folder and beside the game (@mods), where the copy updated last is taken. The addon then fits that version: with a
copy that lacks one of the addons it needs it does not load, and the magazines are told by their names as before.
"""
import glob
import hashlib
import json
import os
import re
import sys
import tempfile

import pbo_config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBERS = os.path.join(ROOT, "addons", "items", "cfg", "calibers.hpp")
TABLES = ("cfgpatches", "cfgmagazines", "cfgammo", "cfgweapons")

# Who these addons are by, in their CfgPatches.
AUTHOR = "Davidaf"

# addon, mod name, its Workshop item, and for a mod without one of its own a PBO every copy of it has
MODS = [
    ("compat_ifa3", "IFA3 AIO", "2648308937", ""),
    ("compat_fow", "Faces of War", "891433622", ""),
    ("compat_nf", "Northern Fronts", "1507586063", ""),
    ("compat_csa38", "CSA38", "641305739", ""),
    ("compat_ifa3lib", "IFA3 Liberation", "", "ifa3_comp.pbo"),
    ("compat_jmssa", "Second Assault", "", "JMSSA_weapons.pbo"),
]

# Magazine class (lowercase, matched from its start) -> caliber, for those whose own name or ammo is not the round the
# weapon really takes. Looked at before anything else.
CALIBER = [
    # IFA3: two hidden leftovers named after another pistol's round.
    (r"lib_7rnd_9x19$", "765x17"),
    (r"lib_7rnd_765x17$", "9x19"),
    # Faces of War: the M1919's belts fire the .303 ammo class, the Webley's cylinder the .45 ACP one.
    (r"fow_\d+rnd_m1919", "762x63"),
    (r"fow_6rnd_455$", "455"),
    # IFA3: the Webley's cylinder names its round by the number alone.
    (r"lib_6rnd_455$", "455"),
    # Northern Fronts: the Swedish Kg m/21 is a 6.5 mm BAR, the m/1893 a 7.5 mm Nagant, and the Lahti L-39 anti-tank
    # rifle fires the long Solothurn round.
    (r"north_20rnd_kg21", "65x55"),
    (r"north_6rnd_m1893", "75x23"),
    (r"north_10rnd_20mm_l39", "20x138"),
    # CSA38 spells its rounds its own way and shares ammo classes between calibers.
    (r"csa38_5x7_62_54r", "762x54"),
    (r"csa38_7_7_", "303"),
    (r"csa38_7_5_", "75x54"),
    (r"csa38_7_63mm", "762x25"),
    (r"csa38_7_65mm_", "765x17"),
    (r"csa38_mas38mag", "765x20"),
    (r"csa38_6_35mm", "635x16"),
    (r"csa38_6rnd_38sw", "38sw"),
    (r"csa38_8(_00|x56)_", "8x56r"),
    (r"csa38_9_?mm_\d+xbrowning", "9x17"),
    (r"csa38_9_?mm_", "9x19"),
    (r"csa38_5_13_9x99", "139x99"),
    (r"csa38_m1919a4mg", "762x63"),
    (r"csa38_7_92_", "792x57"),
    # JMSSA: the PzB 39's magazine is named after the Boys' round.
    (r"jmssa_10rnd_139x99_ap", "792x94"),
]

# Magazine class (lowercase, matched from its start) -> belt or not, where the rules of belt() get it wrong.
BELT = [
    # Saddle drums and pans are filled with loose rounds.
    (r"lib_75rnd_792x57", False),
    (r"csa38_mg34mg2", False),
    (r"jmssa_[12]00rnd_770x56_vikers", False),  # the Vickers K's pans; the Vickers' own 250 are belts
    (r"jmssa_150rnd_750x54_reibel", False),
    (r"csa38_7_7_100x56r", False),
    (r"csa38_dtvz29mag", False),
    (r"lib_440rnd_762x54", False),
    # A carton of three clips for the Mosin, not a belt box.
    (r"north_15rnd_m39_box", False),
    # Every 50-round drum of the MG 34 and 42 holds a belt, whatever else takes it.
    (r"jmssa_50rnd_792x57", True),
]

# No ammunition, or no magazine of its own: left alone entirely.
DISABLED = (
    r".*flam", r".*fake", r".*dummy", r"katana", r"ka_knife", r"lib_.*_empty$", r"lib_empty_magazine",
    r"north_.*_empty$", r".*blank",
    # Northern Fronts' gun ammunition, which its crews carry: boxes of 37 to 114 mm shells are not refilled by hand.
    r"north_\d+shell_", r"north_\d+rnd_\d+_\d+mm_",
)

# Left out of the addons: another pack of the same modset declares the class with a different parent, and one more
# declaration here would only add to that conflict. Classes the mods read here declare twice are left out by themselves.
SKIPPED = (r"fow_fake$",)

# What marks a tracer magazine in its class name: "tracer", IFA3's _t, _t30 and _t46 (not _t2 and the like, which mix
# ball and tracer), Northern Fronts' _T before _Inf, and JMSSA's colours.
TRACER_NAME = re.compile(r"tracer|_t(30|46)?$|_t_inf$|_(red|green|yellow)(_mag)?$")

# Ammo classes that are armour-piercing: the German S.m.K., the Soviet P-41 and B-30, CSA38's second Mauser load and
# its .303 AP, JMSSA's AP and the Lebel's balle P. Heavy ball (sS, D, Mk VIII, M1) counts as ball.
AP_AMMO = re.compile(r"smk|_p41|_b30|mauser2|britishap|_ap_ball|8x50r_p_ball")

# How the class name (lowercase) of a tracer or armour-piercing magazine becomes that of its ball version: the first
# that names a magazine there is gives the family.
BALL_NAME = [
    (r"tracer$", ""), (r"_smk$", ""), (r"_ap$", ""), (r"_b30$", ""), (r"_ap_mag$", "_mag"), (r"ap$", ""),
    (r"apmg$", "mg"), (r"mauser2", "mauser"), (r"(cz|kar)2$", r"\1"),
]

# Magazine class (lowercase, matched from its start) -> gmr_family: the name the game pairs the versions of a magazine
# by (fnc_siblingMagazine), where neither their own names nor BALL_NAME do it.
FAMILY = [
    # IFA3's T-30 and T-46 are both the tracer of the plain Mosin and SVT magazines.
    (r"lib_(\d+)rnd_762x54_t(30|46)$", r"LIB_\1Rnd_762x54"),
    # 8 mm Lebel: balle D is the ball of balle T and balle P.
    (r"jmssa_(\d)rnd_8x50r_[dp]$", r"JMSSA_\1Rnd_8x50R"),
    # CSA38 numbers its belts and boxes: the even one is the armour-piercing version of the odd one before it.
    (r"csa38_zb53mg2(g?)$", r"CSA38_ZB53mg\1"),
    (r"csa38_zb53mg4(g?)$", r"CSA38_ZB53mg3\1"),
    (r"csa38_zb53mg6(g?)$", r"CSA38_ZB53mg5\1"),
    (r"csa38_zb53mg8$", r"CSA38_ZB53mg7"),
    (r"csa38_ckmwz30mg2$", r"CSA38_CKMwz30mg"),
    (r"csa38_tkvz24mag2$", r"CSA38_TKVZ24mag"),
    (r"csa38_zb26mg2(ge)?$", r"csa38_ZB26MG\1"),
]

# The words fnc_siblingMagazine drops from a class name before it compares.
DROPPED = ("tracer", "tracers", "trc", "t", "ir", "irtracer", "red", "green", "yellow", "white", "orange", "ball")

# Weapons whose magazines of 50 rounds and more are belts.
MG_TOKENS = ("mg34", "mg42", "m1919", "m1917", "maxim", "vickers303", "besa", "zb53", "tkvz", "ckm", "laffete",
             "m2_tripod")

# The calibers a magazine of 100 rounds is a belt of, and those that come in belts from 50.
FULL_POWER = ("762x51", "762x54", "792x57", "762x63")
HEAVY = ("127x99", "127x108", "127x81")


def load(pbo, cache):
    """A PBO's config tables, kept between runs for as long as the PBO does not change."""
    stat = os.stat(pbo)
    key = hashlib.sha1(f"{pbo}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()
    path = os.path.join(cache, key + ".json")

    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    try:
        found = [tree.get("__classes", {}) for _, tree in pbo_config.configs(pbo, TABLES)]
    except (ValueError, IndexError, struct_error) as error:
        print(f"  not read: {os.path.basename(pbo)} ({error})")
        found = []

    found = [classes for classes in found if classes]

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(found, handle)

    return found


struct_error = __import__("struct").error


class Tables:
    """CfgMagazines, CfgAmmo and CfgWeapons of everything read, classes by lowercase name."""

    def __init__(self):
        self.data = {name: {} for name in TABLES[1:]}
        self.spelling = {}
        self.origin = {}  # magazine -> (addon, CfgPatches names, parent as first defined)
        self.declared = {}  # magazine -> every parent it is declared with

    def add(self, classes, addon):
        patches = [name for key, value in classes.items() if key.lower() == "cfgpatches"
                   for name, body in value.get("__classes", {}).items() if not body.get("__extern")]

        for key, value in classes.items():
            table = self.data.get(key.lower())

            if table is None:
                continue

            for name, body in value.get("__classes", {}).items():
                if body.get("__extern"):
                    continue

                low = name.lower()
                self.spelling.setdefault((key.lower(), low), name)
                known = table.setdefault(low, {"__parent": None})

                for prop, content in body.items():
                    if prop == "__classes":
                        known.setdefault("__classes", {}).update(content)
                    elif prop != "__parent" or content:
                        known[prop] = content

                if key.lower() == "cfgmagazines" and addon:
                    self.declared.setdefault(low, set()).add(str(body.get("__parent")).lower())
                    self.origin.setdefault(low, (addon, patches, body.get("__parent")))

    def get(self, table, name, prop, default=None):
        prop = prop.lower()
        low = str(name or "").lower()

        for _ in range(40):
            body = self.data[table].get(low)

            if body is None:
                break

            for key, value in body.items():
                if key.lower() == prop:
                    return value

            low = str(body.get("__parent") or "").lower()

        return default

    def parents(self, table, name):
        out = []
        low = str(name or "").lower()

        for _ in range(40):
            parent = self.data[table].get(low, {}).get("__parent")

            if not parent:
                break

            out.append(parent)
            low = parent.lower()

        return out


def clean(text):
    """As fnc_magazineInfo reads names: lowercase, without dots, commas, hyphens and spaces."""
    return "".join(re.split(r"[.,\- ]", str(text or "").lower()))


def first(table, key):
    for pattern, value in table:
        if re.match(pattern, key):
            return True, value

    return False, None


def locate(name, item, pbo, workshop, game, more):
    """The folder of a mod: its Workshop item, or the copy of it that holds its PBO. A copy in the further folders
    goes first, of those in the Workshop folder and beside the game the one updated last."""
    if item:
        return os.path.join(workshop, item)

    def copies(roots):
        return [found for root in roots for found in glob.glob(os.path.join(root, "*", "addons", pbo))]

    found = sorted(copies(more)) or sorted(copies([workshop, game]), key=os.path.getmtime, reverse=True)

    if len(found) > 1:
        print(f"{name}: {len(found)} copies, the one in {os.path.basename(os.path.dirname(os.path.dirname(found[0])))} is read")

    return os.path.dirname(os.path.dirname(found[0])) if found else ""


def main(workshop, game, more=()):
    cache = os.path.join(tempfile.gettempdir(), "gmr_compat_ww2")
    os.makedirs(cache, exist_ok=True)
    calibers = []
    text = open(CALIBERS, encoding="utf-8").read()

    for match in re.finditer(r'^    class (\w+) \{displayName = "[^"]*"; tokens\[\] = \{([^}]*)\}', text, re.M):
        calibers.append((match.group(1), [t.strip().strip('"') for t in match.group(2).split(",") if t.strip()]))

    known = {caliber for caliber, _ in calibers}

    # The variants each caliber has: a magazine is only "tracer" where there are tracer rounds.
    variants = {}
    current = ""

    for line in text.splitlines():
        match = re.match(r"(    |            )class (\w+) \{displayName", line)

        if match and len(match.group(1)) == 4:
            current = match.group(2)
        elif match:
            variants.setdefault(current, set()).add(match.group(2))
    tables = Tables()

    # The game's own classes first: the mods' ammo inherits its simulation from them.
    for pbo in [os.path.join(game, "Dta", "bin.pbo")] + sorted(glob.glob(os.path.join(game, "Addons", "*.pbo"))):
        if os.path.exists(pbo):
            for classes in load(pbo, cache):
                tables.add(classes, None)

    present = []

    for addon, modname, item, pbo in MODS:
        folder = locate(modname, item, pbo, workshop, game, more)
        files = sorted(glob.glob(os.path.join(folder, "**", "*.pbo"), recursive=True)) if folder else []

        if not files:
            print(f"{addon}: {modname} not found, left as it is")
            continue

        present.append(addon)

        for pbo in files:
            for classes in load(pbo, cache):
                tables.add(classes, addon)

    # Magazines only machine guns take.
    mg_mags, other_mags = set(), set()

    for weapon, body in tables.data["cfgweapons"].items():
        lists = [tables.get("cfgweapons", weapon, "magazines", [])]
        lists += [muzzle.get("magazines", []) for muzzle in body.get("__classes", {}).values() if isinstance(muzzle, dict)]
        target = mg_mags if any(token in weapon for token in MG_TOKENS) else other_mags

        for magazines in lists:
            if isinstance(magazines, list):
                target.update(str(m).lower() for m in magazines)

    mg_mags -= other_mags

    def caliber_of(key, ammo):
        hit, value = first(CALIBER, key)

        if hit:
            return value

        # In the order the game looks: class, ammo, then both without underscores. Not the ammo's parents: mods build
        # on whatever base class is near (the Lahti L-39's 20 mm on the game's .50).
        texts = [clean(key), clean(ammo), clean(key).replace("_", ""), clean(ammo).replace("_", "")]

        for text in texts:
            for caliber, tokens in calibers:
                if any(token in text for token in tokens):
                    return caliber

        return ""

    def belt(key, count, caliber):
        hit, value = first(BELT, key)

        if hit and value is not None:
            return value

        return (
            count >= 130
            or any(part in key for part in ("belt", "_box", "pouch", "_saw"))
            or (count >= 100 and caliber in FULL_POWER)
            or (count >= 50 and caliber in HEAVY)
            or (count >= 50 and key in mg_mags)
        )

    def variant(key, caliber, ammo):
        every = int(float(tables.get("cfgmagazines", key, "tracersEvery", 0) or 0))
        has = variants.get(caliber, ())

        if "tracer" in has and TRACER_NAME.search(key) and (every == 1 or "tracer" in key):
            return "tracer"

        return "ap" if "ap" in has and AP_AMMO.search(ammo.lower()) else "basic"

    def family(key, kind):
        for pattern, name in FAMILY:
            match = re.match(pattern, key)

            if match:
                named = match.expand(name)
                return tables.spelling.get(("cfgmagazines", named.lower()), named)

        if kind != "basic":
            for pattern, to in BALL_NAME:
                ball = re.sub(pattern, to, key, count=1)

                if ball != key and ball in tables.data["cfgmagazines"]:
                    return tables.spelling[("cfgmagazines", ball)]

        return ""

    rows = {addon: [] for addon in present}
    facts = {}  # magazine -> (rounds, scope)
    orphans = []  # bullet magazines of no known caliber
    needs = {addon: set() for addon in present}
    unknown = {addon: [] for addon in present}
    skipped = {addon: [] for addon in present}

    for key in sorted(tables.origin):
        addon, patches, parent = tables.origin[key]
        ammo = str(tables.get("cfgmagazines", key, "ammo", "") or "")
        count = int(float(tables.get("cfgmagazines", key, "count", 0) or 0))
        scope = int(float(tables.get("cfgmagazines", key, "scope", 0) or 0))
        bullet = str(tables.get("cfgammo", ammo, "simulation", "") or "").lower() in ("shotbullet", "shotspread")

        if scope < 1 or count < 1 or not bullet or not parent:
            continue

        name = tables.spelling[("cfgmagazines", key)]

        if len(tables.declared[key]) > 1 or any(re.match(pattern, key) for pattern in SKIPPED):
            skipped[addon].append(name)
            continue

        if any(re.match(pattern, key) for pattern in DISABLED):
            rows[addon].append((name, parent, "", False, "", ""))
        else:
            caliber = caliber_of(key, ammo)

            if caliber not in known:
                unknown[addon].append(f"{name} ({ammo})")
                orphans.append((addon, key, name, parent, count, scope, patches))
                continue

            kind = variant(key, caliber, ammo)
            rows[addon].append((name, parent, caliber, belt(key, count, caliber), kind, family(key, kind)))
            facts[name] = (count, scope)

        needs[addon].update(patches)

    # A class inherits what its parent is given here. The lines of a magazine state its caliber, belt and variant
    # themselves; what only some state (left alone, a family) is taken back where a parent's does not hold for it.
    emitted = {row[0].lower(): row for addon in present for row in rows[addon]}

    def inherited(name):
        """(left alone, family) as the nearest parents with a line here hand them down."""
        off = None
        low = name.lower()

        for _ in range(40):
            low = str(tables.data["cfgmagazines"].get(low, {}).get("__parent") or "").lower()
            row = emitted.get(low)

            if not low:
                break

            if row and off is None:
                off = not row[2]

            if row and row[2]:
                return bool(off), row[5]

        return bool(off), ""

    # A magazine of no known caliber still gets a line where a parent has one: it would take that parent's caliber
    # with it (JMSSA's 12.7 mm Vickers belts are children of the .303 Vickers K pan). "-" stands for no caliber.
    for addon, key, name, parent, count, scope, patches in orphans:
        low = key

        for _ in range(40):
            low = str(tables.data["cfgmagazines"].get(low, {}).get("__parent") or "").lower()

            if not low or low in emitted:
                break

        if low in emitted:
            row = (name, parent, "-", belt(key, count, ""), "basic", "")
            rows[addon].append(row)
            emitted[key] = row
            facts[name] = (count, scope)
            needs[addon].update(patches)

    for addon, modname, _, _ in MODS:
        if addon not in present:
            continue

        mine = rows[addon]
        names = {row[0].lower(): row for row in mine}
        spell = lambda parent: tables.spelling.get(("cfgmagazines", parent.lower()), parent)
        outside = sorted({spell(row[1]) for row in mine if row[1].lower() not in names}, key=str.lower)
        lines = ["// Generated by tools/generate_compat_ww2.py - do not edit by hand."]

        if any(row[2] and not row[5] and inherited(row[0])[1] for row in mine):
            lines.append('// gmr_family = ""; takes back the family the parent class is given, which would pair this magazine wrongly.')

        lines += ["", "class CfgMagazines {"]
        lines += [f"    class {parent};" for parent in outside]
        done = set()

        # Parents before children, as the config needs them.
        def emit(row):
            name, parent, caliber, is_belt, kind, group = row

            if name in done:
                return

            if parent.lower() in names:
                emit(names[parent.lower()])

            done.add(name)
            body = "gmr_disabled = 1;"

            if caliber:
                shown = "" if caliber == "-" else caliber
                body = f'gmr_caliber = "{shown}"; gmr_belt = {int(is_belt)}; gmr_variant = "{kind}";'
                off, handed = inherited(name)
                body += " gmr_disabled = 0;" if off else ""
                body += f' gmr_family = "{group}";' if group or handed else ""

            lines.append(f"    class {name}: {spell(parent)} {{{body}}};")

        for row in mine:
            emit(row)

        lines += ["};", ""]
        out = os.path.join(ROOT, "addons", addon)
        os.makedirs(out, exist_ok=True)
        required = ", ".join(f'"{patch}"' for patch in ["gmr_main"] + sorted(needs[addon], key=str.lower))

        with open(os.path.join(out, "CfgMagazines.hpp"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(lines))

        with open(os.path.join(out, "$PBOPREFIX$"), "w", newline="\n") as handle:
            handle.write(f"z\\gmr\\addons\\{addon}\n")

        with open(os.path.join(out, "script_component.hpp"), "w", newline="\n") as handle:
            handle.write(f"#define COMPONENT {addon}\n#define COMPONENT_BEAUTIFIED GMR - {modname}\n"
                         '#include "\\z\\gmr\\addons\\main\\script_mod.hpp"\n'
                         '#include "\\z\\gmr\\addons\\main\\script_macros.hpp"\n')

        with open(os.path.join(out, "config.cpp"), "w", newline="\n") as handle:
            handle.write(f'''#include "script_component.hpp"

// Calibers and belts of {modname}'s magazines. Loads only when that mod is there.
class CfgPatches {{
    class ADDON {{
        name = COMPONENT_NAME;
        units[] = {{}};
        weapons[] = {{}};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {{{required}}};
        skipWhenMissingDependencies = 1;
        author = "{AUTHOR}";
        VERSION_CONFIG;
    }};
}};

#include "CfgMagazines.hpp"
''')

        belts = sum(1 for row in mine if row[3])
        off = sum(1 for row in mine if not row[2])
        tracers = sum(1 for row in mine if row[4] == "tracer")
        piercing = sum(1 for row in mine if row[4] == "ap")
        plain = sum(1 for row in mine if row[2] == "-")
        print(f"{addon}: {len(mine) - off - plain} magazines, {belts} belts, {tracers} tracer, {piercing} AP, "
              f"{off} left alone, {plain} kept universal")

        if skipped[addon]:
            print(f"  declared with more than one parent, left out: {', '.join(skipped[addon])}")

        if unknown[addon]:
            print(f"  no caliber of this mod (stay universal): {', '.join(unknown[addon])}")

    # The pairs the game will make (fnc_siblingMagazine): the same name without the dropped words, or the same
    # gmr_family, the same size, and listed in the Arsenal (scope 2).
    def pair_key(row):
        return "_".join(word for word in (row[5] or row[0]).lower().split("_") if word and word not in DROPPED)

    everything = [row for addon in present for row in rows[addon] if row[2] and facts[row[0]][1] >= 2]
    ball = {(pair_key(row), facts[row[0]][0]) for row in everything if row[4] == "basic"}
    alone = [row[0] for row in everything if row[4] != "basic" and (pair_key(row), facts[row[0]][0]) not in ball]
    print(f"tracer and AP magazines without a ball version to change into: {', '.join(alone) or 'none'}")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "C:/SteamLibrary/steamapps/workshop/content/107410"
    main(folder, sys.argv[2] if len(sys.argv) > 2 else os.path.normpath(os.path.join(folder, "..", "..", "..", "common", "Arma 3")),
         sys.argv[3:])
