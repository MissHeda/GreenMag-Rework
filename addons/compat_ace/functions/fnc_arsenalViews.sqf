#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts this mod's views at the top of ACE Arsenal's sort list while the ammunition tab is open: only the ammunition the
 * unit's weapons take (the default), only rounds, only packs, only belts; the speedloader shows in each. ACE's own sorts
 * below them show everything.
 * Then takes out of the list what the chosen view does not show.
 *
 * ACE fills the sort list anew with every fill of the panel, so this runs after each one. Picking a view fills the
 * panel again (fnc_arsenalViewPicked), as rows taken out cannot come back otherwise.
 *
 * Arguments:
 * 0: The arsenal display <DISPLAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_display] call gmr_compat_ace_fnc_arsenalViews;
 *
 * Public: No
 */

params [["_display", displayNull, [displayNull]]];

private _list = _display displayCtrl ARSENAL_ITEM_LIST;

if (isNull _list) exitWith {};

// ACE fills its sort list after this event, so the views go in on the next frame. Selecting one there must neither sort
// again nor count as the player's pick.
[{
    params ["_display"];

    private _sort = _display displayCtrl ARSENAL_SORT;

    if (isNull _sort || {missionNamespace getVariable ["ace_arsenal_currentRightPanel", -1] != 61 + GVAR(arsenalSlot) * 2}) exitWith {};

    GVAR(viewsBusy) = true;

    private _current = _sort lbData (0 max lbCurSel _sort);
    private _theirs = [];

    for "_i" from 0 to (lbSize _sort) - 1 do {
        private _data = _sort lbData _i;

        if (_data find "gmr_view_" != 0) then {
            _theirs pushBack [_sort lbText _i, _data];
        };
    };

    lbClear _sort;

    {
        _x params ["_id", "_name"];

        private _index = _sort lbAdd _name;
        _sort lbSetData [_index, "gmr_view_" + _id];
        _sort lbSetColor [_index, ARSENAL_FITS_COLOR];
    } forEach [
        ["fitting", LLSTRING(View_Fitting)],
        ["round", LLSTRING(View_Rounds)],
        ["pack", LLSTRING(View_Packs)],
        ["belt", LLSTRING(View_Belts)]
    ];

    {
        _x params ["_name", "_data"];

        private _index = _sort lbAdd _name;
        _sort lbSetData [_index, _data];
    } forEach _theirs;

    private _want = ["gmr_view_" + GVAR(arsenalView), _current] select (GVAR(arsenalView) == "all");
    private _at = 0;

    for "_i" from 0 to (lbSize _sort) - 1 do {
        if ((_sort lbData _i) == _want) exitWith {
            _at = _i;
        };
    };

    ace_arsenal_ignoreFirstSortPanelCall = true;
    _sort lbSetCurSel _at;
    ace_arsenal_ignoreFirstSortPanelCall = false;
    GVAR(viewsBusy) = false;

    // The player's pick is told apart from ACE filling the list by where the focus is: on the list only when picked.
    if !(_display getVariable [QGVAR(viewsHandler), false]) then {
        _display setVariable [QGVAR(viewsHandler), true];
        _sort ctrlAddEventHandler ["LBSelChanged", {call FUNC(arsenalViewPicked)}];
    };
}, [_display]] call CBA_fnc_execNextFrame;

if (GVAR(arsenalView) == "all") exitWith {};

private _fitting = if (GVAR(arsenalView) == "fitting") then {call FUNC(arsenalFits)} else {[]};

// The mod's tools (the speedloader) show in every view; among the fitting ammunition only while a weapon takes a caliber
// that comes on stripper clips.
private _toolsFit = _fitting isEqualTo [] || {
    (keys (_fitting select 0)) findIf {isClass (configFile >> "CfgWeapons" >> format ["gmr_clip_%1_basic", _x])} >= 0
};

for "_row" from ((lnbSize _list) select 0) - 1 to 0 step -1 do {
    private _item = _list lnbData [_row, 0];

    if (toLowerANSI _item find "gmr_" == 0) then {
        private _facts = [_item] call EFUNC(main,itemInfo);
        private _kind = _facts select ITEM_KIND;

        // Stripper clips show with the packs.
        if (_kind == "clip") then {
            _kind = "pack";
        };

        private _shown = switch (true) do {
            case (_kind == ""): {_toolsFit};
            case (_fitting isEqualTo []): {_kind == GVAR(arsenalView)};
            default {((_fitting select ([0, 1] select (_kind == "belt"))) getOrDefault [_facts select ITEM_CALIBER, false])};
        };

        if (!_shown) then {
            _list lnbDeleteRow _row;
        };
    };
};

nil
