#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Moves the ammunition tab of ACE Arsenal directly below its two magazine tabs, and everything that came after them one
 * place down. ACE only offers places below its fixed tabs, and sets the last tab's place again each time, so this runs
 * each time the panel opens. The other mods' tabs keep their order.
 *
 * Arguments:
 * 0: The arsenal display <DISPLAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_display] call gmr_compat_ace_fnc_arrangeArsenal;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]]];

if (isNull _display || {GVAR(arsenalSlot) < 0}) exitWith {};

private _start = (ctrlPosition (_display displayCtrl ARSENAL_BUTTON_MAG_ALL)) select 1;
private _step = _start - ((ctrlPosition (_display displayCtrl ARSENAL_BUTTON_MAG)) select 1);

// Pairs of a button and its background, in the order they come below the magazines.
private _order = [[61 + GVAR(arsenalSlot) * 2, 60 + GVAR(arsenalSlot) * 2], [ARSENAL_BUTTON_THROW, ARSENAL_BUTTON_THROW - 1], [ARSENAL_BUTTON_PUT, ARSENAL_BUTTON_PUT - 1]];

for "_slot" from 0 to 9 do {
    if (_slot != GVAR(arsenalSlot) && {!isNull (_display displayCtrl (61 + _slot * 2))}) then {
        _order pushBack [61 + _slot * 2, 60 + _slot * 2];
    };
};

_order pushBack [ARSENAL_BUTTON_MISC, ARSENAL_BUTTON_MISC - 1];

{
    private _y = _start + _step * (_forEachIndex + 1);

    {
        private _control = _display displayCtrl _x;

        if (!isNull _control) then {
            _control ctrlSetPositionY _y;
            _control ctrlCommit 0;
        };
    } forEach _x;
} forEach _order;

nil
