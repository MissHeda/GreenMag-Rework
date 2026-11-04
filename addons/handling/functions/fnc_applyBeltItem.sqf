#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes loose rounds out of a belt item; what is left of it stays a belt.
 *
 * Arguments:
 * 0: The operation (fnc_start) <HASHMAP>
 * 1: Rounds to take out <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_op, 18] call gmr_handling_fnc_applyBeltItem;
 *
 * Public: No
 */

params [["_op", createHashMap, [createHashMap]], ["_rounds", 0, [0]]];

private _unit = _op get "unit";
private _class = _op get "class";
private _facts = [_class] call EFUNC(main,itemInfo);

if ([_unit, _class, 1] call EFUNC(main,removeItem) != 1) exitWith {
    hintSilent LLSTRING(Hint_Changed);
};

[_unit, _facts select ITEM_BELT_TYPE, (_facts select ITEM_ROUNDS) - _rounds] call EFUNC(main,giveBelt);

if ([_unit, _facts select ITEM_ROUND, _rounds] call EFUNC(main,giveItem) > 0) then {
    hintSilent LLSTRING(Hint_Ground);
};

nil
