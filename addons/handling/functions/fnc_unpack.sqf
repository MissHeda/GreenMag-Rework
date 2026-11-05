#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens a pack: its rounds go where it was in one go, what has no room there into the other containers, and what has no
 * room at all onto the ground.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Pack class <STRING>
 * 2: Take the pack out of the inventory; the context menu has already done so (optional, default: true) <BOOL>
 * 3: The container it was in, if that is known; else the one it is taken from (optional, default: objNull) <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_pack_556x45_basic_30"] call gmr_handling_fnc_unpack;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_pack", "", [""]], ["_remove", true, [true]], ["_container", objNull, [objNull]]];

// fnc_removeItem takes from the first that holds it, in this order.
if (_remove && {isNull _container}) then {
    _container = [uniformContainer _unit, vestContainer _unit, backpackContainer _unit] param [
        [uniformContainer _unit, vestContainer _unit, backpackContainer _unit] findIf {!isNull _x && {_pack in ((getItemCargo _x) select 0)}},
        objNull
    ];
};

if (_remove && {[_unit, _pack, 1] call EFUNC(main,removeItem) != 1}) exitWith {};

private _facts = [_pack] call EFUNC(main,itemInfo);

PLAY_SOUND(pack_open);

if ([_unit, _facts select ITEM_ROUND, _facts select ITEM_ROUNDS, _container] call EFUNC(main,giveItem) > 0) then {
    hintSilent LLSTRING(Hint_Ground);
};

nil
