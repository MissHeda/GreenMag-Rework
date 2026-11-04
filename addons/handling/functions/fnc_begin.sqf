#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The running operation really starts: its clock runs from here, the weapon goes away and the clicks begin. The
 * clicks are only sound, the rounds moved at the end follow from the time (fnc_finish).
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_begin;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _unit = GVAR(op) get "unit";

GVAR(op) set ["started", CBA_missionTime];

if (EGVAR(main,holster) && {isNull objectParent _unit}) then {
    _unit action ["SwitchWeapon", _unit, _unit, NO_WEAPON_MODE];
};

if (EGVAR(main,sounds)) then {
    private _interval = [(GVAR(op) get "time") / (GVAR(op) get "need"), 1] select (GVAR(op) get "belt");

    GVAR(op) set ["tick", [{playSound "ace_magazinerepack_soundRoundFinished"}, _interval] call CBA_fnc_addPerFrameHandler];
};

nil
