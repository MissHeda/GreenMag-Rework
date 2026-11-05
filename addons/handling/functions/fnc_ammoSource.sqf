#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * What a magazine is refilled from when nothing was chosen: its own kind of round if the unit has any, else whichever
 * kind of the same caliber it has most of, else universal ammunition. For a belt magazine, the same among the belts.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Magazine class <STRING>
 *
 * Return Value:
 * Round class or belt type, the magazine's own kind when the unit has none of the caliber <STRING>
 *
 * Example:
 * [player, "30Rnd_556x45_Stanag"] call gmr_handling_fnc_ammoSource;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_class", "", [""]]];

private _magazine = [_class] call EFUNC(main,magazineInfo);
private _belt = _magazine select MAG_BELT;
private _caliber = _magazine select MAG_CALIBER;
private _own = [_magazine select MAG_ROUND, _magazine select MAG_BELT_TYPE] select _belt;
private _universal = [UNIVERSAL_ROUND, UNIVERSAL_BELT] select _belt;
private _found = createHashMap;
private _hasUniversal = false;

{
    private _facts = [_x] call EFUNC(main,itemInfo);

    if ((_facts select ITEM_KIND) == (["round", "belt"] select _belt)) then {
        private _key = [_x, _facts select ITEM_BELT_TYPE] select _belt;

        if (_key == _universal) then {
            _hasUniversal = true;
        };

        if ((_facts select ITEM_CALIBER) == _caliber) then {
            private _rounds = [_y, _y * (_facts select ITEM_ROUNDS)] select _belt;

            _found set [_key, (_found getOrDefault [_key, 0]) + _rounds];
        };
    };
} forEach ([_unit] call EFUNC(main,itemCounts));

if (_own in _found) exitWith {_own};

private _best = [_own, _universal] select _hasUniversal;
private _most = 0;

{
    if (_y > _most) then {
        _best = _x;
        _most = _y;
    };
} forEach _found;

_best
