#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Shows a magazine in a unit's left hand on this machine, every player seeing it through their own local object. Each
 * frame it is put into the hand, turned the way the hand holds it, which needs no attachment.
 * It goes away with the event of fnc_animTick, and by itself if the unit dies or disappears.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Magazine model <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "\z\gmr\addons\handling\data\mag_rifle.p3d"] call gmr_handling_fnc_holdMagazine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_model", "", [""]]];

if (isNull _unit || {_unit distance positionCameraToWorld [0, 0, 0] > MAG_VISIBLE_RANGE}) exitWith {};

deleteVehicle (_unit getVariable [QGVAR(heldMagazine), objNull]);

private _magazine = createSimpleObject [_model, [0, 0, 0], true];

_unit setVariable [QGVAR(heldMagazine), _magazine];

// A magazine made as a part for a weapon has its origin at its top, and lies with its front along X and bottom forward
// bend towards -X, where this mod's stand with their front along Y. Its box says which it is, and where its middle is.
(boundingBoxReal _magazine) params ["_low", "_high"];

private _middle = (_low vectorAdd _high) vectorMultiply 0.5;
private _size = _high vectorDiff _low;
_size params ["_sizeX", "_sizeY", "_sizeZ"];

private _depth = _sizeY min MAG_DEPTH;
private _axisX = MAG_DIR vectorCrossProduct MAG_UP;
private _axisY = MAG_DIR;
private _axisZ = MAG_UP;

if (_sizeX > _sizeY) then {
    // A curved magazine is wider in its box than it is deep. Turned until its curve stands straight, the hand fits it.
    _depth = _sizeX min MAG_DEPTH;

    private _tilt = atan ((_sizeX - _depth) / _sizeZ);

    _axisX = ((MAG_DIR vectorMultiply -cos _tilt) vectorAdd (MAG_UP vectorMultiply sin _tilt));
    _axisY = MAG_ACROSS;
    _axisZ = ((MAG_UP vectorMultiply cos _tilt) vectorAdd (MAG_DIR vectorMultiply sin _tilt));
};

// The back of the magazine lies in the palm, whatever its depth.
private _shift = (((_axisX vectorMultiply (_middle select 0)) vectorAdd (_axisY vectorMultiply (_middle select 1))) vectorAdd (_axisZ vectorMultiply (_middle select 2))) vectorDiff (MAG_DIR vectorMultiply (_depth / 2));

[
    {
        (_this select 0) params ["_unit", "_magazine", "_axisY", "_axisZ", "_shift"];

        if (isNull _magazine || {!alive _unit}) exitWith {
            deleteVehicle _magazine;
            [_this select 1] call CBA_fnc_removePerFrameHandler;
        };

        _magazine setPosWorld (_unit modelToWorldVisualWorld (((_unit selectionPosition ["lefthand", "Memory"]) vectorAdd MAG_FROM_HAND) vectorDiff _shift));
        _magazine setVectorDirAndUp [_unit vectorModelToWorldVisual _axisY, _unit vectorModelToWorldVisual _axisZ];
    },
    0,
    [_unit, _magazine, _axisY, _axisZ, _shift]
] call CBA_fnc_addPerFrameHandler;

nil
