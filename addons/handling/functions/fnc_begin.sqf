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

if (EGVAR(main,loadAnimation)) then {
    private _model = if ((GVAR(op) get "kind") == "unloadBelt") then {QPATHTOF(data\mag_box.p3d)} else {[GVAR(op) get "class"] call FUNC(handModel)};

    [FUNC(animTick), ANIM_CHECK_INTERVAL, [_unit, GVAR(op) get "id", _model]] call CBA_fnc_addPerFrameHandler;
};

if (EGVAR(main,sounds)) then {
    private _belt = GVAR(op) get "belt";
    private _interval = [(GVAR(op) get "time") / (GVAR(op) get "need"), 1] select _belt;
    private _sounds = switch (true) do {
        case (_belt): {[QGVAR(sound_belt_link_1), QGVAR(sound_belt_link_2), QGVAR(sound_belt_link_3)]};
        case ((GVAR(op) get "kind") == "fill"): {[QGVAR(sound_round_in_1), QGVAR(sound_round_in_2), QGVAR(sound_round_in_3), QGVAR(sound_round_in_4)]};
        default {[QGVAR(sound_round_out_1), QGVAR(sound_round_out_2), QGVAR(sound_round_out_3)]};
    };

    GVAR(op) set ["tick", [{playSound selectRandom (_this select 0)}, _interval, _sounds] call CBA_fnc_addPerFrameHandler];
};

nil
