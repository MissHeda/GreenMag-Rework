#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * After the player's reload: an empty magazine goes back into the inventory, unless something already put one there.
 * A partly used magazine is only ever put back when the inventory shows exactly the signature of the game having lost
 * it: compared to the picture from before, the magazine now in the weapon is missing, and nothing else changed at all.
 * Anything else - a magazine picked up, given away, moved by another mod - and it stays as it is, so the guard can
 * miss a lost magazine in a busy moment but cannot make one out of nothing. Every repair is logged.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: New magazine, [class, rounds] <ARRAY>
 * 2: Old magazine, [class, rounds] <ARRAY>
 * 3: The picture from before the reload <HASHMAP>
 * 4: Whether that picture is of this unit <BOOL>
 *
 * Return Value:
 * Whether a magazine was put in <BOOL>
 *
 * Example:
 * [player, ["30Rnd_65x39_caseless_mag", 30], ["30Rnd_65x39_caseless_mag", 12], _picture, true] call gmr_guard_fnc_checkReload;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_new", [], [[]]], ["_old", [], [[]]], ["_before", createHashMap, [createHashMap]], ["_known", false, [false]]];

_old params ["_class", "_rounds"];

if (!alive _unit) exitWith {false};

// As the picture keeps them.
private _oldKey = [toLowerANSI _class, _rounds];
private _newKey = [toLowerANSI (_new select 0), _new select 1];

private _now = [_unit] call FUNC(snapshot);
private _result = false;

if (_rounds == 0) then {
    if (
        EGVAR(main,keepEmpties)
        && {([_class] call EFUNC(main,magazineInfo)) select MAG_OK}
        && {(_now getOrDefault [_oldKey, 0]) <= (_before getOrDefault [_oldKey, 0])}
    ) then {
        [_unit, _class, 0] call EFUNC(main,placeMagazine);
        _result = true;
    };
} else {
    if (EGVAR(main,reloadGuard) && {_known}) then {
        private _gone = [];
        private _came = [];

        {
            private _difference = _y - (_now getOrDefault [_x, 0]);

            for "_i" from 1 to _difference do {
                _gone pushBack _x;
            };
        } forEach _before;

        {
            private _difference = _y - (_before getOrDefault [_x, 0]);

            for "_i" from 1 to _difference do {
                _came pushBack _x;
            };
        } forEach _now;

        if (_came isEqualTo [] && {_gone isEqualTo [_newKey]}) then {
            private _inside = [_unit, _class, _rounds] call EFUNC(main,placeMagazine);

            INFO_3("Reload guard put back %1 with %2 rounds (in inventory: %3).",_class,_rounds,_inside);

            if (EGVAR(main,guardNotice)) then {
                systemChat format [LLSTRING(Restored), ([_class] call EFUNC(main,magazineInfo)) select MAG_NAME, _rounds];
            };

            _result = true;
        };
    };
};

GVAR(picture) = [_unit, [_unit] call FUNC(snapshot)];

_result
