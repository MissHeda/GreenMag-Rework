#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The running operation really starts: its clock runs from here (fnc_tick) and the weapon goes away.
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

if (EGVAR(main,loadAnimation)) then {
    private _model = if ((GVAR(op) get "kind") == "unloadBelt") then {QPATHTOF(data\mag_box.p3d)} else {[GVAR(op) get "class"] call FUNC(handModel)};

    [FUNC(animTick), ANIM_CHECK_INTERVAL, [_unit, GVAR(op) get "id", _model]] call CBA_fnc_addPerFrameHandler;
};

PLAY_SOUND(grab);

GVAR(op) set ["last", CBA_missionTime];

call FUNC(uiRound);

nil
