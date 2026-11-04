#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * How many of each item a unit has in its uniform, vest and backpack.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 *
 * Return Value:
 * Item class -> count <HASHMAP>
 *
 * Example:
 * [player] call gmr_main_fnc_itemCounts;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _counts = createHashMap;

{
    if (!isNull _x) then {
        (getItemCargo _x) params ["_classes", "_amounts"];

        {
            _counts set [_x, (_counts getOrDefault [_x, 0]) + (_amounts select _forEachIndex)];
        } forEach _classes;
    };
} forEach [uniformContainer _unit, vestContainer _unit, backpackContainer _unit];

_counts
