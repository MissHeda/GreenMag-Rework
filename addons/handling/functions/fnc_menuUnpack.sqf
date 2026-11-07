#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The children of "Unpack": one entry per kind of pack and stripper clip the player carries.
 *
 * Arguments:
 * 0: Player <OBJECT>
 *
 * Return Value:
 * ACE actions <ARRAY>
 *
 * Example:
 * [player] call gmr_handling_fnc_menuUnpack;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _packs = (keys ([_unit] call EFUNC(main,itemCounts))) select {
    (([_x] call EFUNC(main,itemInfo)) select ITEM_KIND) in ["pack", "clip"]
};

_packs sort true;

_packs apply {
    private _facts = [_x] call EFUNC(main,itemInfo);
    private _action = [
        format ["gmr_unpack_%1", _x],
        _facts select ITEM_NAME,
        _facts select ITEM_PICTURE,
        {
            params ["", "_player", "_params"];

            [_player, _params select 0, true] call FUNC(unpack);
        },
        {true},
        {},
        [_x]
    ] call ace_interact_menu_fnc_createAction;

    [_action, [], _unit]
}
