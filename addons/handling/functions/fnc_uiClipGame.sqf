#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Draws the stripper clip minigame's window every frame (fnc_clipGameOpen built it, fnc_clipGameTick plays it): the
 * clip where it lies or is dragged, its rounds sinking out of it into the magazine, the magazine's top rounds, the
 * thumb's mark and its pull to the cursor, green while the rounds keep up and red as they are about to jam.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_uiClipGame;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _cg = GVAR(op) getOrDefault ["cg", createHashMap];

if (_cg isEqualTo createHashMap) exitWith {};

private _stage = GVAR(op) get "stage";
private _roundH = _cg get "roundH";
private _per = _cg get "per";
private _travel = _cg get "travel";
private _stalled = CBA_missionTime < (GVAR(op) get "stall");
private _magTop = _cg get "magTop";
private _steps = GVAR(op) get "steps";
private _index = GVAR(op) get "stepIndex";
private _fits = _steps param [_index, _per];

(_cg get "pos") params ["_px", "_py"];

// The empty clip flies off up and away.
private _flying = _cg get "flying";
private _strip = _cg get "strip";

if (_flying) then {
    private _t = ((CBA_missionTime - (_cg get "stageStart")) / CG_STRIP_TIME) min 1;

    _px = _px + 0.12 * _t;
    _py = _py - 0.08 * _t;
    _strip ctrlSetFade _t;
} else {
    _strip ctrlSetFade 0;
};

_strip ctrlSetPosition [_px - 0.008, _py, 0.006, _cg get "clipH"];
_strip ctrlCommit 0;

// The clip's rounds: those that went in are in the magazine now; those left on a clip that had more than fitted stay.
private _seated = _stage in ["push", "strip"];

{
    private _down = [0, _travel] select _seated;
    private _rowY = _py + 0.002 + (_forEachIndex + _down) * _roundH;
    private _gone = _seated && {_forEachIndex >= _per - _fits} && {(_forEachIndex + _down) > _per - 0.5};

    _x ctrlShow (!_gone && {!_flying || {_forEachIndex < _per - _fits}});
    _x ctrlSetPosition [_px, _rowY, _cg get "roundW", _roundH];
    _x ctrlSetTextColor ([UI_ROUND_COLOR, UI_MISS_COLOR] select _stalled);
    _x ctrlCommit 0;
} forEach (_cg get "rounds");

// The rounds left on a partly used clip fly off with it.
if (_flying) then {
    {
        if (_forEachIndex < _per - _fits) then {
            _x ctrlSetPosition [_px, _py + 0.002 + (_forEachIndex + _travel) * _roundH, _cg get "roundW", _roundH];
            _x ctrlSetFade ((CBA_missionTime - (_cg get "stageStart")) / CG_STRIP_TIME);
            _x ctrlCommit 0;
        };
    } forEach (_cg get "rounds");
} else {
    {_x ctrlSetFade 0; _x ctrlCommit 0} forEach (_cg get "rounds");
};

// The magazine's top rounds: as many as it holds now, the newest on top.
private _shown = GVAR(op) get "shown";

{
    _x ctrlShow (_forEachIndex < _shown);
} forEach (_cg get "magRounds");

// Where the clip goes, while it is not there yet.
(_cg get "ghost") ctrlShow (_stage == "place");

// The thumb's mark on the top round still on the clip, and the pull to the cursor while it presses.
private _handle = _cg get "handle";
private _band = _cg get "band";
private _pushing = _stage == "push";

_handle ctrlShow _pushing;
_band ctrlShow (_pushing && {_cg get "held"});

if (_pushing) then {
    private _markX = _px;
    private _markY = _py + 0.002 + _travel * _roundH;
    private _slack = _cg get "slack";
    private _colour = switch (true) do {
        case (_stalled): {UI_MISS_COLOR};
        case (_slack > CG_JAM_SLACK * 0.7): {UI_MISS_COLOR};
        case (_slack > CG_JAM_SLACK * 0.35): {UI_GAUGE_COLOR};
        default {UI_ON_COLOR};
    };

    _handle ctrlSetPosition [_markX + (_cg get "roundW") * 0.3 - CG_HANDLE / 2, _markY - CG_HANDLE * 2 / 3, CG_HANDLE, CG_HANDLE * 4 / 3];
    _handle ctrlSetTextColor ([UI_GAUGE_COLOR, _colour] select (_cg get "held"));
    _handle ctrlCommit 0;

    if (_cg get "held") then {
        private _cursorY = getMousePosition select 1;

        _band ctrlSetPosition [_markX + (_cg get "roundW") * 0.3 - 0.0015, _markY, 0.003, (_cursorY - _markY) max 0];
        _band ctrlSetBackgroundColor _colour;
        _band ctrlCommit 0;
    };
};

// The count, the clips left, and what to do now.
(_cg get "count") ctrlSetStructuredText parseText format [
    "<t size='1.3' font='PuristaSemibold'>%1</t><t size='0.9' color='#9a9a9a' font='PuristaLight'> / %2</t><t size='0.8' color='#9aa0a8'>    %3 %4/%5</t>",
    _shown, GVAR(op) get "capacity", LLSTRING(Clip_Count), (_index + 1) min (count _steps), count _steps
];

call FUNC(uiStreak);

private _hint = switch (true) do {
    case (_stalled): {LLSTRING(Clip_Jammed)};
    case (_stage == "place"): {LLSTRING(Clip_Place)};
    case (_stage == "push"): {LLSTRING(Clip_Push)};
    default {""};
};

if (_hint isNotEqualTo (_cg get "hintShown")) then {
    _cg set ["hintShown", _hint];
    (_cg get "hint") ctrlSetStructuredText parseText format ["<t align='center' size='0.72' color='#9aa0a8'>%1</t>", _hint];
};

nil
