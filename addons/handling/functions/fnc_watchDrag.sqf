#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Every frame while the inventory is open: notes the ammunition under the mouse when the left button goes down, and
 * when it comes up over another row of the same list, hands it to fnc_dropOnMagazine.
 *
 * Arguments:
 * Per-frame handler arguments, unused
 *
 * Return Value:
 * None
 *
 * Example:
 * [] call gmr_handling_fnc_watchDrag;
 *
 * Public: No
 */

private _display = uiNamespace getVariable [QGVAR(dragDisplay), displayNull];

if (isNull _display) exitWith {
    [GVAR(dragWatch)] call CBA_fnc_removePerFrameHandler;
    GVAR(dragWatch) = -1;
};

if (!EGVAR(main,dragToLoad) || {!EGVAR(main,enabled)}) exitWith {};

private _down = inputMouse 0 > 0;

if (_down isEqualTo GVAR(dragDown)) exitWith {};

GVAR(dragDown) = _down;

([_display, getMousePosition] call FUNC(listRowAt)) params ["_list", "_row"];

if (_down) exitWith {
    GVAR(dragStart) = [];

    if (_row >= 0) then {
        private _class = _list lbData _row;

        if (toLowerANSI _class find "gmr_" == 0 && {(([_class] call EFUNC(main,itemInfo)) select ITEM_KIND) in ["round", "pack", "belt"]}) then {
            GVAR(dragStart) = [_list, _row, _class];
        };
    };
};

GVAR(dragStart) params [["_startList", controlNull], ["_startRow", -1], ["_item", ""]];

GVAR(dragStart) = [];

if (_item isEqualTo "" || {_row < 0} || {_list isNotEqualTo _startList} || {_row == _startRow}) exitWith {};

[_list, _row, _item] call FUNC(dropOnMagazine);

nil
