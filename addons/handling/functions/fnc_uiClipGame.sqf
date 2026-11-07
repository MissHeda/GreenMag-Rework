#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The stripper clip minigame's picture, every frame (fnc_clipGameTick plays it). While a clip goes in, it sweeps over the
 * track towards the magazine, whose guide is the green opening; each new clip puts the magazine somewhere else, with a
 * narrower opening the longer the run. While the rounds are pressed down, the clip sits on the magazine and sinks with
 * them, and the gauge below shows the thumb's pressure: in the green the rounds slide in, at the red the clip jams.
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

private _ui = GVAR(op) get "ui";

if !("clip" in _ui) exitWith {};

private _stripX = _ui get "stripX";
private _stripW = _ui get "stripW";
private _clipW = _ui get "clipW";
private _catcherW = _ui get "catcherW";

// A new clip: the magazine waits somewhere new, the opening a little narrower the longer the run.
if ((GVAR(op) get "attempt") != (GVAR(op) get "attemptShown")) then {
    private _size = GAME_ZONE_MIN max (GAME_ZONE_START - GAME_ZONE_SHRINK * (GVAR(op) get "combo"));
    private _from = 0.3 + random (0.65 - _size);

    GVAR(op) set ["attemptShown", GVAR(op) get "attempt"];
    GVAR(op) set ["zone", _from];
    GVAR(op) set ["zoneSize", _size];

    private _left = _stripX + _from * _stripW;

    {
        _x ctrlSetPositionX _left;
        _x ctrlSetPositionW (_size * _stripW);
        _x ctrlCommit 0;
    } forEach [_ui get "glow", _ui get "hit"];

    private _catcher = _ui get "catcher";

    _catcher ctrlSetPositionX (_left + _size * _stripW / 2 - _catcherW / 2);
    _catcher ctrlCommit 0;
};

call FUNC(uiStreak);

// What to do changes with the stage: the line below says it anew (fnc_uiRound writes it).
if ((GVAR(op) get "stage") isNotEqualTo (_ui getOrDefault ["stageShown", ""])) then {
    _ui set ["stageShown", GVAR(op) get "stage"];

    private _played = GVAR(op) get "played";

    // Without a spark: it is not a round that moved.
    GVAR(op) set ["played", 0];
    call FUNC(uiRound);
    GVAR(op) set ["played", _played];
};

private _clip = _ui get "clip";
private _stalled = CBA_missionTime < (GVAR(op) get "stall");
private _pushing = (GVAR(op) get "stage") == "push";
private _clipY = _ui get "clipY";

if (_pushing) then {
    // On the magazine, sinking with the rounds pressed out of it.
    private _rounds = (GVAR(op) get "steps") param [GVAR(op) get "stepIndex", 1];
    private _middle = _stripX + ((GVAR(op) get "zone") + (GVAR(op) get "zoneSize") / 2) * _stripW;

    _clip ctrlSetPositionX (_middle - _clipW / 2);
    _clip ctrlSetPositionY (_clipY + (_ui get "sink") * ((GVAR(op) get "stepDone") / (_rounds max 1)));
} else {
    _clip ctrlSetPositionX (_stripX + ((GVAR(op) get "phase") min 1) * _stripW - _clipW / 2);
    _clip ctrlSetPositionY _clipY;
};

_clip ctrlCommit 0;
_clip ctrlSetTextColor ([[1, 1, 1, 1], UI_MISS_COLOR] select _stalled);

// The thumb's pressure, only while pressing: amber below the green, green while the rounds move, red near the jam.
private _pressure = GVAR(op) get "pressure";
private _fill = _ui get "gaugeFill";

{
    _x ctrlSetFade ([1, 0] select _pushing);
    _x ctrlCommit 0;
} forEach (_ui get "gauge");

_fill ctrlSetPositionW ((_stripW * (_pressure min 1)) max 0.0001);
_fill ctrlCommit 0;
_fill ctrlSetTextColor (switch (true) do {
    case (_stalled): {UI_MISS_COLOR};
    case (_pressure >= CLIP_PRESSURE_RED - 0.08): {UI_MISS_COLOR};
    case (_pressure >= CLIP_PRESSURE_GREEN): {UI_ON_COLOR};
    default {UI_GAUGE_COLOR};
});

nil
