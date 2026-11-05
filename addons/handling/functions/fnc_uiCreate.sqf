#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Draws what loading looks like: the magazine, its count, and a strip with one segment per round of it, so a magazine of
 * ten and one of a hundred look as different as they are. Controls on the game's own display, so no key is taken from
 * the player.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_handling_fnc_uiCreate;
 *
 * Public: No
 */

private _display = findDisplay 46;

if (isNull _display || {isNil QGVAR(op)}) exitWith {};

private _capacity = (GVAR(op) get "capacity") max 1;
private _segments = _capacity min UI_MAX_SEGMENTS;
private _game = GVAR(op) get "game";
private _width = UI_WIDTH;
private _height = [UI_HEIGHT, UI_HEIGHT + UI_GAME_HEIGHT] select _game;
private _x0 = safeZoneX + (safeZoneW - _width) / 2;
private _y0 = safeZoneY + safeZoneH * UI_TOP;
private _all = [];

private _fnc_make = {
    params ["_class", "_x", "_y", "_w", "_h"];

    private _control = _display ctrlCreate [_class, -1];

    _control ctrlSetPosition [_x, _y, _w, _h];
    _control ctrlCommit 0;
    _all pushBack _control;
    _control
};

private _panel = ["RscText", _x0, _y0, _width, _height] call _fnc_make;
_panel ctrlSetBackgroundColor UI_PANEL_COLOR;

private _accent = ["RscText", _x0, _y0, _width, 0.003] call _fnc_make;
_accent ctrlSetBackgroundColor UI_ON_COLOR;

private _pictureHeight = 0.075;
private _pictureWidth = _pictureHeight * 3 / 4;
private _picture = ["RscPictureKeepAspect", _x0 + 0.006, _y0 + 0.008, _pictureWidth, _pictureHeight] call _fnc_make;
_picture ctrlSetText (GVAR(op) get "picture");

private _textX = _x0 + _pictureWidth + 0.014;
private _textW = _width - _pictureWidth - 0.02;

private _title = ["RscStructuredText", _textX, _y0 + 0.006, _textW, 0.036] call _fnc_make;
_title ctrlSetStructuredText parseText format ["<t size='0.85' color='#d8d8d8' font='PuristaMedium'>%1</t>", GVAR(op) get "title"];

private _count = ["RscStructuredText", _textX, _y0 + 0.034, _textW, 0.05] call _fnc_make;

// The strip.
private _stripX = _x0 + 0.008;
private _stripW = _width - 0.016;
private _stripY = _y0 + 0.09;
private _gap = [0.0016, 0.0008] select (_segments > 30);
private _segmentW = (_stripW - _gap * (_segments - 1)) / _segments;
private _strip = [];

for "_i" from 0 to _segments - 1 do {
    private _segment = ["RscText", _stripX + _i * (_segmentW + _gap), _stripY, _segmentW, UI_STRIP_HEIGHT] call _fnc_make;

    _segment ctrlSetBackgroundColor UI_OFF_COLOR;
    _strip pushBack _segment;
};

// The bright spark over the segment that just lit, fading out by itself.
private _spark = ["RscText", _stripX, _stripY - 0.003, _segmentW, UI_STRIP_HEIGHT + 0.006] call _fnc_make;
_spark ctrlSetBackgroundColor [1, 1, 1, 1];
_spark ctrlSetFade 1;
_spark ctrlCommit 0;

private _prompt = ["RscStructuredText", _x0, _y0 + _height + 0.002, _width, 0.036] call _fnc_make;

GVAR(op) set ["ui", createHashMapFromArray [
    ["all", _all],
    ["count", _count],
    ["strip", _strip],
    ["spark", _spark],
    ["prompt", _prompt],
    ["stripX", _stripX],
    ["stripW", _stripW],
    ["segmentW", _segmentW],
    ["gap", _gap],
    ["segments", _segments]
]];

if (_game) then {
    private _trackY = _stripY + UI_STRIP_HEIGHT + 0.012;
    private _track = ["RscText", _stripX, _trackY, _stripW, UI_GAME_HEIGHT - 0.012] call _fnc_make;
    _track ctrlSetBackgroundColor UI_OFF_COLOR;

    private _zone = ["RscText", _stripX, _trackY, 0, UI_GAME_HEIGHT - 0.012] call _fnc_make;
    _zone ctrlSetBackgroundColor UI_ON_COLOR;

    private _marker = ["RscText", _stripX, _trackY - 0.003, 0.003, UI_GAME_HEIGHT - 0.006] call _fnc_make;
    _marker ctrlSetBackgroundColor [1, 1, 1, 1];

    private _ui = GVAR(op) get "ui";
    _ui set ["zone", _zone];
    _ui set ["marker", _marker];
    _ui set ["trackY", _trackY];
};

call FUNC(uiRound);

nil
