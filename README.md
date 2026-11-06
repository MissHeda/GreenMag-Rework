# GreenMag Rework

Ammunition handling for Arma 3: empty magazines stay in your inventory after a reload, and any magazine
can be refilled from loose rounds, or from belts if it is a machine gun's.

Written from scratch by Miss Heda after the idea of [GreenMag](https://steamcommunity.com/sharedfiles/filedetails/?id=2352603233)
by CoseDola | Miller. It contains no code, textures, texts or class names of that mod, is not affiliated with
it, and does not load together with its compat patches. Requires CBA. ACE3 is optional and adds its menu.

## Features

- Drag rounds, a pack or a belt onto a magazine in the inventory to load it
- Refill, unload, unpack, repack and combine through the inventory's context menu (double click), and with ACE also through its self interaction
- Loose rounds, packs of 10 to 60, and belts of 1 to 200 rounds that can be combined or taken apart
- Simple (caliber only) or advanced (tracer, AP, match ...) ammunition, a server setting
- Magazines of other mods are recognised by their class, ammo and description, no compat patch needed
- Time modifiers per unit in Eden, a speedloader item, and all timings as settings
- A reload guard: a magazine the game loses while reloading is put back and logged in the RPT

## Magazines of other mods

Most magazines work by themselves: GreenMag Rework reads the caliber from their class name, ammo and description.
For the rest there are two ways without any code:

- **Universal ammunition** fits every magazine, known or not. With ACE it is in the Ammunition tab of its Arsenal.
- **The server setting "Ammo rules"** names a magazine's caliber: `vn_m16: 556x45, CUP_30Rnd_9x39: 9x39`. Part of the
  class name is enough. The caliber names are listed in `addons/items/cfg/calibers.hpp`.

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
| `gmr_speedload = 0;` | the speedloader does not work on it |
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

## Development

`tools/generate_items.py` writes the item configs from its table, `tools/render_items.py` renders the item
pictures in Blender, `tools/make_icons.py` converts them and draws the menu icons, and `tools/cut_sounds.py`
cuts the loading and unloading sounds out of CC0 recordings from BigSoundBank (see its header). `tools/anim/build_load_gesture.py` computes the loading animation from the Arma 3 Samples'
skeleton, and `tools/anim/preview_rtm.py` shows an RTM on their body in Blender. `tools/make_mag_models.py` writes the magazines shown in the hand,
`tools/make_drop_models.py` the items lying on the ground and their texture. All results are committed,
so `hemtt build` needs none of them.
