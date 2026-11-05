#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The running operation really starts: its clock runs from here, the weapon goes away, the counter shows and the clicks
 * begin (fnc_tick). The rounds moved at the end follow from the time (fnc_finish).
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

if (EGVAR(main,roundCounter)) then {
    private _counter = (findDisplay 46) ctrlCreate ["RscStructuredText", -1];

    _counter ctrlSetPosition [safeZoneX + safeZoneW * 0.4, safeZoneY + safeZoneH * 0.60, safeZoneW * 0.2, safeZoneH * 0.05];
    _counter ctrlCommit 0;
    GVAR(op) set ["counter", _counter];
};

GVAR(op) set ["tick", [FUNC(tick), 0, [GVAR(op) get "id"]] call CBA_fnc_addPerFrameHandler];

nil
