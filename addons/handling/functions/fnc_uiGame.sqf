#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The minigame's track, every frame: the marker runs across once per round, and each new round gets a new green zone,
 * narrower the longer the run.
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

if !("marker" in _ui) exitWith {};

private _beat = (GVAR(op) get "time") / (GVAR(op) get "need");
private _progress = GVAR(op) get "progress";
private _round = floor (_progress / _beat + 0.0001);
private _stripX = _ui get "stripX";
private _stripW = _ui get "stripW";

if (_round != (GVAR(op) get "round")) then {
    private _size = GAME_ZONE_MIN max (GAME_ZONE_START - GAME_ZONE_SHRINK * (GVAR(op) get "combo"));
    private _from = 0.3 + random (0.65 - _size);
    private _zone = _ui get "zone";

    GVAR(op) set ["round", _round];
    GVAR(op) set ["tried", false];
    GVAR(op) set ["zone", _from];
    GVAR(op) set ["zoneSize", _size];
    _zone ctrlSetPositionX (_stripX + _from * _stripW);
    _zone ctrlSetPositionW (_size * _stripW);
    _zone ctrlCommit 0;
};

private _marker = _ui get "marker";

_marker ctrlSetPositionX (_stripX + ((_progress - _round * _beat) / _beat min 1) * _stripW);
_marker ctrlCommit 0;
_marker ctrlSetBackgroundColor ([[1, 1, 1, 1], UI_MISS_COLOR] select (CBA_missionTime < (GVAR(op) get "stall")));

nil
