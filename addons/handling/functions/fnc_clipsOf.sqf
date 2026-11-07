#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The stripper clips of one kind of round the unit carries.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Round class <STRING>
 *
 * Return Value:
 * [clip class, clips, rounds on one] each, the fullest clips first <ARRAY>
 *
 * Example:
 * [player, "gmr_round_556x45_basic"] call gmr_handling_fnc_clipsOf;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_round", "", [""]]];

private _clips = [];

{
    private _facts = [_x] call EFUNC(main,itemInfo);

    if ((_facts select ITEM_KIND) == "clip" && {(_facts select ITEM_ROUND) == _round}) then {
        _clips pushBack [_facts select ITEM_ROUNDS, _x, _y];
    };
} forEach ([_unit] call EFUNC(main,itemCounts));

_clips sort false;
_clips apply {[_x select 1, _x select 2, _x select 0]}
