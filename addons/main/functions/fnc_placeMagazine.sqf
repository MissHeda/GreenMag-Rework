#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts one magazine with exact rounds into a unit's inventory. A given container comes first and takes it whatever
 * its load (the magazine just left it); otherwise the first container with room, the setting's choice first. What
 * fits nowhere goes on the ground, so a magazine is never lost to a full inventory. The cargo is read back: an empty
 * magazine the cargo command refuses goes in through addMagazine.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Magazine class <STRING>
 * 2: Rounds <NUMBER>
 * 3: Container to put it in (optional, default: objNull) <OBJECT>
 *
 * Return Value:
 * Whether it is in the inventory rather than on the ground <BOOL>
 *
 * Example:
 * [player, "30Rnd_556x45_Stanag", 0] call gmr_main_fnc_placeMagazine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_rounds", 0, [0]], ["_into", objNull, [objNull]]];

private _fnc_held = {
    {(_x select 0) == _class && {(_x select 1) == _rounds}} count (magazinesAmmoCargo _this)
};

private _fnc_put = {
    private _held = _this call _fnc_held;

    _this addMagazineAmmoCargo [_class, 1, _rounds];

    (_this call _fnc_held) > _held
};

if (!isNull _into && {_into call _fnc_put}) exitWith {true};

private _mass = getNumber (configFile >> "CfgMagazines" >> _class >> "mass");
private _spots = [
    [uniformContainer _unit, loadUniform _unit],
    [vestContainer _unit, loadVest _unit],
    [backpackContainer _unit, loadBackpack _unit]
];

// The setting's container first: 0 automatic, 1 uniform, 2 vest, 3 backpack.
private _first = (missionNamespace getVariable [QGVAR(emptyContainer), 0]) - 1;

if (_rounds == 0 && {_first >= 0}) then {
    _spots = [_spots select _first] + (_spots - [_spots select _first]);
};

private _placed = false;

{
    _x params ["_container", "_load"];

    if (!isNull _container && {(1 - _load) * getNumber (configOf _container >> "maximumLoad") >= _mass} && {_container call _fnc_put}) exitWith {
        _placed = true;
    };
} forEach _spots;

// The cargo command may not take a magazine without rounds; the unit's own may, where there is room.
if (!_placed && {_rounds == 0}) then {
    private _before = {(_x select 0) == _class && {(_x select 1) == 0}} count (magazinesAmmoFull _unit);

    _unit addMagazine [_class, 0];
    _placed = ({(_x select 0) == _class && {(_x select 1) == 0}} count (magazinesAmmoFull _unit)) > _before;
};

if (!_placed) then {
    [_unit, _class, 1, _rounds] call FUNC(dropOnGround);
};

_placed
