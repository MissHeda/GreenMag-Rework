#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes the rounds out of the magazines, each swapped by itself in the container it lies in. Rounds of a magazine
 * come out loose, those of a belt magazine as a belt item. A magazine that is gone by now is left out.
 *
 * Arguments:
 * 0: The operation (fnc_start) <HASHMAP>
 * 1: Rounds to move <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_op, 18] call gmr_handling_fnc_applyUnload;
 *
 * Public: No
 */

params [["_op", createHashMap, [createHashMap]], ["_rounds", 0, [0]]];

private _unit = _op get "unit";
private _class = _op get "class";
private _source = _op get "source";
private _belt = _op get "belt";
private _left = _rounds;
private _loose = 0;
private _changed = false;

{
    private _out = _x min _left;

    if (_out > 0) then {
        private _from = [_unit, _class, _x] call EFUNC(main,takeMagazine);

        if (isNull _from) then {
            _changed = true;
        } else {
            private _now = _x - _out;

            if (_now > 0 || {EGVAR(main,keepEmpties)}) then {
                [_unit, _class, _now, _from] call EFUNC(main,placeMagazine);
            };

            _left = _left - _out;

            if (_belt) then {
                [_unit, _source, _out] call EFUNC(main,giveBelt);
            } else {
                _loose = _loose + _out;
            };
        };
    };
} forEach (_op get "amounts");

private _dropped = [_unit, _source, _loose] call EFUNC(main,giveItem);

switch (true) do {
    case (_changed): {hintSilent LLSTRING(Hint_Changed)};
    case (_dropped > 0): {hintSilent LLSTRING(Hint_Ground)};
};

nil
