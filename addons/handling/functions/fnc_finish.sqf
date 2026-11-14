#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Ends the running operation. The rounds moved are the ones that clicked (fnc_tick), so they can never come out above what
 * was set up, however the frames fell or however often the key was tapped.
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

[_op get "handle"] call CBA_fnc_removePerFrameHandler;
(findDisplay 46) displayRemoveEventHandler ["KeyDown", _op get "keys"];

private _ui = _op get "ui";

{ctrlDelete _x} forEach (_ui getOrDefault ["all", []]);

// The stripper clip minigame's window (its Unload finds no operation any more, so it stops nothing twice).
private _window = (_op getOrDefault ["cg", createHashMap]) getOrDefault ["display", displayNull];

if (!isNull _window) then {
    _window closeDisplay 2;
};

private _started = _op get "started";

if (_started < 0 || {!alive (_op get "unit")}) exitWith {};

// Whatever clicked went in, no more and no less.
private _done = [_op get "played", _op get "need"] select _completed;

if (!_completed) then {
    PLAY_SOUND(cancel);
};

if (_done <= 0) exitWith {};

switch (_op get "kind") do {
    case "fill": {[_op, _done] call FUNC(applyFill)};
    case "unload": {[_op, _done] call FUNC(applyUnload)};
    case "unloadBelt": {[_op, _done] call FUNC(applyBeltItem)};
    case "refillBelt": {[_op, _done] call FUNC(applyBeltRefill)};
};

if (_completed) then {
    switch (true) do {
        case (_op get "belt"): {PLAY_SOUND(belt_done)};
        case ((_op get "kind") == "fill"): {PLAY_SOUND(magazine_done)};
        default {PLAY_SOUND(magazine_empty)};
    };
};

[EVENT_CHANGED, []] call CBA_fnc_localEvent;

nil
