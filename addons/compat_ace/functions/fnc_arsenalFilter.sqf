#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * ACE Arsenal has filled the ammunition tab: takes out what the settings do not show, belts, packs or single rounds, and
 * ammunition no magazine of the loaded mods takes, by caliber, kind and whether it is a belt.
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

// Until the background count (XEH_postInit) is through, nothing is hidden for it.
private _usedOnly = EGVAR(main,arsenalUsedCalibers) && {!isNil QGVAR(usedCalibers)};

if (_hidden isEqualTo [] && {!_usedOnly}) exitWith {};

for "_row" from ((lnbSize _list) select 0) - 1 to 0 step -1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0) then {
        private _facts = [_item] call EFUNC(main,itemInfo);
        private _caliber = _facts select ITEM_CALIBER;
        private _key = format ["%1:%2:%3", ["round", "belt"] select ((_facts select ITEM_KIND) == "belt"), _caliber, _facts select ITEM_VARIANT];

        if ((_facts select ITEM_KIND) in _hidden || {_usedOnly && {_caliber isNotEqualTo ""} && {!(_key in GVAR(usedCalibers))}}) then {
            _list lnbDeleteRow _row;
        };
    };
};

nil
