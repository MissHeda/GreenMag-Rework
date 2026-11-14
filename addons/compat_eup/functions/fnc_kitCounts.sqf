#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * How many of each of this mod's items are inside the pouches and kits a unit carries (EFAK framework: Enhanced Utility
 * Pouches, Enhanced First Aid Kits). Only what lies directly in a carried pouch counts, not what is in a kit packed
 * inside another one.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 *
 * Return Value:
 * Item class -> count, the class as the config spells it <HASHMAP>
 *
 * Example:
 * [player] call gmr_compat_eup_fnc_kitCounts;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _counts = createHashMap;

{
    {
        _x params ["_class", "_amount"];

        if ((([_class] call EFUNC(main,itemInfo)) select ITEM_KIND) isNotEqualTo "") then {
            private _key = configName (configFile >> "CfgWeapons" >> _class);

            _counts set [_key, (_counts getOrDefault [_key, 0]) + _amount];
        };
    } forEach ([_x] call efak_core_fnc_getContents);
} forEach ([_unit] call efak_core_fnc_getCarriedKits);

_counts
