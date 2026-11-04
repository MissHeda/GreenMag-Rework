#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Gives a unit items: as many as each container has room for by its own load, the rest on the ground. The room is
 * worked out per container because canAdd also refuses a unit over its total load, with plenty of room in its bags.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Item class <STRING>
 * 2: How many <NUMBER>
 *
 * Return Value:
 * How many ended up on the ground <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30] call gmr_main_fnc_giveItem;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_amount", 0, [0]]];

if (_amount <= 0) exitWith {0};

private _mass = (([_class] call FUNC(itemInfo)) select ITEM_MASS) max 0.001;
private _left = _amount;

{
    _x params ["_container", "_load"];

    if (_left <= 0) exitWith {};

    if (!isNull _container) then {
        private _capacity = getNumber (configOf _container >> "maximumLoad");
        private _fits = floor (((1 - _load) * _capacity) / _mass + 0.001);
        private _put = _left min _fits;

        if (_put > 0) then {
            _container addItemCargoGlobal [_class, _put];
            _left = _left - _put;
        };
    };
} forEach [
    [uniformContainer _unit, loadUniform _unit],
    [vestContainer _unit, loadVest _unit],
    [backpackContainer _unit, loadBackpack _unit]
];

if (_left > 0) then {
    [_unit, _class, _left] call FUNC(dropOnGround);
};

_left
