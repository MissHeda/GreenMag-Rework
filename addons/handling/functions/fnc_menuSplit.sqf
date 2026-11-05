#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The children of "Split belt": one entry per kind of belt the player carries that is long enough.
 *
 * Arguments:
 * 0: Player <OBJECT>
 *
 * Return Value:
 * ACE actions <ARRAY>
 *
 * Example:
 * [player] call gmr_handling_fnc_menuSplit;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _belts = (keys ([_unit] call EFUNC(main,itemCounts))) select {
    private _facts = [_x] call EFUNC(main,itemInfo);

    (_facts select ITEM_KIND) == "belt" && {(_facts select ITEM_ROUNDS) >= 2}
};

_belts sort true;

_belts apply {
    private _facts = [_x] call EFUNC(main,itemInfo);
    private _action = [
        format ["gmr_split_%1", _x],
        _facts select ITEM_NAME,
        _facts select ITEM_PICTURE,
        {
            params ["", "_player", "_params"];

            [_player, _params select 0] call FUNC(splitBelt);
        },
        {true},
        {},
        [_x]
    ] call ace_interact_menu_fnc_createAction;

    [_action, [], _unit]
}
