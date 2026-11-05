#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The inventory opened: watches the mouse while it stays open, so ammunition can be dragged onto a magazine. The
 * button is read directly, because the engine keeps a drag inside one list to itself.
 *
 * Arguments:
 * 0: The inventory display <DISPLAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_display] call gmr_handling_fnc_onInventoryLoad;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]]];

uiNamespace setVariable [QGVAR(dragDisplay), _display];
GVAR(dragStart) = [];
GVAR(dragDown) = false;

if (GVAR(dragWatch) < 0) then {
    GVAR(dragWatch) = [FUNC(watchDrag), 0] call CBA_fnc_addPerFrameHandler;
};

nil
