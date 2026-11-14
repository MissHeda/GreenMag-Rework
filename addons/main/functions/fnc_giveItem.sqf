#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Gives a unit items: as many as each container has room for by its own load, the rest on the ground. The room is
 * worked out per container because canAdd also refuses a unit over its total load, with plenty of room in its bags. A
 * container asked for fills first, what has no room there goes on to the others.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Item class <STRING>
 * 2: How many <NUMBER>
 * 3: The container to fill first (optional, default: objNull) <OBJECT>
 *
 * Return Value:
 * How many ended up on the ground <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30] call gmr_main_fnc_giveItem;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_amount", 0, [0]], ["_first", objNull, [objNull]]];

if (_amount <= 0) exitWith {0};

// Unless told otherwise, the container the player's last action was made in comes first (inventory context menu or drag).
if (isNull _first) then {
    _first = missionNamespace getVariable [QGVAR(preferContainer), objNull];
};

private _mass = (([_class] call FUNC(itemInfo)) select ITEM_MASS) max 0.001;
private _left = _amount;
private _containers = [
    [uniformContainer _unit, loadUniform _unit],
    [vestContainer _unit, loadVest _unit],
    [backpackContainer _unit, loadBackpack _unit]
];

_containers = (_containers select {(_x select 0) isEqualTo _first}) + (_containers select {(_x select 0) isNotEqualTo _first});

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
} forEach _containers;

if (_left > 0) then {
    [_unit, _class, _left] call FUNC(dropOnGround);
};

_left
