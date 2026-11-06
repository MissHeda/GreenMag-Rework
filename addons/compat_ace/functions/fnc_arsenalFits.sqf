#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Which ammunition the arsenal's unit can load into its weapons' magazines: calibers of loose rounds (rounds and
 * packs) and calibers of belts, universal ammunition with them while it is on.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * [calibers for rounds and packs, calibers for belts] <ARRAY of HASHMAPs>
 *
 * Example:
 * call gmr_compat_ace_fnc_arsenalFits;
 *
 * Public: No
 */

private _unit = missionNamespace getVariable ["ace_arsenal_center", player];
private _loose = createHashMap;
private _belts = createHashMap;

{
    if (_x isNotEqualTo "") then {
        {
            private _facts = [_x] call EFUNC(main,magazineInfo);

            if (_facts select MAG_OK) then {
                private _fits = [_loose, _belts] select (_facts select MAG_BELT);

                _fits set [_facts select MAG_CALIBER, true];
                _fits set ["universal", EGVAR(main,universalAmmo)];
            };
        } forEach (compatibleMagazines _x);
    };
} forEach [primaryWeapon _unit, handgunWeapon _unit, secondaryWeapon _unit];

[_loose, _belts]
