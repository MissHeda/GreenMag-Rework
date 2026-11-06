#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * ACE Arsenal has filled the ammunition tab: ammunition one of the unit's weapons can be loaded with stands out in colour,
 * universal ammunition too. Rounds and packs need a magazine of loose rounds, belts a belt magazine.
 *
 * Arguments:
 * 0: The arsenal display <DISPLAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_display] call gmr_compat_ace_fnc_arsenalHighlight;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]]];

private _list = _display displayCtrl ARSENAL_ITEM_LIST;

if (isNull _list) exitWith {};

(call FUNC(arsenalFits)) params ["_loose", "_belts"];

for "_row" from 0 to ((lnbSize _list) select 0) - 1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0) then {
        private _facts = [_item] call EFUNC(main,itemInfo);
        private _fits = [_loose, _belts] select ((_facts select ITEM_KIND) == "belt");

        if (_fits getOrDefault [_facts select ITEM_CALIBER, false]) then {
            _list lnbSetColor [[_row, 1], ARSENAL_FITS_COLOR];
        };
    };
};

nil
