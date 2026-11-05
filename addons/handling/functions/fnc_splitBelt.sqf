#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Splits a loose belt into two of half its length.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Belt class <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_belt_556x45_basic_100"] call gmr_handling_fnc_splitBelt;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_item", "", [""]]];

private _facts = [_item] call EFUNC(main,itemInfo);
private _rounds = _facts select ITEM_ROUNDS;

if (_rounds < 2 || {[_unit, _item, 1] call EFUNC(main,removeItem) != 1}) exitWith {};

private _half = floor (_rounds / 2);

[_unit, _facts select ITEM_BELT_TYPE, _half] call EFUNC(main,giveBelt);
[_unit, _facts select ITEM_BELT_TYPE, _rounds - _half] call EFUNC(main,giveBelt);

if (EGVAR(main,sounds)) then {
    playSound QGVAR(sound_belt_link_1);
};

nil
