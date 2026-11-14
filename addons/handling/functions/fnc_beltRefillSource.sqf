#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * What a belt item can be refilled with: rounds of its own kind, or universal rounds while universal ammunition is on.
 * With a dragged item that one decides (loose rounds and packs load loose, clips and cartons of clips load clips); without
 * one (menus) the belt's own rounds come first, universal ones only when there are none of its own.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: The belt item <STRING>
 * 2: The dragged item, "" from a menu <STRING>
 *
 * Return Value:
 * [Round class ("" when nothing fits), "loose", "clips" or "mixed", Reason when nothing fits] <ARRAY>
 *
 * Example:
 * [player, "gmr_belt_762x51_basic100", "gmr_round_762x51_basic"] call gmr_handling_fnc_beltRefillSource;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_belt", "", [""]], ["_item", "", [""]]];

private _facts = [_belt] call EFUNC(main,itemInfo);

if ((_facts select ITEM_KIND) != "belt") exitWith {["", "mixed", LLSTRING(Hint_WrongAmmo)]};
if ((_facts select ITEM_ROUNDS) >= BELT_MAX) exitWith {["", "mixed", LLSTRING(Hint_BeltFull)]};

private _own = _facts select ITEM_ROUND;
private _allowed = [_own];

if (EGVAR(main,universalAmmo) && {_own != UNIVERSAL_ROUND}) then {
    _allowed pushBack UNIVERSAL_ROUND;
};

if (_item isNotEqualTo "") exitWith {
    private _dragged = [_item] call EFUNC(main,itemInfo);
    private _kind = _dragged select ITEM_KIND;

    if !(_kind in ["round", "clip", "pack"]) exitWith {["", "mixed", LLSTRING(Hint_WrongAmmo)]};

    private _round = _dragged select ITEM_ROUND;
    private _from = ["loose", "clips"] select (_kind == "clip");

    // A carton of clips holds clips: their rounds load.
    private _inside = [_round] call EFUNC(main,itemInfo);

    if ((_inside select ITEM_KIND) == "clip") then {
        _round = _inside select ITEM_ROUND;
        _from = "clips";
    };

    if !(_round in _allowed) exitWith {["", "mixed", LLSTRING(Hint_WrongAmmo)]};

    [_round, _from, ""]
};

private _counts = [_unit] call EFUNC(main,itemCounts);
private _found = _allowed findIf {
    (_counts getOrDefault [_x, 0]) > 0 || {[_unit, _x] call FUNC(clipsOf) isNotEqualTo []}
};

if (_found < 0) exitWith {["", "mixed", LLSTRING(Hint_WrongAmmo)]};

[_allowed select _found, "mixed", ""]
