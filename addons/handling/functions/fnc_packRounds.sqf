#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Packs a unit's loose rounds of one kind into the largest of its caliber's packs they fill. What fills no pack stays loose.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Round class <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "gmr_round_556x45_basic"] call gmr_handling_fnc_packRounds;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_round", "", [""]]];

private _facts = [_round] call EFUNC(main,itemInfo);
private _have = ([_unit] call EFUNC(main,itemCounts)) getOrDefault [_round, 0];
private _sizes = [_facts select ITEM_CALIBER] call EFUNC(main,packSizes);
private _packed = 0;
private _rest = _have;

{
    _packed = _packed + (_rest - (_rest % _x));
    _rest = _rest % _x;
} forEach _sizes;

private _left = [_unit, _round, _packed] call EFUNC(main,removeItem);
private _dropped = 0;

{
    private _packs = floor (_left / _x);

    if (_packs > 0) then {
        _dropped = _dropped + ([
            _unit,
            format ["gmr_pack_%1_%2_%3", _facts select ITEM_CALIBER, _facts select ITEM_VARIANT, _x],
            _packs
        ] call EFUNC(main,giveItem));

        _left = _left - _packs * _x;
    };
} forEach _sizes;

if (_packed > 0) then {
    PLAY_SOUND(pack_close);
};

if (_dropped > 0) then {
    hintSilent LLSTRING(Hint_Ground);
};

nil
