#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The minigame's track, every frame: the round flies across once per try, and each try puts the opening to hit
 * somewhere new on the track, with a narrower opening the longer the run.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_uiGame;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _ui = GVAR(op) get "ui";

if !("round" in _ui) exitWith {};

private _stripX = _ui get "stripX";
private _stripW = _ui get "stripW";

if ((GVAR(op) get "attempt") != (GVAR(op) get "attemptShown")) then {
    private _size = GAME_ZONE_MIN max (GAME_ZONE_START - GAME_ZONE_SHRINK * (GVAR(op) get "combo"));
    private _from = 0.3 + random (0.65 - _size);

    GVAR(op) set ["attemptShown", GVAR(op) get "attempt"];
    GVAR(op) set ["tried", false];
    GVAR(op) set ["zone", _from];
    GVAR(op) set ["zoneSize", _size];

    {
        _x ctrlSetPositionX (_stripX + _from * _stripW);
        _x ctrlSetPositionW (_size * _stripW);
        _x ctrlCommit 0;
    } forEach [_ui get "glow", _ui get "hit"];

    (_ui get "edges") params ["_left", "_right"];

    _left ctrlSetPositionX (_stripX + _from * _stripW);
    _left ctrlCommit 0;
    _right ctrlSetPositionX (_stripX + (_from + _size) * _stripW - UI_EDGE_WIDTH);
    _right ctrlCommit 0;
};

private _round = _ui get "round";
private _stalled = CBA_missionTime < (GVAR(op) get "stall");

_round ctrlSetPositionX (_stripX + ((GVAR(op) get "phase") min 1) * _stripW - (_ui get "roundW") / 2);
_round ctrlCommit 0;
_round ctrlSetTextColor ([UI_ROUND_COLOR, UI_MISS_COLOR] select _stalled);

nil
