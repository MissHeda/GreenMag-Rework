#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes rounds off a unit's belts: the shortest belt that covers what is wanted, else the longest and on from there.
 * What is left of the last belt comes back as a shorter one.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Belt type <STRING>
 * 2: Rounds wanted <NUMBER>
 *
 * Return Value:
 * Rounds taken <NUMBER>
 *
 * Example:
 * [player, "gmr_belt_556x45_basic_", 100] call gmr_main_fnc_takeBelts;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_type", "", [""]], ["_wanted", 0, [0]]];

private _belts = [_unit, _type] call FUNC(beltItems);
private _taken = 0;

while {_taken < _wanted && {_belts isNotEqualTo []}} do {
    private _need = _wanted - _taken;
    private _covering = _belts select {(_x select 1) >= _need};
    private _belt = if (_covering isEqualTo []) then {_belts select 0} else {_covering select (count _covering - 1)};

    _belts deleteAt (_belts find _belt);

    if ([_unit, _belt select 0, 1] call FUNC(removeItem) == 1) then {
        _taken = _taken + (_belt select 1);
    };
};

if (_taken > _wanted) then {
    [_unit, _type, _taken - _wanted] call FUNC(giveBelt);
    _taken = _wanted;
};

_taken
