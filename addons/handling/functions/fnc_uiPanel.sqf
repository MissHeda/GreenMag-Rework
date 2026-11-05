#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A flat surface with round corners, as in Arma Inventory Overhaul: three rectangles and four quarter circles, every edge on
 * a screen pixel and nothing overlapping, so a see-through panel shows no seams. A corner is as many pixels across as down,
 * a quarter circle on any screen, and never more than half the panel, so a short bar comes out as a pill.
 *
 * Arguments:
 * 0: Display <DISPLAY>
 * 1: Position [x, y, w, h] <ARRAY>
 * 2: Colour <ARRAY>
 * 3: Corner radius, as a height <NUMBER>
 *
 * Return Value:
 * The controls <ARRAY>
 *
 * Example:
 * [findDisplay 46, [0.1, 0.1, 0.3, 0.2], [0, 0, 0, 0.8], 0.012] call gmr_handling_fnc_uiPanel;
 *
 * Public: No
 */

params ["_display", "_rect", "_color", "_radius"];
_rect params ["_left", "_top", "_width", "_height"];

private _x0 = safeZoneX + round ((_left - safeZoneX) / pixelW) * pixelW;
private _y0 = safeZoneY + round ((_top - safeZoneY) / pixelH) * pixelH;
private _x1 = safeZoneX + round ((_left + _width - safeZoneX) / pixelW) * pixelW;
private _y1 = safeZoneY + round ((_top + _height - safeZoneY) / pixelH) * pixelH;
private _corner = floor (_radius / pixelH) min floor (round ((_x1 - _x0) / pixelW) / 2) min floor (round ((_y1 - _y0) / pixelH) / 2);
private _cap = _corner * pixelW;
private _rise = _corner * pixelH;
private _controls = [];

{
    if ((_x select 3) > 0) then {
        private _control = _display ctrlCreate ["RscText", -1];

        _control ctrlSetPosition _x;
        _control ctrlSetBackgroundColor _color;
        _control ctrlCommit 0;
        _controls pushBack _control;
    };
} forEach [
    [_x0 + _cap, _y0, _x1 - _x0 - 2 * _cap, _y1 - _y0],
    [_x0, _y0 + _rise, _cap, _y1 - _y0 - 2 * _rise],
    [_x1 - _cap, _y0 + _rise, _cap, _y1 - _y0 - 2 * _rise]
];

{
    _x params ["_texture", "_position"];

    private _control = _display ctrlCreate ["RscPicture", -1];

    _control ctrlSetPosition _position;
    _control ctrlSetText _texture;
    _control ctrlSetTextColor _color;
    _control ctrlCommit 0;
    _controls pushBack _control;
} forEach [
    [QPATHTOF(data\corner_tl_ca.paa), [_x0, _y0, _cap, _rise]],
    [QPATHTOF(data\corner_tr_ca.paa), [_x1 - _cap, _y0, _cap, _rise]],
    [QPATHTOF(data\corner_bl_ca.paa), [_x0, _y1 - _rise, _cap, _rise]],
    [QPATHTOF(data\corner_br_ca.paa), [_x1 - _cap, _y1 - _rise, _cap, _rise]]
];

_controls
