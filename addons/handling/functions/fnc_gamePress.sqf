#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The key was pressed during the minigame, one try per round. In the green zone the round seats at once and the run grows,
 * which narrows the zone; outside it the hand fumbles for a moment and the run is over. Doing nothing just takes the
 * normal time, so the game can only speed loading up or slow it down a little, never stop it.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_gamePress;
 *
 * Public: No
 */

if (isNil QGVAR(op) || {GVAR(op) get "tried"} || {CBA_missionTime < (GVAR(op) get "stall")}) exitWith {};

GVAR(op) set ["tried", true];

private _beat = (GVAR(op) get "time") / (GVAR(op) get "need");
private _progress = GVAR(op) get "progress";
private _round = floor (_progress / _beat + 0.0001);
private _at = (_progress - _round * _beat) / _beat;
private _from = GVAR(op) get "zone";

if (_at >= _from && {_at <= _from + (GVAR(op) get "zoneSize")}) then {
    GVAR(op) set ["progress", ((_round + 1) * _beat) min (GVAR(op) get "time")];
    GVAR(op) set ["combo", (GVAR(op) get "combo") + 1];
    GVAR(op) set ["best", (GVAR(op) get "best") max (GVAR(op) get "combo")];
    PLAY_SOUND(drop_item);
} else {
    GVAR(op) set ["stall", CBA_missionTime + GAME_MISS_STALL];
    GVAR(op) set ["combo", 0];
    PLAY_SOUND(denied);
};

nil
