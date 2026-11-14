#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes one of this mod's items out of the pouches and kits a unit carries, pouch by pouch. The new contents go through
 * the framework's own setter, which tells every machine.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Item class <STRING>
 * 2: How many <NUMBER>
 *
 * Return Value:
 * How many it took <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30] call gmr_compat_eup_fnc_kitRemove;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_amount", 0, [0]]];

if (_amount <= 0 || {(([_class] call EFUNC(main,itemInfo)) select ITEM_KIND) isEqualTo ""}) exitWith {0};

private _left = _amount;

{
    if (_left <= 0) exitWith {};

    private _kit = _x;
    private _contents = [_kit] call efak_core_fnc_getContents;
    private _changed = false;

    {
        _x params ["_item", "_held"];

        // Class names compare without regard to case in SQF.
        if (_left > 0 && {_item == _class}) then {
            private _take = _left min _held;

            _x set [1, _held - _take];
            _left = _left - _take;
            _changed = true;
        };
    } forEach _contents;

    if (_changed) then {
        [_kit, _contents select {(_x select 1) > 0}] call efak_core_fnc_setContents;
    };
} forEach ([_unit] call efak_core_fnc_getCarriedKits);

_amount - _left
