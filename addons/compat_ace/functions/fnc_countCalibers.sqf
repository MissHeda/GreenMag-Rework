#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Counts which ammunition the loaded mods' magazines take, for the arsenal: loose rounds or belts, of which caliber and
 * kind. Thousands of classes, so in the background: it would be a noticeable hang on the arsenal's first opening.
 * Universal ammunition is there for the magazines nothing else fits. Once only: further calls do nothing.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_compat_ace_fnc_countCalibers;
 *
 * Public: No
 */

if (GVAR(countingCalibers)) exitWith {};

GVAR(countingCalibers) = true;

[] spawn {
    private _used = createHashMapFromArray [["round:universal:basic", true], ["belt:universal:basic", true]];

    {
        private _facts = [configName _x] call EFUNC(main,magazineInfo);

        if (_facts select MAG_OK) then {
            private _kind = ["round", "belt"] select (_facts select MAG_BELT);

            // Basic ammunition fills any magazine of its caliber, so it is there as soon as one of its kinds is.
            {
                _used set [format ["%1:%2:%3", _kind, _facts select MAG_CALIBER, _x], true];
            } forEach ["basic", _facts select MAG_TYPE];
        };
    } forEach ("getNumber (_x >> 'scope') > 0" configClasses (configFile >> "CfgMagazines"));

    GVAR(usedCalibers) = _used;
};

nil
