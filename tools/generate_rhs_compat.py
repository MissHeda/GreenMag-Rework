"""Builds the RHS compat addons (addons/compat_rhs*) from RHS's own magazine configs.

Every RHS magazine of a caliber this mod knows gets gmr_caliber and gmr_belt set, so nothing depends on guessing from
its name. Each RHS mod gets its own addon, skipped when that mod is not loaded.

Usage: unpack and derapify the RHS weapon configs first, then point this at the folder holding them:
    hemtt utils pbo unpack <workshop>/843577117/addons/rhsusf_c_weapons.pbo rhsusf_c_weapons
    hemtt utils config derapify rhsusf_c_weapons/config.bin rhsusf_c_weapons.cpp
    (same for rhs_c_weapons, rhsgref_c_weapons, rhssaf_c_weapons)
    python tools/generate_rhs_compat.py <folder with the four .cpp files>
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALIBERS = os.path.join(ROOT, "addons", "items", "cfg", "calibers.hpp")

# RHS weapon config -> addon name, mod name
MODS = {
    "rhs_c_weapons": ("compat_rhsafrf", "RHS: AFRF"),
    "rhsusf_c_weapons": ("compat_rhsusaf", "RHS: USAF"),
    "rhsgref_c_weapons": ("compat_rhsgref", "RHS: GREF"),
    "rhssaf_c_weapons": ("compat_rhssaf", "RHS: SAF"),
}

TOK = re.compile(r'"(?:[^"]|"")*"|[A-Za-z0-9_.\-+]+|[{};:=\[\],]')

# Weapons whose magazines of 50 rounds and more are belts.
MG_TOKENS = ("m240", "m249", "pkm", "pkp", "mg42", "mg3", "m60", "m84", "fnmag", "mk48", "saw")


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


def main(folder):
    calibers = []
    text = open(CALIBERS, encoding="utf-8").read()
    for m in re.finditer(r'^    class (\w+) \{displayName = "[^"]*"; tokens\[\] = \{([^}]*)\}', text, re.M):
        calibers.append((m.group(1), [t.strip().strip('"') for t in m.group(2).split(",") if t.strip()]))

    mags, ammo, weapons, origin = {}, {}, {}, {}
    for stem in MODS:
        root = parse(open(os.path.join(folder, stem + ".cpp"), encoding="utf-8", errors="replace").read())
        cl = root.get("__classes", {})
        for src, dst in (("CfgMagazines", mags), ("CfgAmmo", ammo), ("CfgWeapons", weapons)):
            for k, v in cl.get(src, {}).get("__classes", {}).items():
                if v.get("__extern") and k in dst:
                    continue
                dst[k] = v
                if src == "CfgMagazines" and not v.get("__extern"):
                    origin[k] = stem

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
        return top.startswith("B_") or top == "BulletBase"

    mg_mags = set()
    for w in weapons:
        if any(t in w.lower() for t in MG_TOKENS):
            ms = get(weapons, w, "magazines")
            if isinstance(ms, list):
                mg_mags.update(m.lower() for m in ms)

    clean = lambda t: "".join(re.split(r"[. ]", (t or "").lower()))
    per_mod = {stem: [] for stem in MODS}
    skipped = []

    for m in sorted(origin, key=str.lower):
        c = mags[m]
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
            skipped.append(m)
            continue
        key = m.lower()
        count = int(float(get(mags, m, "count") or 0))
        belt = (
            count >= 130
            or any(k in key for k in ("belt", "_box", "pouch", "_saw"))
            or (count >= 100 and caliber in ("762x51", "762x54", "792x57"))
            or (key in mg_mags and count >= 50)
        )
        per_mod[origin[m]].append((m, c["__parent"], caliber, belt))

    for stem, (addon, modname) in MODS.items():
        rows = per_mod[stem]
        out = os.path.join(ROOT, "addons", addon)
        os.makedirs(out, exist_ok=True)
        parents = sorted({p for _, p, _, _ in rows if p and p not in {r[0] for r in rows}}, key=str.lower)
        names = {r[0] for r in rows}
        lines = ["// Generated by tools/generate_rhs_compat.py - do not edit by hand.", "", "class CfgMagazines {"]
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
        requiredAddons[] = {{"gmr_main", "{stem}"}};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    }};
}};

#include "CfgMagazines.hpp"
''')
        print(f"{addon}: {len(rows)} magazines, {sum(r[3] for r in rows)} belts")

    print("No caliber of this mod (stay universal):", ", ".join(skipped))


if __name__ == "__main__":
    main(sys.argv[1])
