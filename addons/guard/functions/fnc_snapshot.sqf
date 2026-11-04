#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The magazines in a unit's uniform, vest and backpack, counted by class and rounds.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 *
 * Return Value:
 * [lowercase class, rounds] -> how many <HASHMAP>
 *
 * Example:
 * [player] call gmr_guard_fnc_snapshot;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _picture = createHashMap;

{
    private _key = [toLowerANSI (_x select 0), _x select 1];

    _picture set [_key, (_picture getOrDefault [_key, 0]) + 1];
} forEach (magazinesAmmoCargo uniformContainer _unit + magazinesAmmoCargo vestContainer _unit + magazinesAmmoCargo backpackContainer _unit);

_picture
