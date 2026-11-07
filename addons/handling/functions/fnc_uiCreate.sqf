#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Draws what loading looks like. By default in the look of Arma Inventory Overhaul: a dark panel with round corners
 * holding the magazine, its count and a strip with one segment per round of it, so a magazine of ten and one of a
 * hundred look as different as they are; in the minigame a track below it, the round flying along it into the green
 * opening. The "classic" display is the original GreenMag's: the game's hold-action ring filling up in the middle of
 * the screen.
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

if (isNil QGVAR(op) || {isNull _display}) exitWith {};

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

if (EGVAR(main,loadDisplay) == 1) exitWith {
    // The ring of the game's hold actions, with the action's icon in it, the magazine's name above and the count below.
    private _size = UI_RING_SIZE;
    private _ringX = 0.5 - _size / 2;
    private _ringY = 0.5 - _size * 4 / 3 / 2 + UI_RING_DROP;
    private _ringH = _size * 4 / 3;

    ["RscPicture", _ringX, _ringY, _size, _ringH, "\A3\Ui_f\data\IGUI\Cfg\HoldActions\idle\idle_0_ca.paa", [1, 1, 1, 0.5]] call _fnc_make;
    private _ring = ["RscPicture", _ringX, _ringY, _size, _ringH, "\A3\Ui_f\data\IGUI\Cfg\HoldActions\progress\progress_0_ca.paa"] call _fnc_make;
    ["RscPicture", _ringX + _size * 0.3, _ringY + _ringH * 0.3, _size * 0.4, _ringH * 0.4, QPATHTOF(data\action_fill.paa)] call _fnc_make;

    private _title = ["RscStructuredText", 0.5 - 0.3, _ringY - 0.045, 0.6, 0.04] call _fnc_make;
    _title ctrlSetStructuredText parseText format ["<t align='center' size='0.9' shadow='2'>%1</t>", GVAR(op) get "title"];

    private _count = ["RscStructuredText", 0.5 - 0.3, _ringY + _ringH + 0.004, 0.6, 0.04] call _fnc_make;
    private _prompt = ["RscStructuredText", 0.5 - 0.3, _ringY + _ringH + 0.038, 0.6, 0.035] call _fnc_make;

    GVAR(op) set ["ui", createHashMapFromArray [
        ["all", _all],
        ["ring", _ring],
        ["count", _count],
        ["strip", []],
        ["spark", controlNull],
        ["prompt", _prompt],
        ["combo", controlNull],
        ["segments", 1],
        ["classic", true]
    ]];

    call FUNC(uiRound);
};

private _capacity = (GVAR(op) get "capacity") max 1;
private _segments = _capacity min UI_MAX_SEGMENTS;
private _game = GVAR(op) get "game";
private _pad = UI_PAD;
private _width = UI_WIDTH;

// Rows from the top: the magazine with its name and count, the strip, the minigame's track, a line, what to press.
private _tileHeight = UI_TILE_HEIGHT;
private _tileWidth = _tileHeight * 3 / 4;
private _stripTop = _pad + _tileHeight + UI_GAP;
private _trackTop = _stripTop + UI_STRIP_HEIGHT + UI_GAP;
private _clipGame = GVAR(op) getOrDefault ["clipGame", false];
private _gameHeight = [UI_GAME_HEIGHT, UI_CLIP_GAME_HEIGHT] select _clipGame;
private _lineTop = [_stripTop + UI_STRIP_HEIGHT, _trackTop + _gameHeight] select _game;
_lineTop = _lineTop + UI_GAP;
private _height = _lineTop + UI_PROMPT_HEIGHT + _pad * 0.5;
private _x0 = safeZoneX + (safeZoneW - _width) / 2;
private _y0 = safeZoneY + safeZoneH * UI_TOP;

_all append ([_display, [_x0, _y0, _width, _height], UI_PANEL_COLOR, UI_RADIUS] call FUNC(uiPanel));
_all append ([_display, [_x0 + _pad, _y0 + _pad, _tileWidth, _tileHeight], UI_TILE_COLOR, UI_RADIUS * 0.6] call FUNC(uiPanel));
["RscPictureKeepAspect", _x0 + _pad + 0.003, _y0 + _pad + 0.003, _tileWidth - 0.006, _tileHeight - 0.006, GVAR(op) get "picture"] call _fnc_make;

private _textX = _x0 + _pad * 2 + _tileWidth;
private _textW = _width - _tileWidth - _pad * 3;

private _title = ["RscStructuredText", _textX, _y0 + _pad - 0.004, _textW, 0.034] call _fnc_make;
_title ctrlSetStructuredText parseText format ["<t size='0.85' color='#c9ced6' font='PuristaMedium'>%1</t>", GVAR(op) get "title"];

private _count = ["RscStructuredText", _textX, _y0 + _pad + _tileHeight - 0.046, _textW, 0.05] call _fnc_make;

// The run of hits in the minigame, on the free right of the count.
private _combo = ["RscStructuredText", _textX, _y0 + _pad + _tileHeight - 0.036, _textW, 0.036] call _fnc_make;

// The strip: a little pill per round.
private _stripX = _x0 + _pad;
private _stripW = _width - _pad * 2;
private _stripY = _y0 + _stripTop;
private _gap = [0.0022, 0.0011] select (_segments > 30);
private _segmentW = (_stripW - _gap * (_segments - 1)) / _segments;
private _strip = [];

for "_i" from 0 to _segments - 1 do {
    _strip pushBack (["RscPicture", _stripX + _i * (_segmentW + _gap), _stripY, _segmentW, UI_STRIP_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_OFF_COLOR] call _fnc_make);
};

// The bright spark over the segment that just lit, fading out by itself.
private _spark = ["RscPicture", _stripX, _stripY - 0.003, _segmentW, UI_STRIP_HEIGHT + 0.006, QPATHTOF(data\pill_ca.paa), [1, 1, 1, 1]] call _fnc_make;
_spark ctrlSetFade 1;
_spark ctrlCommit 0;

// A hairline between the display and what to press.
private _line = ["RscText", _stripX, _y0 + _lineTop - UI_GAP / 2, _stripW, pixelH] call _fnc_make;
_line ctrlSetBackgroundColor [1, 1, 1, 0.07];

private _prompt = ["RscStructuredText", _stripX, _y0 + _lineTop, _stripW, UI_PROMPT_HEIGHT] call _fnc_make;

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
    ["segments", _segments],
    ["classic", false]
]];

// The stripper clip minigame: the clip above the track, the magazine with its guide (the green opening) on it, the
// thumb's pressure gauge below with its green and red stretches.
if (_game && {_clipGame}) then {
    private _ui = GVAR(op) get "ui";
    private _rowTop = _y0 + _trackTop;
    private _clipH = 0.046;
    private _middle = _rowTop + _clipH + 0.012;

    _all append ([_display, [_stripX, _middle - UI_TRACK_HEIGHT / 2, _stripW, UI_TRACK_HEIGHT], UI_OFF_COLOR, UI_TRACK_HEIGHT / 2] call FUNC(uiPanel));

    private _zoneY = _middle - UI_ZONE_HEIGHT / 2;
    private _glow = ["RscPicture", _stripX, _zoneY, 0, UI_ZONE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_ZONE_COLOR] call _fnc_make;
    private _hit = ["RscPicture", _stripX, _zoneY, 0, UI_ZONE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_ON_COLOR] call _fnc_make;
    _hit ctrlSetFade 1;
    _hit ctrlCommit 0;

    private _catcherH = 0.05;
    private _catcherW = _catcherH * 3 / 4;
    private _catcher = ["RscPictureKeepAspect", _stripX, _middle - _catcherH * 0.3, _catcherW, _catcherH, GVAR(op) get "picture"] call _fnc_make;

    private _clip = ["RscPictureKeepAspect", _stripX, _rowTop, UI_CLIP_WIDTH, _clipH, GVAR(op) get "clipPicture"] call _fnc_make;

    // The gauge: its track, the green stretch the rounds move in, the red one that jams, and the pressure filling it.
    private _gaugeY = _rowTop + UI_CLIP_GAME_HEIGHT - UI_GAUGE_HEIGHT;
    private _gauge = [];

    _gauge pushBack (["RscPicture", _stripX, _gaugeY, _stripW, UI_GAUGE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_OFF_COLOR] call _fnc_make);
    _gauge pushBack (["RscPicture", _stripX + _stripW * CLIP_PRESSURE_GREEN, _gaugeY, _stripW * (CLIP_PRESSURE_RED - CLIP_PRESSURE_GREEN), UI_GAUGE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_ZONE_COLOR] call _fnc_make);
    _gauge pushBack (["RscPicture", _stripX + _stripW * CLIP_PRESSURE_RED, _gaugeY, _stripW * (1 - CLIP_PRESSURE_RED), UI_GAUGE_HEIGHT, QPATHTOF(data\pill_ca.paa), [1, 0.3, 0.2, 0.35]] call _fnc_make);

    private _fill = ["RscPicture", _stripX, _gaugeY + UI_GAUGE_HEIGHT * 0.2, 0.0001, UI_GAUGE_HEIGHT * 0.6, QPATHTOF(data\pill_ca.paa), UI_GAUGE_COLOR] call _fnc_make;
    _gauge pushBack _fill;

    _ui set ["glow", _glow];
    _ui set ["hit", _hit];
    _ui set ["catcher", _catcher];
    _ui set ["catcherW", _catcherW];
    _ui set ["comboShown", []];
    _ui set ["clip", _clip];
    _ui set ["clipW", UI_CLIP_WIDTH];
    _ui set ["clipY", _rowTop];
    _ui set ["sink", 0.012];
    _ui set ["gauge", _gauge];
    _ui set ["gaugeFill", _fill];

    call FUNC(uiClipGame);
};

if (_game && {!_clipGame}) then {
    private _ui = GVAR(op) get "ui";
    private _middle = _y0 + _trackTop + UI_GAME_HEIGHT / 2;

    _all append ([_display, [_stripX, _middle - UI_TRACK_HEIGHT / 2, _stripW, UI_TRACK_HEIGHT], UI_OFF_COLOR, UI_TRACK_HEIGHT / 2] call FUNC(uiPanel));

    // The round flies in from the left; the magazine waits on the track to catch it. The green capsule under it is how
    // far off the catch may be, and flashes on a hit.
    private _zoneY = _middle - UI_ZONE_HEIGHT / 2;
    private _glow = ["RscPicture", _stripX, _zoneY, 0, UI_ZONE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_ZONE_COLOR] call _fnc_make;

    private _hit = ["RscPicture", _stripX, _zoneY, 0, UI_ZONE_HEIGHT, QPATHTOF(data\pill_ca.paa), UI_ON_COLOR] call _fnc_make;
    _hit ctrlSetFade 1;
    _hit ctrlCommit 0;

    private _catcherW = UI_CATCHER_HEIGHT * 3 / 4;
    private _catcher = ["RscPictureKeepAspect", _stripX, _middle - UI_CATCHER_HEIGHT / 2, _catcherW, UI_CATCHER_HEIGHT, GVAR(op) get "picture"] call _fnc_make;

    private _roundW = 0.05;
    private _roundH = UI_GAME_HEIGHT * 0.6;
    private _round = ["RscPictureKeepAspect", _stripX, _middle - _roundH / 2, _roundW, _roundH, QPATHTOF(data\round_side_ca.paa), UI_ROUND_COLOR] call _fnc_make;

    _ui set ["glow", _glow];
    _ui set ["hit", _hit];
    _ui set ["catcher", _catcher];
    _ui set ["catcherW", _catcherW];
    _ui set ["comboShown", []];
    _ui set ["round", _round];
    _ui set ["roundW", _roundW];

    call FUNC(uiGame);
};

call FUNC(uiRound);

nil
