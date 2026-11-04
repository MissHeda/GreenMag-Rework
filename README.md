# GreenMag Rework

Ammunition handling for Arma 3: empty magazines stay in your inventory after a reload, and any magazine
can be refilled from loose rounds, or from belts if it is a machine gun's.

Written from scratch by Miss Heda after the idea of [GreenMag](https://steamcommunity.com/sharedfiles/filedetails/?id=2352603233)
by CoseDola | Miller. It contains no code, textures, texts or class names of that mod, is not affiliated with
it, and does not load together with its compat patches. Requires CBA and ACE3.

## Features

- Refill, unload, unpack and repack through ACE self interaction, packs also through the inventory context menu
- Loose rounds, packs of 10 to 60, and belts of 1 to 200 rounds that can be combined or taken apart
- Simple (caliber only) or advanced (tracer, AP, match ...) ammunition, a server setting
- Magazines of other mods are recognised by their class, ammo and description, no compat patch needed
- Time modifiers per unit in Eden, a speedloader item, and all timings as settings
- A reload guard: a magazine the game loses while reloading is put back and logged in the RPT

## For other mods

A magazine can state what it is in `CfgMagazines`; every entry is optional:

```cpp
class my_30Rnd_Mag: CA_Magazine {
    gmr_caliber = "556x45"; // a class of gmr_calibers
    gmr_variant = "tracer"; // a class of its variants
    gmr_belt = 0;           // 1 refills from belts
    gmr_speedload = 1;      // a speedloader works on it
    gmr_disabled = 0;       // 1 leaves it out completely
};
```

New calibers are classes of `gmr_calibers` at the config root, see `addons/items/cfg/calibers.hpp`. A magazine
can also be declared a belt at runtime, on every machine:
`[["my_100Rnd_Belt"]] call gmr_main_fnc_registerBelts`.

## Development

`tools/generate_items.py` writes the item configs from its table, `tools/make_icons.py` draws the icons.
Both results are committed, so `hemtt build` needs neither.
