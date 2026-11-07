#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The run of hits beside the count, in both minigames: louder the longer it runs; a reward it paid out shows there for
 * a moment.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_uiStreak;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _ui = GVAR(op) get "ui";

// The streak beside the count grows louder the longer it runs; a reward it paid out shows there for a moment.
private _combo = GVAR(op) get "combo";
private _bonus = CBA_missionTime < (GVAR(op) get "bonusUntil");
private _key = [_combo, [-1, GVAR(op) get "bonusUntil"] select _bonus];

if (_key isNotEqualTo (_ui get "comboShown")) then {
    _ui set ["comboShown", _key];

    private _tier = {_combo >= _x} count [2, 5, 10, 20];
    private _text = if (_tier == 0) then {""} else {
        format [[LLSTRING(Streak_1), LLSTRING(Streak_2), LLSTRING(Streak_3), LLSTRING(Streak_4)] select (_tier - 1), _combo]
    };

    // A reward takes the place of the streak for its moment: both in one line run out of the panel.
    private _colour = ["#ffffff", "#9be89b", "#ffd75a", "#ff9a3c", "#ff4d4d"] select _tier;

    if (_bonus) then {
        _tier = _tier max 2;
        _text = GVAR(op) get "bonusText";
        _colour = "#6beb6b";
    };

    (_ui get "combo") ctrlSetStructuredText parseText format [
        "<t align='right' size='%1' color='%2' font='PuristaBold' shadow='%3'>%4</t>",
        [0, 0.85, 0.95, 1.05, 1.15] select _tier,
        _colour,
        [0, 0, 1, 2, 2] select _tier,
        _text
    ];
};

nil
