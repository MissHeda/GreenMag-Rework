#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Which loose belts a unit can link into the machine gun a unit is firing: its own kind, else universal. An empty or full
 * gun takes none, as with ACE's own linking of a box.
 *
 * Arguments:
 * 0: Unit linking <OBJECT>
 * 1: Unit with the weapon, may be the same <OBJECT>
 *
 * Return Value:
 * [belt type, rounds the unit carries of it, rounds the gun is missing], [] if it cannot be done <ARRAY>
 *
 * Example:
 * [player, cursorObject] call gmr_compat_ace_fnc_linkBeltSource;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_target", objNull, [objNull]]];

if (!EGVAR(main,enabled) || {!EGVAR(main,beltsEnabled)} || {!isNull objectParent _target} || {!alive _target}) exitWith {[]};

private _magazine = currentMagazine _target;

if (_magazine isEqualTo "") exitWith {[]};

private _facts = [_magazine] call EFUNC(main,magazineInfo);

if !((_facts select MAG_OK) && {_facts select MAG_BELT}) exitWith {[]};

private _ammo = _target ammo currentWeapon _target;
private _missing = (_facts select MAG_CAPACITY) - _ammo;

if (_ammo == 0 || {_missing <= 0}) exitWith {[]};

private _source = [];

{
    private _rounds = 0;

    {
        _rounds = _rounds + (_x select 1);
    } forEach ([_unit, _x] call EFUNC(main,beltItems));

    if (_rounds > 0) exitWith {
        _source = [_x, _rounds, _missing];
    };
} forEach [_facts select MAG_BELT_TYPE, UNIVERSAL_BELT];

_source
