#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts what does not fit anywhere near the unit: the vehicle it sits in, else a scripted ground holder (which the
 * engine does not delete as empty), one within two metres being reused.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Item class, or magazine class when the rounds are given <STRING>
 * 2: How many items <NUMBER>
 * 3: Rounds of the magazine, -1 for an item (optional, default: -1) <NUMBER>
 *
 * Return Value:
 * The holder <OBJECT>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 5] call gmr_main_fnc_dropOnGround;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_amount", 1, [0]], ["_rounds", -1, [0]]];

private _holder = objectParent _unit;

if (isNull _holder) then {
    _holder = (nearestObjects [_unit, ["GroundWeaponHolder_Scripted"], 2]) param [0, objNull];
};

if (isNull _holder) then {
    _holder = createVehicle ["GroundWeaponHolder_Scripted", getPosATL _unit, [], 0, "CAN_COLLIDE"];
};

if (_rounds < 0) then {
    _holder addItemCargoGlobal [_class, _amount];
} else {
    _holder addMagazineAmmoCargo [_class, _amount, _rounds];
};

_holder
