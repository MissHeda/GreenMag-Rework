# GreenMag Rework

Ammunition handling for Arma 3: empty magazines stay in your inventory after a reload, and any magazine
can be refilled from loose rounds, or from belts if it is a machine gun's.

Written from scratch by Miss Heda after the idea of [GreenMag](https://steamcommunity.com/sharedfiles/filedetails/?id=2352603233)
by CoseDola | Miller. It contains no code, textures, texts or class names of that mod, is not affiliated with
it, and does not load together with its compat patches. Requires CBA. ACE3 is optional and adds its menu.

## Features

- Drag rounds, a pack, a stripper clip or a belt onto a magazine in the inventory to load it: what you drag is what
  goes in
- Refill, unload, unpack, repack and combine through the inventory's context menu (double click), and with ACE also through its self interaction
- Loose rounds, packs of 10, 30 and 60, and belts of 1 to 200 rounds that can be combined or taken apart
- Simple (caliber only) or advanced (tracer, AP, match ...) ammunition, a server setting
- Magazines of other mods are recognised by their class, ammo and description, no compat patch needed
- Stripper clips for the rifle calibers issued on them, in cartons as they are issued: strip them into loose rounds,
  or seat a clip in the speedloader's guide and press the rounds down, with its own minigame
- Time modifiers per unit in Eden and all timings as settings
- A reload guard: a magazine the game loses while reloading is put back and logged in the RPT

## Magazines of other mods

Most magazines work by themselves: GreenMag Rework reads the caliber from their class name, ammo and description.
For the rest there are two ways without any code:

- **Universal ammunition** fits every magazine, known or not. With ACE it is in the Ammunition tab of its Arsenal.
- **The server setting "Ammo rules"** names a magazine's caliber: `vn_m16: 556x45, CUP_30Rnd_9x39: 9x39`. Part of the
  class name is enough. The caliber names are listed in `addons/items/cfg/calibers.hpp`.
- **The magazine scan** writes that line for you: set a key for "Scan magazines of other mods" in the CBA controls
  (GreenMag Rework), or run `call gmr_main_fnc_scanMagazines` in the debug console. It lists every magazine with no
  caliber, suggests one where possible and, in singleplayer or as host, copies the line to the clipboard. Fill in the
  ones marked `?` and paste it into the server setting.
- **The server setting "Excluded magazines"** makes GreenMag leave a magazine alone, for magazines that hold no rounds
  to take out (flamethrower tanks, batteries): `flame, _battery`. Part of the class name is enough, but every class
  containing it is excluded, so use enough of the name. It is `flame` by default, which covers the flamethrower tanks
  of the mods seen so far; keep it in the list when you add your own. Mods can do the same with `gmr_disabled = 1;` (below).

## For modders: add your magazines and ammo

**1. Your magazine takes an existing caliber.** One line in its class, nothing else to load or require: without
GreenMag the line is simply ignored.

```cpp
class CfgMagazines {
    class CA_Magazine;
    class my_30Rnd_Mag: CA_Magazine {
        gmr_caliber = "556x45";   // which rounds fit, see calibers.hpp
    };
};
```

Optional lines, only if you need them:

| line | does |
| --- | --- |
| `gmr_belt = 1;` | refills from belts instead of loose rounds |
| `gmr_variant = "tracer";` | the kind of round inside (advanced ammunition) |
| `gmr_family = "my_30Rnd_Mag";` | the magazine it is a version of, where the class names do not tell |
| `gmr_speedload = 0;` | no stripper clips with the speedloader (single rounds only) |
| `gmr_disabled = 1;` | GreenMag leaves this magazine alone |

**2. Your own kind of ammunition** (a new caliber): name it once, then give it a round and, if you like, a box. This
part needs `"gmr_items"` in your `requiredAddons`, so it belongs in an optional compat PBO.

```cpp
class gmr_calibers {
    class plasma {
        displayName = "Plasma Cell";
        tokens[] = {"plasma"};          // magazines with this in their class name use it
        packs[] = {20};                 // box sizes
        class variants {
            class basic {displayName = "Basic"; tokens[] = {};};
        };
    };
};

class CfgWeapons {
    class gmr_round_base;
    class gmr_pack_base;

    // The names must be exactly gmr_round_<caliber>_basic and gmr_pack_<caliber>_basic_<size>.
    class gmr_round_plasma_basic: gmr_round_base {
        scope = 2;
        displayName = "Plasma Cell";
        picture = "\my_mod\data\plasma_cell.paa";
        gmr_caliber = "plasma";
        gmr_variant = "basic";
        gmr_round = "gmr_round_plasma_basic";
    };
    class gmr_pack_plasma_basic_20: gmr_pack_base {
        displayName = "Plasma Cells (20)";
        picture = "\my_mod\data\plasma_box.paa";
        gmr_rounds = 20;
        gmr_caliber = "plasma";
        gmr_variant = "basic";
        gmr_round = "gmr_round_plasma_basic";
    };
};
```

That is all: your magazines with "plasma" in their name now load from Plasma Cells, round by round.

**3. Your own items in GreenMag's Arsenal tab** (ammo cans, bandoliers, anything your mod turns into rounds or clips).
One line in the item's class, nothing to require: without GreenMag or ACE it is simply ignored.

```cpp
class CfgWeapons {
    class CBA_MiscItem;
    class my_bandolier_556: CBA_MiscItem {
        scope = 2;
        gmr_arsenal = 1;   // listed in the Ammunition tab of ACE Arsenal instead of Misc
    };
};
```

It works for `CfgWeapons` and `CfgMagazines` classes with `scope = 2`, as long as ACE Arsenal counts them as misc
items (inventory items, not magazines a weapon loads). They always show, whatever view the tab is set to.

All lines at a glance:

| line | in | does |
| --- | --- | --- |
| `gmr_caliber = "556x45";` | magazine | which rounds fit (names in `addons/items/cfg/calibers.hpp`) |
| `gmr_belt = 1;` | magazine | refills from belts instead of loose rounds |
| `gmr_variant = "tracer";` | magazine | the kind of round inside (advanced ammunition) |
| `gmr_family = "my_30Rnd_Mag";` | magazine | pairs it with its ball or tracer version when the names differ by more than a word |
| `gmr_speedload = 0;` | magazine | no stripper clips with the speedloader |
| `gmr_disabled = 1;` | magazine | GreenMag leaves it alone |
| `gmr_arsenal = 1;` | item | shows it in GreenMag's Arsenal tab |

Built in already, each loading only with its mod: RHS (AFRF, USAF, GREF, SAF), 3CB Factions and BAF Weapons, BWMod,
CUP Weapons, NIArms, MCC and ACE Crew-Served Weapons, and for the Second World War IFA3 AIO, Faces of War, Northern
Fronts, CSA38, IFA3 Liberation and JM's Second Assault. Missing your mod? Ask on the Workshop page or open an issue.

The Second World War mods bring their own rounds: .30-06, .30 Carbine, 7.92 Kurz, .303 (also as 7.7x56 R), 7.7 and 6.5
Arisaka, 6.5 Swedish, the Carcano, Lebel, Mannlicher, MAS and Breda rifle rounds, the pistol rounds from 6.35 Browning
to .455 Webley, the anti-tank rifles' (.55 Boys, 7.92x94, 7.92x107, 14.5x114, 20x138 B) and the 12.7x81 of the heavy
Vickers.
The belts of the MG 34 and 42, the M1919, the Vickers and the Maxim refill from belts; pans, drums and feed strips (DP, Bren, Lewis, Hotchkiss, Breda) take
loose rounds. Flamethrower fuel, blades, the placeholder magazines of scripted reloads and the shell boxes a gun crew
carries are left alone.

With the advanced ammunition, the rounds those mods have tracer magazines of come as tracer too (7.92x57, .30-06,
.303, 7.62x25, .30 Carbine, 7.92 Kurz, 7.5 MAS, 8 mm Lebel, 8x59 Breda, 6.5x55), 7.92x57, .30-06 and .303 also as
tracer belts: tracer rounds in an empty ball clip make it the tracer clip and the other way round. The same goes for
armour-piercing rounds, which there are for 7.92x57 (S.m.K.), .303, 7.62x25 (P-41), 7.62x54 R (B-30), 8 mm Lebel
(balle P) and 8x59 Breda, 7.92x57 and .303 also as belts. Heavy ball (sS, D, Mk VIII, M1) takes ball.

## Development

`tools/generate_compat.py` and `tools/generate_compat_ww2.py` write the compat addons from the other mods' own configs;
the latter reads them with `tools/pbo_config.py`, without HEMTT, and has tables for what a name does not tell.
`tools/generate_items.py` writes the item configs from its table, `tools/render_items.py` renders the item
pictures in Blender, `tools/make_icons.py` converts them and draws the menu icons, and `tools/cut_sounds.py`
cuts the loading and unloading sounds out of CC0 recordings from BigSoundBank (see its header). `tools/anim/build_load_gesture.py` computes the loading animation from the Arma 3 Samples'
skeleton, and `tools/anim/preview_rtm.py` shows an RTM on their body in Blender. `tools/make_mag_models.py` writes the magazines shown in the hand,
`tools/make_drop_models.py` the items lying on the ground; the packs' cartons take their texture from
`tools/render_pack_textures.py`, which renders the sides of the inventory picture's carton. All results are committed,
so `hemtt build` needs none of them.
