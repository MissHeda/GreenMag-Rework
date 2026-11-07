#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The stripper clip minigame, every frame (fnc_tick), as it is done by hand. First the clip has to go into the guide on
 * the magazine: it sweeps over the track and the key seats it while it is over the opening, a miss fumbles for a moment.
 * Then the thumb presses the rounds down: holding the key builds pressure, faster the fuller the magazine as its spring
 * pushes back, and letting go eases it. The rounds slide in while the pressure is in the green; past the red the clip
 * jams, the run is over and the thumb has to start again. An empty clip flies off and the next one comes.
 * Without the server's "must hit" a clip seats itself after a few passes and the rounds go down slowly unpressed.
 *
 * Arguments:
 * 0: Seconds since the last frame <NUMBER>
 * 1: The key is held <BOOL>
 * 2: It was held the frame before <BOOL>
 *
 * Return Value:
 * None
 *
 * Example:
 * [0.016, true, false] call gmr_handling_fnc_clipGameTick;
 *
 * Public: No
 */

params [["_step", 0, [0]], ["_pressed", false, [false]], ["_wasPressed", false, [false]]];

if (isNil QGVAR(op)) exitWith {};

private _op = GVAR(op);
private _now = CBA_missionTime;
private _steps = _op get "steps";
private _index = _op get "stepIndex";
private _mustHit = _op get "mustHit";

if (_index >= count _steps) exitWith {};

// A miss or a jam holds the hand; the thumb eases off meanwhile.
if (_now < (_op get "stall")) exitWith {
    _op set ["pressure", ((_op get "pressure") - _step * CLIP_PRESSURE_FALL) max 0];
};

private _fnc_seat = {
    _op set ["stage", "push"];
    _op set ["pressure", 0];
    _op set ["passes", 0];
    PLAY_SOUND(grab);
};

if ((_op get "stage") == "insert") exitWith {
    if (_pressed && {!_wasPressed} && {!(_op get "tried")}) then {
        _op set ["tried", true];

        private _phase = _op get "phase";
        private _from = _op get "zone";

        if (_phase >= _from && {_phase <= _from + (_op get "zoneSize")}) then {
            private _hit = (_op get "ui") getOrDefault ["hit", controlNull];

            _hit ctrlSetFade 0;
            _hit ctrlCommit 0;
            _hit ctrlSetFade 1;
            _hit ctrlCommit UI_HIT_TIME;

            call _fnc_seat;
        } else {
            _op set ["stall", _now + GAME_MISS_STALL];
            _op set ["combo", 0];
            PLAY_SOUND(denied);
        };
    };

    if ((_op get "stage") == "insert") then {
        private _phase = (_op get "phase") + _step / CLIP_SWEEP_TIME;

        if (_phase >= 1) then {
            _phase = 0;
            _op set ["tried", false];
            _op set ["passes", (_op get "passes") + 1];

            if (!_mustHit && {(_op get "passes") >= CLIP_AUTO_PASSES}) then {
                call _fnc_seat;
            };
        };

        _op set ["phase", _phase];
    };
};

// Pressing the rounds down.
private _pressure = _op get "pressure";
private _fill = (_op get "shown") / ((_op get "capacity") max 1);

if (_pressed) then {
    _pressure = _pressure + _step * (CLIP_PRESSURE_RISE + CLIP_PRESSURE_SPRING * _fill);
} else {
    _pressure = (_pressure - _step * CLIP_PRESSURE_FALL) max 0;
};

if (_pressure >= CLIP_PRESSURE_RED) exitWith {
    _op set ["pressure", 0];
    _op set ["stall", _now + CLIP_JAM_STALL];
    _op set ["combo", 0];
    PLAY_SOUND(denied);
};

_op set ["pressure", _pressure];

private _rate = switch (true) do {
    case (_pressure >= CLIP_PRESSURE_GREEN): {1};
    case (!_pressed && {!_mustHit}): {CLIP_AUTO_RATE};
    default {0};
};

if (_rate <= 0) exitWith {};

private _rounds = _steps select _index;
private _move = (_step * _rate / ((_op get "beat") max 0.01)) min (_rounds - (_op get "stepDone"));

_op set ["stepDone", (_op get "stepDone") + _move];
_op set ["pushed", (_op get "pushed") + _move];

// The clip is empty: it flies off, the run grows, the next clip has to go in.
if ((_op get "stepDone") >= _rounds - 0.0001) then {
    _op set ["pushed", (_op get "pushed") + _rounds - (_op get "stepDone")];
    _op set ["stepIndex", _index + 1];
    _op set ["stepDone", 0];
    _op set ["stage", "insert"];
    _op set ["phase", 0];
    _op set ["tried", false];
    _op set ["pressure", 0];
    _op set ["attempt", (_op get "attempt") + 1];
    _op set ["combo", (_op get "combo") + 1];
    PLAY_SOUND(drop_item);
};

nil
