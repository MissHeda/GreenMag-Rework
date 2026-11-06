#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The key was pressed during the minigame, one try per pass of the round. On the magazine the round seats at once and the
 * run grows, which narrows the opening; off it the hand fumbles for a moment and the run is over. What happens without a
 * press is the server's choice (fnc_tick): the round seats anyway, so nobody has to play, or nothing happens until it is hit.
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

private _phase = GVAR(op) get "phase";
private _from = GVAR(op) get "zone";

if (_phase >= _from && {_phase <= _from + (GVAR(op) get "zoneSize")}) then {
    private _hit = (GVAR(op) get "ui") getOrDefault ["hit", controlNull];

    _hit ctrlSetFade 0;
    _hit ctrlCommit 0;
    _hit ctrlSetFade 1;
    _hit ctrlCommit UI_HIT_TIME;

    GVAR(op) set ["rounds", (GVAR(op) get "rounds") + 1];
    GVAR(op) set ["phase", 0];
    GVAR(op) set ["attempt", (GVAR(op) get "attempt") + 1];
    GVAR(op) set ["combo", (GVAR(op) get "combo") + 1];
    PLAY_SOUND(drop_item);

    // A long enough streak pays out extra rounds, the longest a full magazine.
    call FUNC(gameReward);
} else {
    GVAR(op) set ["stall", CBA_missionTime + GAME_MISS_STALL];
    GVAR(op) set ["combo", 0];
    PLAY_SOUND(denied);
};

nil
