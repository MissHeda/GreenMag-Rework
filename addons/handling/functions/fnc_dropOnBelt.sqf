#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Loose rounds, a pack, a stripper clip or a carton of clips was dropped on a belt item: what fits (its own rounds, or
 * universal ones while universal ammunition is on) goes onto the belt, the same as "Refill belt" from the context menu.
 * The longer belt comes back into the container the belt lay in. Also called by other inventories (AIO).
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: The belt item dropped on <STRING>
 * 2: The dragged item <STRING>
 * 3: Container the belt lies in (objNull: any) <OBJECT>
 *
 * Return Value:
 * Whether loading starts <BOOL>
 *
 * Example:
 * [player, "gmr_belt_762x51_basic100", "gmr_round_762x51_basic", vestContainer player] call gmr_handling_fnc_dropOnBelt;
 *
 * Public: Yes
 */

params [["_unit", objNull, [objNull]], ["_belt", "", [""]], ["_item", "", [""]], ["_container", objNull, [objNull]]];

([_unit, _belt, _item] call FUNC(beltRefillSource)) params ["_round", "_from", "_why"];

if (_round isEqualTo "") exitWith {
    hintSilent _why;
    PLAY_SOUND(denied);
    false
};

// A pack is opened first, unless packs must be opened by hand.
if ((([_item] call EFUNC(main,itemInfo)) select ITEM_KIND) == "pack") then {
    if (EGVAR(main,packsMustOpen)) exitWith {
        _round = "";
    };

    [_unit, _item, true, _container] call FUNC(unpack);
};

if (_round isEqualTo "") exitWith {
    hintSilent LLSTRING(Hint_OpenPack);
    PLAY_SOUND(denied);
    false
};

EGVAR(main,preferContainer) = _container;

PLAY_SOUND(drop_item);
closeDialog 0;

[
    {
        params ["_unit", "_belt", "_round", "_from"];

        [_unit, "refillBelt", _belt, [], _round, _from] call FUNC(start);
    },
    [_unit, _belt, _round, _from]
] call CBA_fnc_execNextFrame;

true
