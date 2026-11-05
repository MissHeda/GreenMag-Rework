#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Reads the server's ammo rules: "part of a magazine's class name: caliber", separated by commas. No compat patch is
 * needed for a mod's magazines this way. What is known about magazines starts over.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_main_fnc_parseAmmoRules;
 *
 * Public: No
 */

GVAR(ammoRuleList) = [];

{
    (_x splitString ":") params [["_magazine", ""], ["_caliber", ""]];

    _magazine = toLowerANSI trim _magazine;
    _caliber = toLowerANSI trim _caliber;

    if (_magazine isNotEqualTo "" && {_caliber isNotEqualTo ""}) then {
        GVAR(ammoRuleList) pushBack [_magazine, _caliber];
    };
} forEach (GVAR(ammoRules) splitString ",");

GVAR(magazineCache) = createHashMap;

nil
