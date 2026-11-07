#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes rounds of one kind out of the inventory, loose ones and those on stripper clips of that kind. With clipsFirst
 * (loading with the speedloader) whole clips go first and loose rounds fill up the rest; else the loose rounds go first.
 * A clip is only ever used whole: whatever is left on the last one it needed comes back as loose rounds.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Round class <STRING>
 * 2: Rounds wanted <NUMBER>
 * 3: Clips first (optional, default: false) <BOOL>
 *
 * Return Value:
 * Rounds taken, at most those wanted <NUMBER>
 *
 * Example:
 * [player, "gmr_round_556x45_basic", 30, true] call gmr_handling_fnc_takeRounds;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_round", "", [""]], ["_wanted", 0, [0]], ["_clipsFirst", false, [false]]];

if (_wanted <= 0) exitWith {0};

private _clips = [_unit, _round] call FUNC(clipsOf);
private _taken = 0;

// Whole clips that fit in what is wanted, largest first.
private _fnc_wholeClips = {
    {
        _x params ["_clip", "_count", "_per"];

        private _want = floor ((_wanted - _taken) / _per) min _count;

        if (_want > 0) then {
            _taken = _taken + _per * ([_unit, _clip, _want] call EFUNC(main,removeItem));
        };
    } forEach _clips;
};

if (_clipsFirst) then {
    call _fnc_wholeClips;
};

if (_taken < _wanted) then {
    _taken = _taken + ([_unit, _round, _wanted - _taken] call EFUNC(main,removeItem));
};

if (!_clipsFirst) then {
    call _fnc_wholeClips;
};

// What is still missing comes off one more clip; the rest of it stays loose.
if (_taken < _wanted) then {
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
};

_taken
