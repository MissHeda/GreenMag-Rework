#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The inventory's context menu, a double click on an item: everything the ACE menu can do, for playing without ACE. Each
 * entry shows only where it can do something.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_addContextMenus;
 *
 * Public: No
 */

private _fnc_magazineCan = {
    params ["", "_container", "_item"];

    private _facts = [_item] call EFUNC(main,magazineInfo);

    EGVAR(main,enabled) && {_facts select MAG_OK} && {
        private _capacity = _facts select MAG_CAPACITY;

        (magazinesAmmoCargo _container) findIf {
            (_x select 0) == _item && {[(_x select 1) > 0, (_x select 1) < _capacity] select (_this select 5 == "fill")}
        } >= 0
    }
};

{
    _x params ["_label", "_kind", "_icon"];

    [
        "#Magazine",
        "CONTAINER",
        _label,
        nil,
        _icon,
        [{true}, {(_this + [_this select 4 select 0]) call (_this select 4 select 1)}],
        {
            params ["_unit", "_container", "_item", "", "_params"];

            [_unit, _container, _item, _params select 0] call FUNC(contextMagazine);
            false
        },
        false,
        [_kind, _fnc_magazineCan]
    ] call CBA_fnc_addItemContextMenuOption;
} forEach [
    [LLSTRING(Refill), "fill", QPATHTOF(data\action_fill.paa)],
    [LLSTRING(Unload), "unload", QPATHTOF(data\action_unload.paa)]
];

// Packs open, CBA takes the item away itself.
[
    "gmr_pack_base",
    "CONTAINER",
    LLSTRING(Unpack),
    nil,
    QPATHTOF(data\action_unpack.paa),
    {EGVAR(main,enabled)},
    {
        params ["_unit", "_container", "_item"];

        [_unit, _item, false, _container] call FUNC(unpack);
    },
    true,
    []
] call CBA_fnc_addItemContextMenuOption;

// Stripper clips are stripped into loose rounds the same way.
[
    "gmr_clip_base",
    "CONTAINER",
    LLSTRING(StripClip),
    nil,
    QPATHTOF(data\action_unpack.paa),
    {EGVAR(main,enabled)},
    {
        params ["_unit", "_container", "_item"];

        [_unit, _item, false, _container] call FUNC(unpack);
    },
    true,
    []
] call CBA_fnc_addItemContextMenuOption;

// Loose rounds go into packs.
[
    "gmr_round_base",
    "CONTAINER",
    LLSTRING(Pack),
    nil,
    QPATHTOF(data\action_pack.paa),
    [
        {true},
        {
            params ["_unit", "", "_item"];

            EGVAR(main,enabled) && {EGVAR(main,allowPacking)} && {(([_unit] call EFUNC(main,itemCounts)) getOrDefault [_item, 0]) >= 10}
        }
    ],
    {
        params ["_unit", "", "_item"];

        [_unit, _item] call FUNC(packRounds);
        false
    },
    false,
    []
] call CBA_fnc_addItemContextMenuOption;

// Belts come apart into rounds, split in two, or are joined with the others of their type.
[
    "gmr_belt_base",
    "CONTAINER",
    LLSTRING(SplitBelt),
    nil,
    QPATHTOF(data\action_split.paa),
    [
        {true},
        {
            params ["", "", "_item"];

            EGVAR(main,enabled) && {(([_item] call EFUNC(main,itemInfo)) select ITEM_ROUNDS) >= 2}
        }
    ],
    {
        params ["_unit", "", "_item"];

        [_unit, _item] call FUNC(splitBelt);
        false
    },
    false,
    []
] call CBA_fnc_addItemContextMenuOption;

[
    "gmr_belt_base",
    "CONTAINER",
    LLSTRING(Unload),
    nil,
    QPATHTOF(data\action_unload.paa),
    {EGVAR(main,enabled)},
    {
        params ["_unit", "", "_item"];

        closeDialog 0;
        [{_this call FUNC(start)}, [_unit, "unloadBelt", _item, []]] call CBA_fnc_execNextFrame;
        false
    },
    false,
    []
] call CBA_fnc_addItemContextMenuOption;

// Loose rounds of its own kind, and those on its stripper clips, go back onto a belt that is not full.
[
    "gmr_belt_base",
    "CONTAINER",
    LLSTRING(RefillBelt),
    nil,
    QPATHTOF(data\action_fill.paa),
    [
        {true},
        {
            params ["_unit", "", "_item"];

            private _facts = [_item] call EFUNC(main,itemInfo);

            EGVAR(main,enabled)
                && {(_facts select ITEM_ROUNDS) < BELT_MAX}
                && {
                    private _round = _facts select ITEM_ROUND;

                    (([_unit] call EFUNC(main,itemCounts)) getOrDefault [_round, 0]) > 0
                        || {[_unit, _round] call FUNC(clipsOf) isNotEqualTo []}
                }
        }
    ],
    {
        params ["_unit", "", "_item"];

        closeDialog 0;
        [{_this call FUNC(start)}, [_unit, "refillBelt", _item, []]] call CBA_fnc_execNextFrame;
        false
    },
    false,
    []
] call CBA_fnc_addItemContextMenuOption;

[
    "gmr_belt_base",
    "CONTAINER",
    LLSTRING(CombineAll),
    nil,
    QPATHTOF(data\action_belt.paa),
    [
        {true},
        {
            params ["_unit", "", "_item"];

            EGVAR(main,enabled) && {count ([_unit, ([_item] call EFUNC(main,itemInfo)) select ITEM_BELT_TYPE] call EFUNC(main,beltItems)) >= 2}
        }
    ],
    {
        params ["_unit", "", "_item"];

        [_unit, ([_item] call EFUNC(main,itemInfo)) select ITEM_BELT_TYPE] call FUNC(combineBelts);
        false
    },
    false,
    []
] call CBA_fnc_addItemContextMenuOption;

nil
