#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Joins belts of one type, each result at most 200 rounds long: two chosen ones, or all of them.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Belt type <STRING>
 * 2: First belt, "" for all belts of the type (optional, default: "") <STRING>
 * 3: Second belt (optional, default: "") <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_belt_556x45_basic_", "gmr_belt_556x45_basic_50", "gmr_belt_556x45_basic_30"] call gmr_handling_fnc_combineBelts;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_type", "", [""]], ["_first", "", [""]], ["_second", "", [""]]];

private _rounds = 0;

if (_first isEqualTo "") then {
    {
        if ([_unit, _x select 0, 1] call EFUNC(main,removeItem) == 1) then {
            _rounds = _rounds + (_x select 1);
        };
    } forEach ([_unit, _type] call EFUNC(main,beltItems));
} else {
    {
        if ([_unit, _x, 1] call EFUNC(main,removeItem) == 1) then {
            _rounds = _rounds + (([_x] call EFUNC(main,itemInfo)) select ITEM_ROUNDS);
        };
    } forEach [_first, _second];
};

[_unit, _type, _rounds] call EFUNC(main,giveBelt);

if (EGVAR(main,sounds) && {_rounds > 0}) then {
    playSound "ace_magazinerepack_soundMagazineFinished";
};

nil
