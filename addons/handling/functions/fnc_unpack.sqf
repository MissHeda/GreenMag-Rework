#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens a pack: its rounds go into the inventory in one go, what has no room onto the ground.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Pack class <STRING>
 * 2: Take the pack out of the inventory; the context menu has already done so (optional, default: true) <BOOL>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_pack_556x45_basic_30"] call gmr_handling_fnc_unpack;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_pack", "", [""]], ["_remove", true, [true]]];

if (_remove && {[_unit, _pack, 1] call EFUNC(main,removeItem) != 1}) exitWith {};

private _facts = [_pack] call EFUNC(main,itemInfo);

PLAY_SOUND(pack_open);

if ([_unit, _facts select ITEM_ROUND, _facts select ITEM_ROUNDS] call EFUNC(main,giveItem) > 0) then {
    hintSilent LLSTRING(Hint_Ground);
};

nil
