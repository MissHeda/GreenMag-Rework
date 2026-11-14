#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts loose rounds of a belt item's own kind onto it, loose rounds first and then off stripper clips (fnc_takeRounds),
 * as far as they are still there. The belt item becomes the longer one; nothing is joined with another belt.
 *
 * Arguments:
 * 0: The operation (fnc_start) <HASHMAP>
 * 1: Rounds to put on <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_op, 18] call gmr_handling_fnc_applyBeltRefill;
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

private _taken = [_unit, _op get "source", _rounds, _op getOrDefault ["from", "mixed"]] call FUNC(takeRounds);

[_unit, _facts select ITEM_BELT_TYPE, (_facts select ITEM_ROUNDS) + _taken] call EFUNC(main,giveBelt);

if (_taken < _rounds) then {
    hintSilent LLSTRING(Hint_Changed);
};

nil
