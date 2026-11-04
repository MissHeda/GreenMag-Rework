#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The children of "Pack rounds": one entry per kind of loose round the player has at least a small pack of.
 *
 * Arguments:
 * 0: Player <OBJECT>
 *
 * Return Value:
 * ACE actions <ARRAY>
 *
 * Example:
 * [player] call gmr_handling_fnc_menuPack;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _actions = [];

{
    private _facts = [_x] call EFUNC(main,itemInfo);

    if ((_facts select ITEM_KIND) == "round" && {_y >= 10}) then {
        private _action = [
            format ["gmr_pack_%1", _x],
            format ["%1 (%2)", _facts select ITEM_NAME, _y],
            _facts select ITEM_PICTURE,
            {
                params ["", "_player", "_params"];

                [_player, _params select 0] call FUNC(packRounds);
            },
            {true},
            {},
            [_x]
        ] call ace_interact_menu_fnc_createAction;

        _actions pushBack [_action, [], _unit];
    };
} forEach ([_unit] call EFUNC(main,itemCounts));

_actions
