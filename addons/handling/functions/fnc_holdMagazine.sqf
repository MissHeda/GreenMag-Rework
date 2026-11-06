#include "..\script_component.hpp"
#include "..\mag_backs.hpp"
#include "..\round_path.hpp"
/*
 * Author: Miss Heda
 * Shows a magazine in a unit's left hand on this machine, every player seeing it through their own local object. Each
 * frame it is attached anew where the hand is, turned the way the hand holds it. A round goes with the right hand
 * through the loading gesture: taken between thumb and index finger at the pouch, carried up and pressed in from
 * above, where it goes; GVAR(roundPath) says where it is from the right hand's point for the gesture's progress.
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
 * [player, "\z\gmr\addons\handling\data\mag_rifle_30.p3d"] call gmr_handling_fnc_holdMagazine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_model", "", [""]]];

if (isNull _unit || {_unit distance positionCameraToWorld [0, 0, 0] > MAG_VISIBLE_RANGE}) exitWith {};

deleteVehicle (_unit getVariable [QGVAR(heldMagazine), objNull]);
deleteVehicle (_unit getVariable [QGVAR(heldRound), objNull]);

private _magazine = createSimpleObject [_model, [0, 0, 0], true];

_unit setVariable [QGVAR(heldMagazine), _magazine];

private _round = createSimpleObject [QPATHTOF(data\round_hand.p3d), [0, 0, 0], true];
_round hideObject true;
_unit setVariable [QGVAR(heldRound), _round];

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

// This mod's own magazines know where their back is, however deep a large caliber or bent the curve makes them.
private _path = (toLowerANSI _model) splitString "\\";
private _ownName = ((_path select (count _path - 1)) splitString ".") select 0;
private _ownAt = MAG_BACKS findIf {(_x select 0) == _ownName};

if (_ownAt >= 0 && {QPATHTOF(data) in _model}) then {
    _depth = 2 * ((_middle select 1) - ((MAG_BACKS select _ownAt) select 1));
};

// The back of the magazine lies in the palm, whatever its depth.
private _shift = (((_axisX vectorMultiply (_middle select 0)) vectorAdd (_axisY vectorMultiply (_middle select 1))) vectorAdd (_axisZ vectorMultiply (_middle select 2))) vectorDiff (MAG_DIR vectorMultiply (_depth / 2));

[
    {
        (_this select 0) params ["_unit", "_magazine", "_axisY", "_axisZ", "_shift", "_round"];

        if (isNull _magazine || {!alive _unit}) exitWith {
            deleteVehicle _magazine;
            deleteVehicle _round;
            [_this select 1] call CBA_fnc_removePerFrameHandler;
        };

        // The round, while the right hand holds it: from the pinch at the pouch until it is pressed in.
        private _progress = _unit getUnitMovesInfo 5;
        private _held = gestureState _unit == QGVAR(load) && {_progress >= ROUND_GRAB || {_progress <= ROUND_PRESS}};

        _round hideObject !_held;

        if (_held) then {
            private _path = GVAR(roundPath);
            private _at = (_progress max 0 min 1) * (count _path - 1);
            private _index = floor _at min (count _path - 2);
            private _from = _path select _index;
            private _point = _from vectorAdd (((_path select (_index + 1)) vectorDiff _from) vectorMultiply (_at - _index));

            _round attachTo [_unit, (_unit selectionPosition ["righthand", "Memory"]) vectorAdd _point];
            _round setVectorDirAndUp [MAG_DIR, MAG_UP];
        };

        // Attached, not set into place: a magazine model with a geometry of its own (the CAR-95's) would otherwise
        // shove the unit across the map. Attached, its turn is the unit's own.
        _magazine attachTo [_unit, ((_unit selectionPosition ["lefthand", "Memory"]) vectorAdd MAG_FROM_HAND) vectorDiff _shift];
        _magazine setVectorDirAndUp [_axisY, _axisZ];
    },
    0,
    [_unit, _magazine, _axisY, _axisZ, _shift, _round]
] call CBA_fnc_addPerFrameHandler;

nil
