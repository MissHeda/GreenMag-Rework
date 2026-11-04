#include "script_component.hpp"

if (!hasInterface) exitWith {};

// Unpack from the inventory's context menu; CBA takes the item away itself.
[
    "gmr_pack_base",
    "CONTAINER",
    LLSTRING(Unpack),
    nil,
    QPATHTOF(data\action_unpack.paa),
    {EGVAR(main,enabled)},
    {
        params ["_unit", "", "_item"];

        [_unit, _item, false] call FUNC(unpack);
    },
    true,
    []
] call CBA_fnc_addItemContextMenuOption;
