#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Gives a unit rounds as belt items, each at most 200 long.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Belt type <STRING>
 * 2: Rounds <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_belt_556x45_basic_", 250] call gmr_main_fnc_giveBelt;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_type", "", [""]], ["_rounds", 0, [0]]];

while {_rounds > 0} do {
    private _length = _rounds min BELT_MAX;

    [_unit, _type + str _length, 1] call FUNC(giveItem);
    _rounds = _rounds - _length;
};

nil
