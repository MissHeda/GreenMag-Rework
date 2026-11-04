#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The belt items of one type a unit carries.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Belt type, the class name up to the length: "gmr_belt_556x45_basic_" <STRING>
 *
 * Return Value:
 * [[class, length], ...] with one entry per belt, longest first <ARRAY>
 *
 * Example:
 * [player, "gmr_belt_556x45_basic_"] call gmr_main_fnc_beltItems;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_type", "", [""]]];

private _belts = [];

{
    private _facts = [_x] call FUNC(itemInfo);

    if ((_facts select ITEM_BELT_TYPE) == _type) then {
        for "_i" from 1 to _y do {
            _belts pushBack [_facts select ITEM_ROUNDS, _x];
        };
    };
} forEach ([_unit] call FUNC(itemCounts));

_belts sort false;

_belts apply {[_x select 1, _x select 0]}
