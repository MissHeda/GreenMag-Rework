#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The minigame's track, every frame: the round flies across once per try, and each try puts the magazine, the
 * opening to hit, somewhere new on the track, the rounds of the run standing in it, with a narrower opening the longer the run.
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

    // The run so far stands in the magazine, as many rounds as fit in it.
    private _size2 = _ui get "stackSize";
    private _step = _size2 * 0.42;
    private _left = _stripX + _from * _stripW + UI_ZONE_HEIGHT * 0.35;
    private _room = floor ((_size * _stripW - UI_ZONE_HEIGHT * 0.7 - _size2) / _step) + 1;
    private _standing = (GVAR(op) get "combo") min _room;

    {
        _x ctrlSetPositionX (_left + _forEachIndex * _step - _size2 * 0.3);
        _x ctrlSetFade ([1, 0] select (_forEachIndex < _standing));
        _x ctrlCommit 0;
    } forEach (_ui get "stack");
};

// The streak beside the count grows louder the longer it runs.
private _combo = GVAR(op) get "combo";

if (_combo != (_ui get "comboShown")) then {
    _ui set ["comboShown", _combo];

    // A miss empties the magazine at once.
    {
        if (_forEachIndex >= _combo) then {
            _x ctrlSetFade 1;
            _x ctrlCommit 0;
        };
    } forEach (_ui get "stack");

    private _tier = {_combo >= _x} count [2, 5, 10, 20];
    private _text = if (_tier == 0) then {""} else {
        format [[LLSTRING(Streak_1), LLSTRING(Streak_2), LLSTRING(Streak_3), LLSTRING(Streak_4)] select (_tier - 1), _combo]
    };

    (_ui get "combo") ctrlSetStructuredText parseText format [
        "<t align='right' size='%1' color='%2' font='PuristaBold' shadow='%3'>%4</t>",
        [0, 0.85, 1.0, 1.15, 1.3] select _tier,
        ["#ffffff", "#9be89b", "#ffd75a", "#ff9a3c", "#ff4d4d"] select _tier,
        [0, 0, 1, 2, 2] select _tier,
        _text
    ];
};

private _round = _ui get "round";
private _stalled = CBA_missionTime < (GVAR(op) get "stall");

_round ctrlSetPositionX (_stripX + ((GVAR(op) get "phase") min 1) * _stripW - (_ui get "roundW") / 2);
_round ctrlCommit 0;
_round ctrlSetTextColor ([UI_ROUND_COLOR, UI_MISS_COLOR] select _stalled);

nil
