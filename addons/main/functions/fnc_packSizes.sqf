#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The pack sizes of a caliber, largest first, as its real cartridges are boxed (gmr_calibers >> packs[]).
 *
 * Arguments:
 * 0: Caliber <STRING>
 *
 * Return Value:
 * Rounds per pack <ARRAY>
 *
 * Example:
 * ["556x45"] call gmr_main_fnc_packSizes;
 *
 * Public: No
 */

params [["_caliber", "", [""]]];

private _sizes = getArray (configFile >> "gmr_calibers" >> _caliber >> "packs");

if (_sizes isEqualTo []) then {[30]} else {_sizes}
