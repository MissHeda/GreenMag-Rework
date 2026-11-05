#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The minigame's track, every frame: the round flies across once per try, and each try puts the magazine, the slot to hit,
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

    private _slot = _ui get "slot";

    _slot ctrlSetPositionX (_stripX + (_from + _size / 2) * _stripW - (_ui get "slotW") / 2);
    _slot ctrlCommit 0;
};

private _round = _ui get "round";
private _stalled = CBA_missionTime < (GVAR(op) get "stall");

_round ctrlSetPositionX (_stripX + ((GVAR(op) get "phase") min 1) * _stripW - (_ui get "roundW") / 2);
_round ctrlCommit 0;
_round ctrlSetTextColor ([UI_ROUND_COLOR, UI_MISS_COLOR] select _stalled);

nil
