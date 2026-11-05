#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Runs every frame of an operation, and is its only clock. Holding starts it and letting go ends it; each round that has
 * moved by the clock clicks once and lights its segment, so sound and picture cannot drift apart. The inventory changes
 * at the end (fnc_finish). Over a magazine the click climbs in pitch as the spring tightens.
 *
 * Arguments:
 * 0: [operation id], the per-frame handler's arguments <ARRAY>
 * 1: The per-frame handler <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [[1], 0] call gmr_handling_fnc_tick;
 *
 * Public: No
 */

params ["_args", "_handle"];
_args params ["_id"];

if (isNil QGVAR(op) || {(GVAR(op) get "id") != _id}) exitWith {
    [_handle] call CBA_fnc_removePerFrameHandler;
};

if !(alive (GVAR(op) get "unit")) exitWith {
    [false] call FUNC(finish);
};

private _now = CBA_missionTime;
private _pressed = inputAction "Action" > 0;
private _wasPressed = GVAR(op) get "pressed";

GVAR(op) set ["pressed", _pressed];
GVAR(op) set ["seen", _now];

// Not begun yet: it waits for the key, and leaves if nobody comes. Nothing has changed yet, so nothing is lost.
if ((GVAR(op) get "started") < 0) exitWith {
    if (_pressed) then {
        call FUNC(begin);
    } else {
        if (_now > (GVAR(op) get "created") + HOLD_TIMEOUT) then {
            [false] call FUNC(finish);
        };
    };
};

if ((GVAR(op) get "hold") && {!_pressed}) exitWith {
    [false] call FUNC(finish);
};

private _step = _now - (GVAR(op) get "last");

GVAR(op) set ["last", _now];

if (GVAR(op) get "game") then {
    if (_pressed && {!_wasPressed}) then {
        call FUNC(gamePress);
    };

    if (_now < (GVAR(op) get "stall")) then {
        _step = 0;
    };
};

private _need = GVAR(op) get "need";
private _time = (GVAR(op) get "time") max 0.01;
private _progress = ((GVAR(op) get "progress") + _step) min _time;

GVAR(op) set ["progress", _progress];

private _done = floor (_need * (_progress / _time) + 0.0001);

if (_done > (GVAR(op) get "played")) then {
    GVAR(op) set ["played", _done];

    private _kind = GVAR(op) get "kind";
    private _capacity = GVAR(op) get "capacity";
    private _shown = 0;
    private _left = _done;

    if (_kind == "unloadBelt") then {
        _shown = _capacity - _done;
    } else {
        private _amounts = GVAR(op) get "amounts";

        {
            private _moves = [_x, _capacity - _x] select (_kind == "fill");

            // On to the next magazine only when this one is through.
            if (_left < _moves || {_forEachIndex == count _amounts - 1}) exitWith {
                _shown = [_x - _left, _x + _left] select (_kind == "fill");
            };

            _left = _left - _moves;
        } forEach _amounts;
    };

    GVAR(op) set ["shown", _shown];

    if (EGVAR(main,sounds)) then {
        private _level = _shown / (_capacity max 1);

        playSound (switch (true) do {
            case (GVAR(op) get "belt"): {format [QGVAR(sound_belt_link_%1), 1 + floor random 4]};
            case (_kind == "fill"): {format [QGVAR(sound_round_in_%1), 1 + (floor (_level * 8) min 7)]};
            default {format [QGVAR(sound_round_out_%1), 1 + (floor (_level * 6) min 5)]};
        });
    };

    call FUNC(uiRound);
};

if (GVAR(op) get "game") then {
    call FUNC(uiGame);
};

if (_progress >= _time) then {
    [true] call FUNC(finish);
};

nil
