#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Runs while an operation runs and looks after the loading gesture: it plays once the weapon is away, with a magazine
 * in the left hand, and it ends with the operation, whichever way that ends. So nothing is left behind if the unit dies
 * or something else cuts the operation off. The gesture needs free hands and fits neither lying down nor a seat. Other
 * animations can push it out, a weapon being put away for one, so it is asked for again until it is what plays.
 *
 * Arguments:
 * 0: [unit, operation id, magazine model], the per-frame handler's arguments <ARRAY>
 * 1: The per-frame handler <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [[player, 1, "\z\gmr\addons\handling\data\mag_rifle.p3d"], 0] call gmr_handling_fnc_animTick;
 *
 * Public: No
 */

params ["_args", "_handle"];
_args params ["_unit", "_id", "_model"];

private _running = !isNil QGVAR(op) && {(GVAR(op) get "id") == _id} && {alive _unit};
private _fits = _running
    && {isNull objectParent _unit}
    && {stance _unit in ["STAND", "CROUCH"]}
    && {currentWeapon _unit isEqualTo ""};

if (_fits) then {
    private _gesture = gestureState _unit;

    if (_gesture != QGVAR(load)) then {
        _unit playActionNow QGVAR(load);

        INFO_1("Loading gesture asked for, playing now: %1",_gesture);
    };

    if (!GVAR(animPlaying)) then {
        GVAR(animPlaying) = true;
        [QGVAR(magazineShown), [_unit, _model]] call CBA_fnc_globalEvent;
    };
};

if (!_fits && {GVAR(animPlaying)}) then {
    GVAR(animPlaying) = false;
    [QGVAR(magazineHidden), [_unit]] call CBA_fnc_globalEvent;
    _unit playActionNow QGVAR(stop);
};

if (!_running) then {
    [_handle] call CBA_fnc_removePerFrameHandler;
};

nil
