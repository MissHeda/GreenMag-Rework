#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A hit in the minigame has just grown the streak: from the server's first reward streak on, every few hits throw in
 * extra rounds, a random 1 up to one more per reward so far (at most the server's limit). At the jackpot streak, and at
 * every multiple of it, the magazine in hand fills at once. The extra rounds come out of the same ammunition as the
 * others, so they make it faster, never cheaper.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_gameReward;
 *
 * Public: No
 */

if (isNil QGVAR(op) || {!EGVAR(main,gameRewards)}) exitWith {};

private _combo = GVAR(op) get "combo";
private _rounds = GVAR(op) get "rounds";
private _need = GVAR(op) get "need";

if (_rounds >= _need) exitWith {};

private _start = round EGVAR(main,gameRewardStart);
private _step = (round EGVAR(main,gameRewardStep)) max 1;
private _jackpot = round EGVAR(main,gameRewardJackpot);

// The jackpot: up to the end of the magazine that is being worked on now.
if (_jackpot > 0 && {_combo >= _jackpot} && {_combo % _jackpot == 0}) exitWith {
    private _kind = GVAR(op) get "kind";
    private _capacity = GVAR(op) get "capacity";
    private _end = 0;

    {
        _end = _end + ([_x, _capacity - _x] select (_kind == "fill"));

        if (_end > _rounds) exitWith {};
    } forEach (GVAR(op) get "amounts");

    _end = (_end max (_rounds + 1)) min _need;

    GVAR(op) set ["rounds", _end];
    GVAR(op) set ["bonusText", format [LLSTRING(Reward_Full), _end - _rounds]];
    GVAR(op) set ["bonusUntil", CBA_missionTime + GAME_REWARD_SHOW];
    PLAY_SOUND(magazine_done);
};

if (_start <= 0 || {_combo < _start} || {(_combo - _start) % _step != 0}) exitWith {};

private _tier = (_combo - _start) / _step + 1;
private _extra = (1 + floor random (_tier min (round EGVAR(main,gameRewardMaxRounds)))) min (_need - _rounds);

if (_extra <= 0) exitWith {};

GVAR(op) set ["rounds", _rounds + _extra];
GVAR(op) set ["bonusText", format [[LLSTRING(Reward_Rounds), LLSTRING(Reward_Round)] select (_extra == 1), _extra]];
GVAR(op) set ["bonusUntil", CBA_missionTime + GAME_REWARD_SHOW];
PLAY_SOUND(round_in_8);

nil
