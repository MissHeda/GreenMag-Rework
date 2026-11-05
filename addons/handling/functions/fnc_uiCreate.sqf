#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Draws what loading looks like, in the look of Arma Inventory Overhaul: a dark panel with round corners holding the
 * magazine, its count and a strip with one segment per round of it, so a magazine of ten and one of a hundred look as
 * different as they are. In the minigame a track below: the round flies along it, the magazine is the slot to hit.
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
private _height = ([UI_HEIGHT, UI_HEIGHT + UI_GAME_HEIGHT] select _game) + UI_PROMPT_HEIGHT;
private _x0 = safeZoneX + (safeZoneW - _width) / 2;
private _y0 = safeZoneY + safeZoneH * UI_TOP;
private _all = [];

private _fnc_make = {
    params ["_class", "_x", "_y", "_w", "_h", ["_texture", ""], ["_colour", []]];

    private _control = _display ctrlCreate [_class, -1];

    _control ctrlSetPosition [_x, _y, _w, _h];

    if (_texture isNotEqualTo "") then {
        _control ctrlSetText _texture;
    };

    if (_colour isNotEqualTo []) then {
        _control ctrlSetTextColor _colour;
    };

    _control ctrlCommit 0;
    _all pushBack _control;
    _control
};

_all append ([_display, [_x0, _y0, _width, _height], UI_PANEL_COLOR, UI_RADIUS] call FUNC(uiPanel));

private _tileHeight = 0.076;
private _tileWidth = _tileHeight * 3 / 4;
private _pad = 0.008;

_all append ([_display, [_x0 + _pad, _y0 + _pad, _tileWidth, _tileHeight], UI_TILE_COLOR, UI_RADIUS * 0.6] call FUNC(uiPanel));
["RscPictureKeepAspect", _x0 + _pad + 0.002, _y0 + _pad + 0.002, _tileWidth - 0.004, _tileHeight - 0.004, GVAR(op) get "picture"] call _fnc_make;

private _textX = _x0 + _pad * 2 + _tileWidth;
private _textW = _width - _tileWidth - _pad * 3;

private _title = ["RscStructuredText", _textX, _y0 + 0.006, _textW, 0.036] call _fnc_make;
_title ctrlSetStructuredText parseText format ["<t size='0.85' color='#c9ced6' font='PuristaMedium'>%1</t>", GVAR(op) get "title"];

private _count = ["RscStructuredText", _textX, _y0 + 0.032, _textW, 0.05] call _fnc_make;
// The run of hits in the minigame, on the free right of the count.
private _combo = ["RscStructuredText", _textX, _y0 + 0.042, _textW, 0.036] call _fnc_make;

// The strip: a little pill per round.
private _stripX = _x0 + _pad;
private _stripW = _width - _pad * 2;
private _stripY = _y0 + _pad * 2 + _tileHeight;
private _gap = [0.0018, 0.0009] select (_segments > 30);
private _segmentW = (_stripW - _gap * (_segments - 1)) / _segments;
private _strip = [];

for "_i" from 0 to _segments - 1 do {
    _strip pushBack (["RscPicture", _stripX + _i * (_segmentW + _gap), _stripY, _segmentW, UI_STRIP_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_OFF_COLOR] call _fnc_make);
};

// The bright spark over the segment that just lit, fading out by itself.
private _spark = ["RscPicture", _stripX, _stripY - 0.003, _segmentW, UI_STRIP_HEIGHT + 0.006, QPATHTOF(data\pill_ca.paa), [1, 1, 1, 1]] call _fnc_make;
_spark ctrlSetFade 1;
_spark ctrlCommit 0;

// What to press, on the bottom line of the panel.
private _prompt = ["RscStructuredText", _x0 + _pad, _y0 + _height - UI_PROMPT_HEIGHT, _width - _pad * 2, UI_PROMPT_HEIGHT] call _fnc_make;

GVAR(op) set ["ui", createHashMapFromArray [
    ["all", _all],
    ["count", _count],
    ["strip", _strip],
    ["spark", _spark],
    ["prompt", _prompt],
    ["combo", _combo],
    ["stripX", _stripX],
    ["stripW", _stripW],
    ["segmentW", _segmentW],
    ["gap", _gap],
    ["segments", _segments]
]];

if (_game) then {
    private _ui = GVAR(op) get "ui";
    private _trackY = _stripY + UI_STRIP_HEIGHT + _pad + 0.004;
    private _trackH = UI_GAME_HEIGHT - _pad - 0.004;
    private _middle = _trackY + _trackH / 2 - UI_TRACK_HEIGHT / 2;

    _all append ([_display, [_stripX, _middle, _stripW, UI_TRACK_HEIGHT], UI_OFF_COLOR, UI_TRACK_HEIGHT / 2] call FUNC(uiPanel));

    // The slot: a glow on the track where the round has to be, and the magazine on it. It flashes on a hit.
    private _glow = ["RscPicture", _stripX, _trackY + 0.004, 0, _trackH - 0.008, QPATHTOF(data\pill_ca.paa), UI_ZONE_COLOR] call _fnc_make;
    private _hit = ["RscPicture", _stripX, _trackY + 0.004, 0, _trackH - 0.008, QPATHTOF(data\pill_ca.paa), UI_ON_COLOR] call _fnc_make;
    _hit ctrlSetFade 1;
    _hit ctrlCommit 0;

    private _slotH = _trackH + 0.012;
    private _slot = ["RscPictureKeepAspect", _stripX, _trackY - 0.006, _slotH * 3 / 4, _slotH, GVAR(op) get "picture"] call _fnc_make;
    private _roundW = 0.05;
    private _round = ["RscPictureKeepAspect", _stripX, _trackY, _roundW, _trackH, QPATHTOF(data\round_side_ca.paa), UI_ROUND_COLOR] call _fnc_make;

    _ui set ["glow", _glow];
    _ui set ["hit", _hit];
    _ui set ["slot", _slot];
    _ui set ["slotW", _slotH * 3 / 4];
    _ui set ["round", _round];
    _ui set ["roundW", _roundW];

    call FUNC(uiGame);
};

call FUNC(uiRound);

nil
