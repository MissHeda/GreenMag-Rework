#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * What letting an item go on a belt item does: a belt of the same type joins it ("combine"), rounds, a box or clips that
 * fit go onto it ("refill", fnc_beltRefillSource), anything else nothing ("").
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: The belt item let go on <STRING>
 * 2: The dragged item <STRING>
 *
 * Return Value:
 * ["combine", "refill" or "", Round class for refill, "loose"/"clips"/"mixed", Reason when it cannot] <ARRAY>
 *
 * Example:
 * [player, "gmr_belt_762x51_basic_100", "gmr_belt_762x51_basic_50"] call gmr_handling_fnc_canDropOnBelt;
 *
 * Public: Yes
 */

params [["_unit", objNull, [objNull]], ["_belt", "", [""]], ["_item", "", [""]]];

private _target = [_belt] call EFUNC(main,itemInfo);
private _dragged = [_item] call EFUNC(main,itemInfo);

if ((_target select ITEM_KIND) != "belt") exitWith {["", "", "mixed", ""]};

if ((_dragged select ITEM_KIND) == "belt") exitWith {
    if ((_dragged select ITEM_BELT_TYPE) != (_target select ITEM_BELT_TYPE)) exitWith {["", "", "mixed", LLSTRING(Hint_WrongAmmo)]};

    // Two of the same length lie in one stack: the stack needs two of them.
    if (_belt == _item && {(([_unit] call EFUNC(main,itemCounts)) getOrDefault [_belt, 0]) < 2}) exitWith {["", "", "mixed", ""]};

    ["combine", "", "mixed", ""]
};

([_unit, _belt, _item] call FUNC(beltRefillSource)) params ["_round", "_from", "_why"];

[["", "refill"] select (_round isNotEqualTo ""), _round, _from, _why]
