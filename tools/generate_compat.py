"""Builds the compat addons (addons/compat_*) from other mods' own magazine configs.

Every magazine of a caliber this mod knows gets gmr_caliber and gmr_belt set, so nothing depends on guessing from
its name. Each mod gets its own addon, skipped when that mod is not loaded.

The configs are read straight from the mods' PBOs in the Steam workshop folder (only config.bin is pulled out, nothing
else is unpacked). Needs hemtt on PATH.
    python tools/generate_compat.py [workshop folder] [cache folder]
Defaults: C:/SteamLibrary/steamapps/workshop/content/107410 and %TEMP%/gmr_compat.
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBERS = os.path.join(ROOT, "addons", "items", "cfg", "calibers.hpp")

# addon name, mod name, PBOs (relative to the workshop folder)
MODS = [
    ("compat_rhsafrf", "RHS: AFRF", ["843425103/addons/rhs_c_weapons.pbo"]),
    ("compat_rhsusaf", "RHS: USAF", ["843577117/addons/rhsusf_c_weapons.pbo"]),
    ("compat_rhsgref", "RHS: GREF", ["843593391/addons/rhsgref_c_weapons.pbo"]),
    ("compat_rhssaf", "RHS: SAF", ["843632231/addons/rhssaf_c_weapons.pbo"]),
    ("compat_3cbbaf", "3CB BAF Weapons", ["893339590/addons/uk3cb_baf_weapons_*.pbo"]),
    ("compat_3cbf", "3CB Factions", ["1673456286/addons/uk3cb_factions_weapons*.pbo"]),
    ("compat_bwmod", "BWMod", ["1200127537/addons/bwa3_*.pbo"]),
]

TOK = re.compile(r'"(?:[^"]|"")*"|[A-Za-z0-9_.\-+]+|[{};:=\[\],]')

# Weapons whose magazines of 50 rounds and more are belts.
MG_TOKENS = ("m240", "m249", "pkm", "pkp", "mg42", "mg3", "mg4", "mg5", "m60", "m84", "fnmag", "mk48", "saw",
             "l7a2", "l110", "rpd", "ukm", "m1919")

# Vanilla ammo base names that are not bullets (grenades, missiles, rockets, shells, flares, smoke).
NOT_BULLET = ("g_", "m_", "r_", "sh_", "f_", "smoke", "rocket", "missile", "grenade")


def configs(pbo, cache):
    """Pulls every config.bin out of a PBO and returns the derapified .cpp paths."""
    out = []
    listing = subprocess.run(["hemtt", "utils", "pbo", "inspect", pbo], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
    for path in re.findall(r"│ (\S*config\.bin) ", listing):
        dst = os.path.join(cache, os.path.basename(pbo)[:-4], path.replace("\\", os.sep))
        cpp = dst[:-4] + ".cpp"
        if not os.path.exists(cpp) or os.path.getmtime(cpp) < os.path.getmtime(pbo):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            subprocess.run(["hemtt", "utils", "pbo", "extract", pbo, path, dst], check=True, capture_output=True)
            subprocess.run(["hemtt", "utils", "config", "derapify", dst, cpp], check=True, capture_output=True)
        out.append(cpp)
    return out


def parse(text):
    toks = TOK.findall(text)
    i = 0

    def block():
        nonlocal i
        d = {}
        while i < len(toks):
            t = toks[i]
            if t == "}":
                i += 1
                if i < len(toks) and toks[i] == ";":
                    i += 1
                return d
            if t == "class":
                name = toks[i + 1]
                i += 2
                parent = None
                if toks[i] == ":":
                    parent = toks[i + 1]
                    i += 2
                if toks[i] == ";":
                    i += 1
                    d.setdefault("__classes", {}).setdefault(name, {"__parent": parent, "__extern": True})
                    continue
                i += 1
                c = block()
                c["__parent"] = parent
                d.setdefault("__classes", {})[name] = c
                continue
            if t == "delete":
                i += 3
                continue
            name = t
            i += 1
            if toks[i] == "[":
                i += 3
                depth = 0
                vals = []
                while True:
                    x = toks[i]
                    i += 1
                    if x == "{":
                        depth += 1
                    elif x == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    elif x != ",":
                        vals.append(x.strip('"'))
                if toks[i] == ";":
                    i += 1
                d[name] = vals
            else:
                i += 1
                vals = []
                while toks[i] != ";":
                    vals.append(toks[i])
                    i += 1
                i += 1
                d[name] = " ".join(v.strip('"') for v in vals)
        return d

    return block()


def main(workshop, cache):
    calibers = []
    text = open(CALIBERS, encoding="utf-8").read()
    for m in re.finditer(r'^    class (\w+) \{displayName = "[^"]*"; tokens\[\] = \{([^}]*)\}', text, re.M):
        calibers.append((m.group(1), [t.strip().strip('"') for t in m.group(2).split(",") if t.strip()]))

    # Tables of all mods together, so one mod's magazines can lean on another's ammo and base classes.
    mags, ammo, weapons = {}, {}, {}
    origin = {}  # magazine -> (addon, CfgPatches classes of the config that defines it)
    present = []
    for addon, modname, pbos in MODS:
        files = sorted(f for p in pbos for f in glob.glob(os.path.join(workshop, p)))
        if not files:
            print(f"{addon}: {modname} not found in {workshop}, left as it is")
            continue
        present.append(addon)
        for pbo in files:
            for cpp in configs(pbo, cache):
                root = parse(open(cpp, encoding="utf-8", errors="replace").read())
                cl = root.get("__classes", {})
                patches = [k for k, v in cl.get("CfgPatches", {}).get("__classes", {}).items() if not v.get("__extern")]
                for src, dst in (("CfgMagazines", mags), ("CfgAmmo", ammo), ("CfgWeapons", weapons)):
                    for k, v in cl.get(src, {}).get("__classes", {}).items():
                        if v.get("__extern") and k in dst:
                            continue
                        dst[k] = v
                        if src == "CfgMagazines" and not v.get("__extern"):
                            origin[k] = (addon, patches)

    def get(table, cls, key, depth=0):
        c = table.get(cls)
        if c is None or depth > 30:
            return None
        if key in c:
            return c[key]
        return get(table, c["__parent"], key, depth + 1) if c.get("__parent") else None

    def is_bullet(a):
        sim = (get(ammo, a, "simulation") or "").lower()
        if sim:
            return sim in ("shotbullet", "shotspread")
        top, n = a, 0
        while top in ammo and ammo[top].get("__parent") and n < 30:
            top = ammo[top]["__parent"]
            n += 1
        # Ammo whose config is in another mod: judge by the name. Only magazines of a known caliber get through anyway.
        return not top.lower().startswith(NOT_BULLET)

    mg_mags = set()
    for w in weapons:
        if any(t in w.lower() for t in MG_TOKENS):
            ms = get(weapons, w, "magazines")
            if isinstance(ms, list):
                mg_mags.update(m.lower() for m in ms)

    clean = lambda t: "".join(re.split(r"[. ]", (t or "").lower()))
    per_mod = {addon: [] for addon in present}
    needs = {addon: set() for addon in present}
    skipped = {addon: [] for addon in present}

    for m in sorted(origin, key=str.lower):
        c = mags[m]
        addon, patches = origin[m]
        if str(get(mags, m, "scope") or "2") != "2":
            continue
        a = get(mags, m, "ammo") or ""
        if not is_bullet(a):
            continue
        caliber = ""
        for t in (clean(m), clean(a)):
            hit = [cid for cid, tokens in calibers if any(k in t for k in tokens)]
            if hit:
                caliber = hit[0]
                break
        if not caliber:
            skipped[addon].append(m)
            continue
        key = m.lower()
        count = int(float(get(mags, m, "count") or 0))
        belt = (
            count >= 130
            or any(k in key for k in ("belt", "_box", "pouch", "_saw"))
            or (count >= 100 and caliber in ("762x51", "762x54", "792x57"))
            or (key in mg_mags and count >= 50)
        )
        per_mod[addon].append((m, c["__parent"], caliber, belt))
        needs[addon].update(patches)

    for addon, modname, _ in MODS:
        if addon not in present:
            continue
        # Mods spell the same base class in different cases; the config wants one spelling throughout.
        spelling = {}
        for m in sorted(mags, key=lambda k: bool(mags[k].get("__extern"))):
            spelling.setdefault(m.lower(), m)
        rows = [(m, spelling.get((p or "").lower(), p), cal, belt) for m, p, cal, belt in per_mod[addon]]
        out = os.path.join(ROOT, "addons", addon)
        os.makedirs(out, exist_ok=True)
        names = {r[0] for r in rows}
        parents = sorted({p for _, p, _, _ in rows if p and p not in names}, key=str.lower)
        lines = ["// Generated by tools/generate_compat.py - do not edit by hand.", "", "class CfgMagazines {"]
        lines += [f"    class {p};" for p in parents]
        done = set()

        # Parents before children, as the config needs them.
        def emit(row):
            m, p, cal, belt = row
            if m in done:
                return
            if p in names:
                emit(next(r for r in rows if r[0] == p))
            done.add(m)
            lines.append(f'    class {m}: {p} {{gmr_caliber = "{cal}"; gmr_belt = {int(belt)};}};')

        for r in rows:
            emit(r)
        lines += ["};", ""]
        required = ", ".join(f'"{p}"' for p in ["gmr_main"] + sorted(needs[addon], key=str.lower))
        open(os.path.join(out, "CfgMagazines.hpp"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        open(os.path.join(out, "$PBOPREFIX$"), "w", newline="\n").write(f"z\\gmr\\addons\\{addon}\n")
        open(os.path.join(out, "script_component.hpp"), "w", newline="\n").write(
            f"#define COMPONENT {addon}\n#define COMPONENT_BEAUTIFIED GMR - {modname}\n"
            '#include "\\z\\gmr\\addons\\main\\script_mod.hpp"\n#include "\\z\\gmr\\addons\\main\\script_macros.hpp"\n')
        open(os.path.join(out, "config.cpp"), "w", newline="\n").write(f'''#include "script_component.hpp"

// Calibers and belts of {modname}'s magazines. Loads only when that mod is there.
class CfgPatches {{
    class ADDON {{
        name = COMPONENT_NAME;
        units[] = {{}};
        weapons[] = {{}};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {{{required}}};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    }};
}};

#include "CfgMagazines.hpp"
''')
        print(f"{addon}: {len(rows)} magazines, {sum(r[3] for r in rows)} belts")
        if skipped[addon]:
            print(f"  no caliber of this mod (stay universal): {', '.join(skipped[addon])}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "C:/SteamLibrary/steamapps/workshop/content/107410",
         sys.argv[2] if len(sys.argv) > 2 else os.path.join(tempfile.gettempdir(), "gmr_compat"))
