#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes rounds of one kind out of the inventory, from where the loading was set up to take them (fnc_start):
 * "loose" only loose rounds, "clips" only rounds on stripper clips, "mixed" loose rounds first and then clips.
 * A clip is only ever used whole: whatever is left on the last one it needed comes back as loose rounds.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Round class <STRING>
 * 2: Rounds wanted <NUMBER>
 * 3: "loose", "clips" or "mixed" (optional, default: "mixed") <STRING>
 *
 * Return Value:
 * Rounds taken, at most those wanted <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30, "clips"] call gmr_handling_fnc_takeRounds;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_round", "", [""]], ["_wanted", 0, [0]], ["_from", "mixed", [""]]];

if (_wanted <= 0) exitWith {0};

private _taken = 0;

if (_from != "clips") then {
    _taken = [_unit, _round, _wanted] call EFUNC(main,removeItem);
};

if (_from == "loose" || {_taken >= _wanted}) exitWith {_taken};

private _clips = [_unit, _round] call FUNC(clipsOf);

// Whole clips that fit in what is still wanted, the fullest first.
{
    _x params ["_clip", "_count", "_per"];

    private _want = floor ((_wanted - _taken) / _per) min _count;

    if (_want > 0) then {
        _taken = _taken + _per * ([_unit, _clip, _want] call EFUNC(main,removeItem));
    };
} forEach _clips;

// What is still missing comes off one more clip; the rest of it stays loose.
{
    _x params ["_clip", "", "_per"];

    if (_taken < _wanted && {[_unit, _clip, 1] call EFUNC(main,removeItem) == 1}) then {
        private _use = _per min (_wanted - _taken);

        _taken = _taken + _use;

        if (_per > _use) then {
            [_unit, _round, _per - _use] call EFUNC(main,giveItem);
        };
    };
} forEach _clips;

_taken
