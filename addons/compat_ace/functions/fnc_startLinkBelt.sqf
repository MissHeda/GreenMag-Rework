#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Links loose belts into the machine gun a unit is firing, behind a progress bar. The belts leave the inventory only at
 * the end, and only as many rounds as the gun is missing; the rest of a belt stays a shorter belt.
 *
 * Arguments:
 * 0: Unit linking <OBJECT>
 * 1: Unit with the weapon, may be the same <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, cursorObject] call gmr_compat_ace_fnc_startLinkBelt;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_target", objNull, [objNull]]];

if (([_unit, _target] call FUNC(linkBeltSource)) isEqualTo []) exitWith {};

[_unit, "PutDown"] call ace_common_fnc_doGesture;

[
    LINK_BELT_TIME,
    [_unit, _target, currentMagazine _target],
    {
        (_this select 0) params ["_unit", "_target", "_magazine"];

        private _source = [_unit, _target] call FUNC(linkBeltSource);

        if (_source isEqualTo [] || {currentMagazine _target != _magazine}) exitWith {
            [LLSTRING(BeltNotLinked)] call ace_common_fnc_displayTextStructured;
        };

        _source params ["_type", "", "_missing"];

        private _rounds = [_unit, _type, _missing] call EFUNC(main,takeBelts);

        if (_rounds > 0) then {
            [QGVAR(beltLinked), [_target, _unit, _magazine, _type, _rounds], _target] call CBA_fnc_targetEvent;
        };
    },
    {
        [LLSTRING(BeltNotLinked)] call ace_common_fnc_displayTextStructured;
    },
    LLSTRING(LinkingBelt),
    {
        (_this select 0) params ["_unit", "_target", "_magazine"];

        ([_unit, _target, ["isNotInside"]] call ace_common_fnc_canInteractWith)
        && {_unit distance _target < 3}
        && {speed _target < 1}
        && {currentMagazine _target == _magazine}
    },
    ["isNotInside"]
] call ace_common_fnc_progressBar;

nil
