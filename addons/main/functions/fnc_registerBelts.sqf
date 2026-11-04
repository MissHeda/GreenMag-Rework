#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Declares magazines of other mods as belts, for those their name and size do not give away. Local: call it on every
 * machine, or give the magazine gmr_belt = 1 in its config instead.
 *
 * Arguments:
 * 0: Magazine classes <ARRAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [["rhs_100Rnd_762x54mmR"]] call gmr_main_fnc_registerBelts;
 *
 * Public: Yes
 */

params [["_classes", [], [[]]]];

{
    GVAR(registeredBelts) set [toLowerANSI _x, true];
    GVAR(magazineCache) deleteAt toLowerANSI _x;
} forEach _classes;

nil
