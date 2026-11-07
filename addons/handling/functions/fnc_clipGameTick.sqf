#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The stripper clip minigame, every frame (fnc_tick), played with the mouse in its window (fnc_clipGameOpen).
 *
 * "place": the clip is dragged from where it lies into the guide on the magazine. Let go near the guide, it slides in;
 * anywhere else, it drops back. "push": the thumb's mark on the top round is held and pulled down. The rounds follow,
 * at most as fast as the spring lets them, slower the fuller the magazine; pulled further ahead than that, the rounds
 * jam: they spring back to the last one that went in and the thumb has to set on again. "strip": the empty clip flies
 * off, and the next one lies ready.
 * Without the server's "must hit" a clip left alone for a few seconds slides into the guide by itself, and its rounds
 * sink in unpressed, slower than pressed, so nobody has to play but playing is faster.
 *
 * Arguments:
 * 0: Seconds since the last frame <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [0.016] call gmr_handling_fnc_clipGameTick;
 *
 * Public: No
 */

params [["_step", 0, [0]]];

if (isNil QGVAR(op)) exitWith {};

private _op = GVAR(op);
private _cg = _op getOrDefault ["cg", createHashMap];

if (_cg isEqualTo createHashMap) exitWith {};

private _now = CBA_missionTime;
private _steps = _op get "steps";
private _index = _op get "stepIndex";

if (_index >= count _steps) exitWith {};

private _mustHit = _op get "mustHit";
private _mouse = inputMouse 0 > 0;
private _pressedNow = _mouse && {!(_cg get "mouse")};
private _released = !_mouse && {_cg get "mouse"};
private _cursor = getMousePosition;
private _stage = _op get "stage";

_cg set ["mouse", _mouse];

// A jam holds the thumb for a moment.
if (_now < (_op get "stall")) exitWith {};

private _fnc_seat = {
    _cg set ["pos", _cg get "seat"];
    _cg set ["dragging", false];
    _cg set ["travel", 0];
    _cg set ["held", false];
    _op set ["stage", "push"];
    _cg set ["stageStart", _now];
    PLAY_SOUND(grab);
};

if (_stage == "place") exitWith {
    (_cg get "pos") params ["_clipX", "_clipY"];
    private _clipH = _cg get "clipH";
    private _clipW = (_cg get "roundW") + 0.01;

    if (_pressedNow
        && {(_cursor select 0) >= _clipX - 0.012 && {(_cursor select 0) <= _clipX + _clipW}}
        && {(_cursor select 1) >= _clipY && {(_cursor select 1) <= _clipY + _clipH}}
    ) then {
        _cg set ["dragging", true];
        _cg set ["grab", [(_cursor select 0) - _clipX, (_cursor select 1) - _clipY]];
    };

    if (_cg get "dragging") then {
        (_cg get "grab") params ["_dx", "_dy"];

        _cg set ["pos", [(_cursor select 0) - _dx, (_cursor select 1) - _dy]];
        _cg set ["stageStart", _now];

        if (_released) then {
            _cg set ["dragging", false];
            (_cg get "pos") params ["_px", "_py"];
            (_cg get "seat") params ["_sx", "_sy"];

            if (abs (_px - _sx) < CG_SNAP_X && {abs (_py - _sy) < CG_SNAP_Y}) then {
                call _fnc_seat;
            } else {
                // Off the guide: it drops back where it lay.
                _cg set ["pos", _cg get "table"];
                _op set ["combo", 0];
                PLAY_SOUND(denied);
            };
        };
    } else {
        if (!_mustHit && {_now > (_cg get "stageStart") + CG_AUTO_WAIT}) then {
            call _fnc_seat;
        };
    };
};

private _per = _cg get "per";
private _rounds = _steps select _index;
private _travel = _cg get "travel";

if (_stage == "push") exitWith {
    private _roundH = _cg get "roundH";
    private _fill = (_op get "shown") / ((_op get "capacity") max 1);
    private _rate = CG_PUSH_RATE / ((_op get "beat") max 0.01) * (1 - CG_SPRING * _fill);

    // The thumb sets on at its mark: the top round left on the clip.
    if (_pressedNow) then {
        (_cg get "seat") params ["_sx", "_sy"];
        private _markY = _sy + 0.002 + _travel * _roundH;

        if (abs ((_cursor select 1) - _markY) < CG_GRAB_RANGE && {(_cursor select 0) >= _sx - 0.03 && {(_cursor select 0) <= _sx + (_cg get "roundW") + 0.03}}) then {
            _cg set ["held", true];
            _cg set ["stageStart", _now];
            _cg set ["grabY", _cursor select 1];
            _cg set ["grabTravel", _travel];
        };
    };

    if (!_mouse && {_cg get "held"}) then {
        _cg set ["held", false];
        _cg set ["stageStart", _now];
    };

    private _move = 0;

    if (_cg get "held") then {
        private _target = ((_cg get "grabTravel") + ((_cursor select 1) - (_cg get "grabY")) / _roundH) min _rounds;
        private _slack = _target - _travel;

        _cg set ["slack", _slack max 0];

        // Pulled ahead of what the spring lets through: the rounds jam and spring back to the last one in.
        if (_slack > CG_JAM_SLACK) exitWith {
            _cg set ["travel", floor _travel];
            _cg set ["held", false];
            _cg set ["slack", 0];
            _op set ["stall", _now + CG_JAM_STALL];
            _op set ["combo", 0];
            _op set ["pushed", (_op get "stepsDone") + floor _travel];
            PLAY_SOUND(denied);
        };

        if (_slack > 0) then {
            _move = _slack min (_rate * _step);
        };
    } else {
        _cg set ["slack", 0];

        // Left alone a while without "must hit", the rounds sink in by themselves, slower than pressed.
        if (!_mustHit && {_now > (_cg get "stageStart") + CG_AUTO_WAIT}) then {
            _move = CG_AUTO_RATE * _step / ((_op get "beat") max 0.01);
        };
    };

    if (_now < (_op get "stall")) exitWith {};

    _travel = (_travel + _move) min _rounds;
    _cg set ["travel", _travel];
    _op set ["pushed", (_op get "stepsDone") + _travel];

    // All of this clip's rounds that fit are in: the clip comes away.
    if (_travel >= _rounds - 0.0001) then {
        _op set ["stepsDone", (_op get "stepsDone") + _rounds];
        _op set ["pushed", _op get "stepsDone"];
        _op set ["stage", "strip"];
        _op set ["combo", (_op get "combo") + 1];
        _cg set ["held", false];
        _cg set ["stageStart", _now];
        _cg set ["flying", true];
        PLAY_SOUND(drop_item);
    };
};

// "strip": the empty clip flies off; then the next one lies ready.
if (_now > (_cg get "stageStart") + CG_STRIP_TIME) then {
    _op set ["stepIndex", _index + 1];
    _op set ["stage", "place"];
    _cg set ["travel", 0];
    _cg set ["pos", _cg get "table"];
    _cg set ["flying", false];
    _cg set ["stageStart", _now];
};

nil
