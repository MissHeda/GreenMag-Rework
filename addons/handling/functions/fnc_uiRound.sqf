#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Brings the display in step with the rounds: the count, the segments lit, a spark on the one that just changed and the
 * line below. Called once per round, with its click.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_uiRound;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _ui = GVAR(op) get "ui";

if (_ui isEqualTo createHashMap) exitWith {};

private _capacity = (GVAR(op) get "capacity") max 1;
private _shown = GVAR(op) get "shown";
private _before = GVAR(op) get "shownAtStart";
private _segments = _ui get "segments";
private _lit = ceil (_segments * _shown / _capacity);
private _old = ceil (_segments * _before / _capacity);

{
    _x ctrlSetTextColor (switch (true) do {
        case (_forEachIndex >= _lit): {UI_OFF_COLOR};
        case (_forEachIndex >= _old): {UI_ON_COLOR};
        default {UI_OLD_COLOR};
    });
} forEach (_ui get "strip");

if (EGVAR(main,roundCounter)) then {
    (_ui get "count") ctrlSetStructuredText parseText format [
        "<t size='1.5' font='PuristaSemibold' shadow='0'>%1</t><t size='0.95' color='#9a9a9a' font='PuristaLight'> / %2</t>",
        _shown, _capacity
    ];
};

if (_ui getOrDefault ["classic", false]) then {
    (_ui get "ring") ctrlSetText format ["\A3\Ui_f\data\IGUI\Cfg\HoldActions\progress\progress_%1_ca.paa", round (24 * _shown / _capacity)];

    if (EGVAR(main,roundCounter)) then {
        (_ui get "count") ctrlSetStructuredText parseText format ["<t align='center' size='1.1' font='PuristaSemibold' shadow='2'>%1 / %2</t>", _shown, _capacity];
    };
};

// The speedloader's badge lights up with each round it sped up.
private _badge = _ui getOrDefault ["badge", controlNull];

if (!isNull _badge && {(GVAR(op) get "played") > 0}) then {
    _badge ctrlSetFade 0;
    _badge ctrlCommit 0;
    _badge ctrlSetFade 0.45;
    _badge ctrlCommit UI_SPARK_TIME * 1.5;
};

if ((GVAR(op) get "played") > 0) then {
    private _spark = _ui get "spark";
    private _at = (_lit - 1) max 0;

    _spark ctrlSetPositionX ((_ui get "stripX") + _at * ((_ui get "segmentW") + (_ui get "gap")));
    _spark ctrlSetFade 0;
    _spark ctrlCommit 0;
    _spark ctrlSetFade 1;
    _spark ctrlCommit UI_SPARK_TIME;
};

private _waiting = (GVAR(op) get "started") < 0;
private _key = (actionKeysNames ["Action", 1, "Keyboard"]) splitString """" joinString "";
private _keyName = if (_key isEqualTo "") then {"Action"} else {_key};
private _line = switch (true) do {
    case (_waiting): {format [LLSTRING(Prompt_Hold), _keyName]};
    case (GVAR(op) getOrDefault ["clipGame", false]): {
        format [[LLSTRING(Prompt_ClipInsert), LLSTRING(Prompt_ClipPush)] select ((GVAR(op) get "stage") == "push"), _keyName]
    };
    case (GVAR(op) get "game"): {format [[LLSTRING(Prompt_Game), LLSTRING(Prompt_GameMust)] select (GVAR(op) get "mustHit"), _keyName]};
    case (GVAR(op) get "hold"): {LLSTRING(Prompt_LetGo)};
    default {LLSTRING(Prompt_Esc)};
};

(_ui get "prompt") ctrlSetStructuredText parseText format ["<t align='center' size='0.72' color='#9aa0a8' shadow='%2'>%1</t>", _line, [0, 2] select (_ui getOrDefault ["classic", false])];

nil
