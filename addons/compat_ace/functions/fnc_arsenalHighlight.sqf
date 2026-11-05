#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * ACE Arsenal has filled the ammunition tab: ammunition that fits one of the unit's weapons stands out in colour, universal
 * ammunition too. ACE keeps a row's colour and only changes its transparency when the row no longer fits the container.
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
private _calibers = createHashMapFromArray [["universal", true]];

{
    if (_x isNotEqualTo "") then {
        {
            _calibers set [([_x] call EFUNC(main,magazineInfo)) select MAG_CALIBER, true];
        } forEach (compatibleMagazines _x);
    };
} forEach [primaryWeapon _unit, handgunWeapon _unit, secondaryWeapon _unit];

for "_row" from 0 to ((lnbSize _list) select 0) - 1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0 && {(([_item] call EFUNC(main,itemInfo)) select ITEM_CALIBER) in _calibers}) then {
        _list lnbSetColor [[_row, 1], ARSENAL_FITS_COLOR];
    };
};

nil
