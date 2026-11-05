#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * ACE Arsenal has filled the ammunition tab: takes out what the settings do not show, belts, packs or single rounds.
 *
 * Arguments:
 * 0: The arsenal display <DISPLAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_display] call gmr_compat_ace_fnc_arsenalFilter;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]]];

private _list = _display displayCtrl ARSENAL_ITEM_LIST;

if (isNull _list) exitWith {};

private _hidden = [];

{
    _x params ["_shown", "_kind"];

    if (!_shown) then {
        _hidden pushBack _kind;
    };
} forEach [[EGVAR(main,arsenalBelts), "belt"], [EGVAR(main,arsenalPacks), "pack"], [EGVAR(main,arsenalRounds), "round"]];

if (_hidden isEqualTo []) exitWith {};

for "_row" from ((lnbSize _list) select 0) - 1 to 0 step -1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0 && {(([_item] call EFUNC(main,itemInfo)) select ITEM_KIND) in _hidden}) then {
        _list lnbDeleteRow _row;
    };
};

nil
