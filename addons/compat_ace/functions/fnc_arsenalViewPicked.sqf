#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The player picked an entry of ACE Arsenal's sort list in the ammunition tab: one of this mod's views, or one of ACE's
 * sorts, which shows everything. A different view fills the panel again, the next frame, after ACE's own sorting.
 *
 * Arguments:
 * 0: The sort list <CONTROL>
 * 1: The picked row <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_control, 0] call gmr_compat_ace_fnc_arsenalViewPicked;
 *
 * Public: No
 */

params ["_control", "_row"];

private _display = ctrlParent _control;
private _button = 61 + GVAR(arsenalSlot) * 2;

if (GVAR(viewsBusy) || {focusedCtrl _display != _control} || {missionNamespace getVariable ["ace_arsenal_currentRightPanel", -1] != _button}) exitWith {};

private _data = _control lbData _row;
private _view = if (_data find "gmr_view_" == 0) then {_data select [9]} else {"all"};

if (_view == GVAR(arsenalView)) exitWith {};

GVAR(arsenalView) = _view;

[{
    params ["_display", "_button"];

    if (isNull _display) exitWith {};

    GVAR(viewsBusy) = true;
    [_display, _display displayCtrl _button, false] call ace_arsenal_fnc_fillRightPanel;
    GVAR(viewsBusy) = false;
}, [_display, _button]] call CBA_fnc_execNextFrame;

nil
