#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Twice a second for the player's unit: keeps the picture of its magazines the reload check compares against, frozen
 * while a reload runs, and notices an empty magazine leaving a weapon's slot without a reload. The game deletes an
 * empty magazine that is dragged out of a weapon, so it is put back here.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call gmr_guard_fnc_watch;
 *
 * Public: No
 */

if !(missionNamespace getVariable [QEGVAR(main,enabled), false]) exitWith {};

private _unit = PLAYER_UNIT;

if (isNull _unit || {!alive _unit}) exitWith {};

// The magazine's reload phase; the magazines are in motion while it runs.
if (((weaponState _unit) param [6, 0]) > 0) exitWith {};

private _now = [_unit] call FUNC(snapshot);
private _before = GVAR(picture) select 1;
private _sameUnit = (GVAR(picture) select 0) isEqualTo _unit;

GVAR(picture) = [_unit, _now];

private _slots = [];

{
    _x params ["_weapon", "_magazines"];

    if (_weapon isNotEqualTo "" && {_magazines isNotEqualTo []} && {(_unit ammo _weapon) == 0}) then {
        _slots pushBack [_weapon, _magazines select 0];
    };
} forEach [
    [primaryWeapon _unit, primaryWeaponMagazine _unit],
    [handgunWeapon _unit, handgunMagazine _unit]
];

if (_sameUnit && {EGVAR(main,keepEmpties)} && {CBA_missionTime - GVAR(lastReload) > RELOAD_QUIET_TIME}) then {
    {
        _x params ["_weapon", "_class"];

        private _key = [toLowerANSI _class, 0];

        if (
            _weapon in [primaryWeapon _unit, handgunWeapon _unit]
            && {!(_class in (primaryWeaponMagazine _unit + handgunMagazine _unit))}
            && {(_now getOrDefault [_key, 0]) <= (_before getOrDefault [_key, 0])}
            && {([_class] call EFUNC(main,magazineInfo)) select MAG_OK}
        ) then {
            [_unit, _class, 0] call EFUNC(main,placeMagazine);
            GVAR(picture) = [_unit, [_unit] call FUNC(snapshot)];
        };
    } forEach GVAR(emptySlots);
};

GVAR(emptySlots) = _slots;

nil
