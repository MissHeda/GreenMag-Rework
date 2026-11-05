#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The shown list of the unit's own containers under a screen position, and the row there. The rows' height is the
 * one the game's inventory gives its lists; the scrollbar says how far the list is scrolled.
 *
 * Arguments:
 * 0: The inventory display <DISPLAY>
 * 1: Screen position <ARRAY>
 *
 * Return Value:
 * [list, row]; [controlNull, -1] when none is there <ARRAY>
 *
 * Example:
 * [_display, getMousePosition] call gmr_handling_fnc_listRowAt;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]], ["_mouse", [0, 0], [[]]]];

_mouse params ["_mouseX", "_mouseY"];

private _rowHeight = 2 * (((safezoneW / safezoneH) min 1.2) / 1.2 / 25);
private _result = [controlNull, -1];

{
    private _list = _display displayCtrl _x;

    if (!isNull _list && {ctrlShown _list}) then {
        (ctrlPosition _list) params ["_x0", "_y0", "_width", "_height"];

        if (_mouseX >= _x0 && {_mouseX <= _x0 + _width} && {_mouseY >= _y0} && {_mouseY <= _y0 + _height}) exitWith {
            private _visible = floor (_height / _rowHeight);
            private _hidden = (lbSize _list - _visible) max 0;
            private _top = round (((ctrlScrollValues _list select 0) max 0) * _hidden);
            private _row = _top + floor ((_mouseY - _y0) / _rowHeight);

            _result = [_list, [-1, _row] select (_row < lbSize _list)];
        };
    };
} forEach [IDC_LIST_UNIFORM, IDC_LIST_VEST, IDC_LIST_BACKPACK];

_result
