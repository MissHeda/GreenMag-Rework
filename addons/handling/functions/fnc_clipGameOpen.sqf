#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens the stripper clip minigame: a window of its own, played with the mouse. The magazine stands cut open in the
 * middle, the speedloader's guide on top of it; the clip lies beside it. Dragged into the guide it seats, and the
 * rounds are pressed down out of it with the thumb, by its mark (fnc_clipGameTick plays it, fnc_uiClipGame draws it).
 * Esc closes the window and stops loading, what went in stays in.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_clipGameOpen;
 *
 * Public: No
 */

if (isNil QGVAR(op)) exitWith {};

private _display = (findDisplay 46) createDisplay "RscDisplayEmpty";

if (isNull _display) exitWith {};

// Closed by Esc (or anything else) while loading: it stops there.
_display displayAddEventHandler ["Unload", {
    if (!isNil QGVAR(op) && {GVAR(op) getOrDefault ["clipGame", false]}) then {
        [false] call FUNC(finish);
    };
}];

private _fnc_make = {
    params ["_class", "_x", "_y", "_w", "_h", ["_texture", ""], ["_colour", []]];

    private _control = _display ctrlCreate [_class, -1];

    _control ctrlSetPosition [_x, _y, _w, _h];

    if (_texture isNotEqualTo "") then {
        _control ctrlSetText _texture;
    };

    if (_colour isNotEqualTo []) then {
        if (_class == "RscText") then {
            _control ctrlSetBackgroundColor _colour;
        } else {
            _control ctrlSetTextColor _colour;
        };
    };

    _control ctrlCommit 0;
    _control
};

private _per = GVAR(op) getOrDefault ["clipSize", 10];
private _roundH = CG_ROUND_HEIGHT;
private _roundW = CG_ROUND_WIDTH;
private _width = CG_WIDTH;
private _height = CG_HEIGHT;
private _x0 = safeZoneX + (safeZoneW - _width) / 2;
private _y0 = safeZoneY + safeZoneH * CG_TOP;

[_display, [_x0, _y0, _width, _height], UI_PANEL_COLOR, UI_RADIUS] call FUNC(uiPanel);

private _title = ["RscStructuredText", _x0 + UI_PAD, _y0 + UI_PAD - 0.004, _width - UI_PAD * 2, 0.034] call _fnc_make;
_title ctrlSetStructuredText parseText format ["<t size='0.85' color='#c9ced6' font='PuristaMedium'>%1</t>", GVAR(op) get "title"];

private _count = ["RscStructuredText", _x0 + UI_PAD, _y0 + UI_PAD + 0.026, _width - UI_PAD * 2, 0.04] call _fnc_make;
private _combo = ["RscStructuredText", _x0 + UI_PAD, _y0 + UI_PAD + 0.03, _width - UI_PAD * 2, 0.036] call _fnc_make;

// The magazine, cut open: its walls, its floor, the feed lips, and the top rounds of what is in it.
private _magW = _roundW + 0.016;
private _magX = _x0 + _width * 0.56;
private _magTop = _y0 + CG_MAG_TOP;
private _magH = CG_MAG_HEIGHT;
private _wall = 0.006;

["RscText", _magX, _magTop, _magW, _magH, "", [0.03, 0.035, 0.04, 0.9]] call _fnc_make;
["RscText", _magX, _magTop, _wall, _magH, "", CG_STEEL] call _fnc_make;
["RscText", _magX + _magW - _wall, _magTop, _wall, _magH, "", CG_STEEL] call _fnc_make;
["RscText", _magX - 0.004, _magTop + _magH - 0.008, _magW + 0.008, 0.008, "", CG_STEEL] call _fnc_make;
["RscText", _magX + _wall, _magTop, 0.008, 0.004, "", CG_STEEL] call _fnc_make;
["RscText", _magX + _magW - _wall - 0.008, _magTop, 0.008, 0.004, "", CG_STEEL] call _fnc_make;

private _inX = _magX + _wall + 0.002;
private _slots = floor ((_magH - 0.014) / _roundH);
private _magRounds = [];

for "_i" from 0 to _slots - 1 do {
    _magRounds pushBack (["RscPictureKeepAspect", _inX, _magTop + 0.005 + _i * _roundH, _roundW, _roundH, QPATHTOF(data\round_side_ca.paa), UI_ROUND_COLOR] call _fnc_make);
};

// The speedloader's guide on top: a channel the clip's strip slides into.
private _guideH = 0.03;

["RscText", _magX - 0.006, _magTop - _guideH, 0.006, _guideH, "", CG_GUIDE] call _fnc_make;
["RscText", _magX + _magW, _magTop - _guideH, 0.006, _guideH, "", CG_GUIDE] call _fnc_make;

// Where the clip sits once it is in the guide, and where it lies before; a faint outline marks the guide's place.
private _clipH = _per * _roundH + 0.004;
private _seatX = _inX;
private _seatTop = _magTop - _clipH;
private _tableX = _x0 + UI_PAD + 0.02;
private _tableTop = _magTop + (_magH - _clipH) / 2;

private _ghost = ["RscText", _seatX - 0.01, _seatTop, _roundW + 0.012, _clipH, "", [0.42, 0.92, 0.42, 0.10]] call _fnc_make;

// The clip: its steel strip along the rims, and its rounds.
private _strip = ["RscText", _tableX - 0.008, _tableTop, 0.006, _clipH, "", CG_STEEL] call _fnc_make;
private _rounds = [];

for "_i" from 0 to _per - 1 do {
    _rounds pushBack (["RscPictureKeepAspect", _tableX, _tableTop + 0.002 + _i * _roundH, _roundW, _roundH, QPATHTOF(data\round_side_ca.paa), UI_ROUND_COLOR] call _fnc_make);
};

// The thumb's mark on the top round, and the pull from it to the cursor while pressing.
private _band = ["RscText", 0, 0, 0.003, 0, "", UI_ON_COLOR] call _fnc_make;
private _handle = ["RscPicture", 0, 0, CG_HANDLE, CG_HANDLE * 4 / 3, QPATHTOF(data\pill_ca.paa), UI_GAUGE_COLOR] call _fnc_make;
_handle ctrlShow false;
_band ctrlShow false;

private _hint = ["RscStructuredText", _x0 + UI_PAD, _y0 + _height - UI_PROMPT_HEIGHT - 0.006, _width - UI_PAD * 2, UI_PROMPT_HEIGHT] call _fnc_make;

GVAR(op) set ["cg", createHashMapFromArray [
    ["display", _display],
    ["count", _count],
    ["combo", _combo],
    ["hint", _hint],
    ["hintShown", ""],
    ["magRounds", _magRounds],
    ["ghost", _ghost],
    ["strip", _strip],
    ["rounds", _rounds],
    ["band", _band],
    ["handle", _handle],
    ["per", _per],
    ["roundH", _roundH],
    ["roundW", _roundW],
    ["clipH", _clipH],
    ["magTop", _magTop],
    ["seat", [_seatX, _seatTop]],
    ["table", [_tableX, _tableTop]],
    ["pos", [_tableX, _tableTop]],
    ["dragging", false],
    ["grab", [0, 0]],
    ["held", false],
    ["grabY", 0],
    ["grabTravel", 0],
    ["travel", 0],
    ["slack", 0],
    ["mouse", false],
    ["stageStart", CBA_missionTime],
    ["flying", false]
]];

// The streak shows in this window's own line (fnc_uiStreak writes to "combo").
(GVAR(op) get "ui") set ["combo", _combo];
(GVAR(op) get "ui") set ["comboShown", []];

call FUNC(uiClipGame);

nil
