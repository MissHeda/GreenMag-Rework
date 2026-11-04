#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes one exact magazine, by its class and rounds, out of the unit's uniform, vest or backpack. All other magazines
 * of the class stay untouched where they are - nothing is ever removed and added back wholesale. The cargo is read
 * before and after, so a magazine that did not leave counts as not taken.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Magazine class <STRING>
 * 2: Rounds <NUMBER>
 *
 * Return Value:
 * The container it was in, objNull when no such magazine is there <OBJECT>
 *
 * Example:
 * [player, "30Rnd_556x45_Stanag", 12] call gmr_main_fnc_takeMagazine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]], ["_rounds", 0, [0]]];

private _fnc_held = {
    {(_x select 0) == _class && {(_x select 1) == _rounds}} count (magazinesAmmoCargo _this)
};

private _from = objNull;

{
    if (!isNull _x) then {
        private _held = _x call _fnc_held;

        if (_held > 0) exitWith {
            _x addMagazineAmmoCargo [_class, -1, _rounds];

            if ((_x call _fnc_held) == _held - 1) then {
                _from = _x;
            };
        };
    };

    if (!isNull _from) exitWith {};
} forEach [uniformContainer _unit, vestContainer _unit, backpackContainer _unit];

_from
