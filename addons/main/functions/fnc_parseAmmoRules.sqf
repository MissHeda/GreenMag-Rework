#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Reads the server's ammo rules: "part of a magazine's class name: caliber", separated by commas. A third part "belt"
 * or "mag" also says whether it is a belt. No compat patch is needed for a mod's magazines this way. What is known about
 * magazines starts over.
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
    (_x splitString ":") params [["_magazine", ""], ["_caliber", ""], ["_kind", ""]];

    _magazine = toLowerANSI trim _magazine;
    _caliber = toLowerANSI trim _caliber;
    _kind = toLowerANSI trim _kind;

    // -1 = decided as usual by name and size, 1 = belt, 0 = magazine of loose rounds.
    private _belt = switch (true) do {
        case (_kind in ["belt", "box"]): {1};
        case (_kind in ["mag", "magazine", "loose"]): {0};
        default {-1};
    };

    if (_magazine isNotEqualTo "" && {_caliber isNotEqualTo ""}) then {
        GVAR(ammoRuleList) pushBack [_magazine, _caliber, _belt];
    };
} forEach (GVAR(ammoRules) splitString ",");

GVAR(magazineCache) = createHashMap;

nil
