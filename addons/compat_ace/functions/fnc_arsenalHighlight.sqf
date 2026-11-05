#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * ACE Arsenal has filled the ammunition tab: ammunition one of the unit's weapons can be loaded with stands out in colour,
 * universal ammunition too. Rounds and packs need a magazine of loose rounds, belts a belt magazine. ACE keeps a row's colour and only changes its transparency when the row no longer fits the container.
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

private _unit = missionNamespace getVariable ["ace_arsenal_center", player];
// A magazine of loose rounds takes rounds and packs, a belt magazine takes belts: a caliber only lights up for the kind
// one of the weapons can be loaded with.
private _loose = createHashMap;
private _belts = createHashMap;

{
    if (_x isNotEqualTo "") then {
        {
            private _facts = [_x] call EFUNC(main,magazineInfo);

            if (_facts select MAG_OK) then {
                private _fits = [_loose, _belts] select (_facts select MAG_BELT);

                _fits set [_facts select MAG_CALIBER, true];
                _fits set ["universal", true];
            };
        } forEach (compatibleMagazines _x);
    };
} forEach [primaryWeapon _unit, handgunWeapon _unit, secondaryWeapon _unit];

for "_row" from 0 to ((lnbSize _list) select 0) - 1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0) then {
        private _facts = [_item] call EFUNC(main,itemInfo);
        private _fits = [_loose, _belts] select ((_facts select ITEM_KIND) == "belt");

        if ((_facts select ITEM_CALIBER) in _fits) then {
            _list lnbSetColor [[_row, 1], ARSENAL_FITS_COLOR];
        };
    };
};

nil
