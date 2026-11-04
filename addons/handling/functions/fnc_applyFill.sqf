#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts the rounds into the magazines. The rounds are taken first, as far as they are still there; then each magazine
 * is swapped by itself, by its class and rounds, in the container it lies in. A magazine that is gone by now is left
 * out and its rounds come back. No other magazine is touched, so nothing that happened to the inventory since the
 * menu can be lost or doubled.
 *
 * Arguments:
 * 0: The operation (fnc_start) <HASHMAP>
 * 1: Rounds to move <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_op, 18] call gmr_handling_fnc_applyFill;
 *
 * Public: No
 */

params [["_op", createHashMap, [createHashMap]], ["_rounds", 0, [0]]];

private _unit = _op get "unit";
private _class = _op get "class";
private _source = _op get "source";
private _belt = _op get "belt";
private _free = EGVAR(main,freeRefill);
private _capacity = ([_class] call EFUNC(main,magazineInfo)) select MAG_CAPACITY;

private _left = switch (true) do {
    case (_free): {_rounds};
    case (_belt): {[_unit, _source, _rounds] call EFUNC(main,takeBelts)};
    default {[_unit, _source, _rounds] call EFUNC(main,removeItem)};
};

private _changed = false;

{
    private _load = (_capacity - _x) min _left;

    if (_load > 0) then {
        private _from = [_unit, _class, _x] call EFUNC(main,takeMagazine);

        if (isNull _from) then {
            _changed = true;
        } else {
            [_unit, _class, _x + _load, _from] call EFUNC(main,placeMagazine);
            _left = _left - _load;
        };
    };
} forEach (_op get "amounts");

if (_left > 0 && {!_free}) then {
    if (_belt) then {
        [_unit, _source, _left] call EFUNC(main,giveBelt);
    } else {
        [_unit, _source, _left] call EFUNC(main,giveItem);
    };
};

if (_changed) then {
    hintSilent LLSTRING(Hint_Changed);
};

nil
