#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Ends the running operation. The rounds moved follow from the time that passed, so they can never come out above
 * what was set up, however the frames fell or however often the action was tapped.
 *
 * Arguments:
 * 0: It ran to the end <BOOL>
 *
 * Return Value:
 * None
 *
 * Example:
 * [true] call gmr_handling_fnc_finish;
 *
 * Public: No
 */

params [["_completed", false, [false]]];

if (isNil QGVAR(op)) exitWith {};

private _op = GVAR(op);

GVAR(op) = nil;

if ((_op get "tick") >= 0) then {
    [_op get "tick"] call CBA_fnc_removePerFrameHandler;
};

if ((_op get "cancel") >= 0) then {
    (_op get "unit") removeAction (_op get "cancel");
};

// A completed hold action has removed itself.
if (!_completed && {(_op get "hold") >= 0}) then {
    [_op get "unit", _op get "hold"] call BIS_fnc_holdActionRemove;
};

private _started = _op get "started";

if (_started < 0 || {!alive (_op get "unit")}) exitWith {};

private _need = _op get "need";
private _done = if (_completed) then {
    _need
} else {
    floor (_need * (((CBA_missionTime - _started) / ((_op get "time") max 0.01)) min 1))
};

if (_done <= 0) exitWith {};

switch (_op get "kind") do {
    case "fill": {[_op, _done] call FUNC(applyFill)};
    case "unload": {[_op, _done] call FUNC(applyUnload)};
    case "unloadBelt": {[_op, _done] call FUNC(applyBeltItem)};
};

if (EGVAR(main,sounds)) then {
    playSound QGVAR(sound_magazine_done);
};

[EVENT_CHANGED, []] call CBA_fnc_localEvent;

nil
