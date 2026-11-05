#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * An inventory context menu's "Refill" or "Unload" on a magazine. The menu only says the class, so of those in that
 * container it takes the fullest with room to refill and the emptiest with rounds to unload. The inventory closes and
 * the same action as everywhere takes over.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Container <OBJECT>
 * 2: Magazine class <STRING>
 * 3: "fill" or "unload" <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, uniformContainer player, "30Rnd_556x45_Stanag", "fill"] call gmr_handling_fnc_contextMagazine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_container", objNull, [objNull]], ["_class", "", [""]], ["_kind", "fill", [""]]];

private _capacity = ([_class] call EFUNC(main,magazineInfo)) select MAG_CAPACITY;
private _rounds = ((magazinesAmmoCargo _container) select {(_x select 0) == _class}) apply {_x select 1};

_rounds = _rounds select {[_x > 0, _x < _capacity] select (_kind == "fill")};
_rounds sort (_kind != "fill");

if (_rounds isEqualTo []) exitWith {};

closeDialog 0;

[
    {
        params ["_unit", "_kind", "_class", "_amount"];

        [_unit, _kind, _class, [_amount]] call FUNC(start);
    },
    [_unit, _kind, _class, _rounds select 0]
] call CBA_fnc_execNextFrame;

nil
