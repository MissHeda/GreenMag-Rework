#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes items out of a unit's uniform, vest and backpack in one command per container, and reports what the cargo
 * shows as gone rather than what was asked for.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Item class <STRING>
 * 2: How many <NUMBER>
 *
 * Return Value:
 * How many left the inventory <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30] call gmr_main_fnc_removeItem;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_amount", 0, [0]]];

private _fnc_held = {
    (getItemCargo _this) params ["_classes", "_amounts"];

    private _at = _classes findIf {_x == _class};

    // Not an array with "select": SQF works out both entries first, and select -1 stops the script.
    if (_at < 0) then {0} else {_amounts select _at}
};

private _left = _amount;

{
    if (_left <= 0) exitWith {};

    if (!isNull _x) then {
        private _held = _x call _fnc_held;
        private _take = _left min _held;

        if (_take > 0) then {
            _x addItemCargoGlobal [_class, -_take];
            _left = _left - (_held - (_x call _fnc_held));
        };
    };
} forEach [uniformContainer _unit, vestContainer _unit, backpackContainer _unit];

_amount - _left
