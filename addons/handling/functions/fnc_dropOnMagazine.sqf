#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Ammunition was dropped on a row of a list: if that row is a magazine of its caliber that takes this kind of round
 * (fnc_loadRule), loading starts; loose rounds, stripper clips and packs go into magazines, belts into belt magazines. The list
 * only says the magazine's class, so its rounds come from the cargo, by its place among the rows of that class; when
 * that one is full, the fullest one with room takes its place. The inventory closes and the same action as from the
 * ACE menu takes over: the hold action, or the progress bar when "Hold to load" is off.
 *
 * Arguments:
 * 0: The list <CONTROL>
 * 1: The row dropped on <NUMBER>
 * 2: The dragged item <STRING>
 *
 * Return Value:
 * Whether loading starts <BOOL>
 *
 * Example:
 * [_list, 4, "gmr_round_556x45_basic"] call gmr_handling_fnc_dropOnMagazine;
 *
 * Public: No
 */

params [["_list", controlNull, [controlNull]], ["_row", -1, [0]], ["_item", "", [""]]];

private _class = _list lbData _row;
private _config = configFile >> "CfgMagazines" >> _class;

if (!isClass _config) exitWith {false};

private _unit = PLAYER_UNIT;
private _magazine = [_class] call EFUNC(main,magazineInfo);
private _facts = [_item] call EFUNC(main,itemInfo);
private _capacity = _magazine select MAG_CAPACITY;

private _isBelt = (_facts select ITEM_KIND) == "belt";
private _fits = (_magazine select MAG_OK)
    && {(_facts select ITEM_CALIBER) in [_magazine select MAG_CALIBER, ["", "universal"] select EGVAR(main,universalAmmo)]}
    && {_isBelt isEqualTo (_magazine select MAG_BELT)};

if (!_fits) exitWith {
    hintSilent LLSTRING(Hint_WrongAmmo);
    PLAY_SOUND(denied);
    false
};

private _container = switch (ctrlIDC _list) do {
    case IDC_LIST_UNIFORM: {uniformContainer _unit};
    case IDC_LIST_VEST: {vestContainer _unit};
    default {backpackContainer _unit};
};

private _rounds = ((magazinesAmmoCargo _container) select {(_x select 0) == _class}) apply {_x select 1};
private _place = 0;

for "_i" from 0 to (_row - 1) do {
    if ((_list lbData _i) == _class) then {
        _place = _place + 1;
    };
};

private _amount = _rounds param [_place, _capacity];

if (_amount >= _capacity) then {
    private _open = _rounds select {_x < _capacity};

    _open sort false;
    _amount = _open param [0, _capacity];
};

if (_amount >= _capacity) exitWith {
    PLAY_SOUND(denied);
    false
};

private _closed = false;
private _ammunition = [_facts select ITEM_ROUND, _facts select ITEM_BELT_TYPE] select _isBelt;

// A carton of stripper clips holds clips: it loads their rounds. A clip itself loads as its rounds (fnc_takeRounds).
private _inside = [_ammunition] call EFUNC(main,itemInfo);

if (!_isBelt && {(_inside select ITEM_KIND) == "clip"}) then {
    _ammunition = _inside select ITEM_ROUND;
};
private _why = ([_class, _amount, _ammunition] call FUNC(loadRule)) select 1;

if (_why isNotEqualTo "") exitWith {
    hintSilent _why;
    PLAY_SOUND(denied);
    false
};

if ((_facts select ITEM_KIND) == "pack") then {
    if (EGVAR(main,packsMustOpen)) exitWith {
        _closed = true;
    };

    [_unit, _item, true] call FUNC(unpack);
};

if (_closed) exitWith {
    hintSilent LLSTRING(Hint_OpenPack);
    PLAY_SOUND(denied);
    false
};

PLAY_SOUND(drop_item);
closeDialog 0;

[
    {
        params ["_unit", "_class", "_amount", "_ammunition"];

        [_unit, "fill", _class, [_amount], _ammunition] call FUNC(start);
    },
    [_unit, _class, _amount, _ammunition]
] call CBA_fnc_execNextFrame;

true
