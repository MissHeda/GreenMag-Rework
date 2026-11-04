#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A unit reloaded. The game has not finished putting the old magazine away yet, so the inventory is looked at a moment
 * later (fnc_checkReload), against the picture from before the reload. AI has no picture: it only gets its empty
 * magazine, when the setting says so.
 *
 * A handler of the "Reloaded" event of CAManBase; it runs where the unit is local.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Weapon <STRING>
 * 2: Muzzle <STRING>
 * 3: New magazine, [class, rounds, ...] <ARRAY>
 * 4: Old magazine, [] when nothing was loaded <ARRAY>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, "arifle_MX_F", "arifle_MX_F", ["30Rnd_65x39_caseless_mag", 30, 1, 0], ["30Rnd_65x39_caseless_mag", 0, 1, 1]] call gmr_guard_fnc_onReloaded;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_weapon", "", [""]], "", ["_new", [], [[]]], ["_old", [], [[]]]];

if (!EGVAR(main,enabled) || {isNull _unit} || {!local _unit} || {_old isEqualTo []}) exitWith {};

// A vehicle's gun or a weapon the unit does not carry is none of this.
if !(_weapon in [primaryWeapon _unit, handgunWeapon _unit, secondaryWeapon _unit]) exitWith {};

_old params [["_class", "", [""]], ["_rounds", 0, [0]]];
_new params [["_newClass", "", [""]], ["_newRounds", 0, [0]]];

private _isPlayer = _unit isEqualTo PLAYER_UNIT;

if (_isPlayer) then {
    GVAR(lastReload) = CBA_missionTime;
};

if (!_isPlayer) exitWith {
    if (_rounds == 0 && {EGVAR(main,keepEmpties)} && {EGVAR(main,emptiesForAI)} && {([_class] call EFUNC(main,magazineInfo)) select MAG_OK}) then {
        [{_this call EFUNC(main,placeMagazine)}, [_unit, _class, 0], CHECK_DELAY_EMPTY] call CBA_fnc_waitAndExecute;
    };
};

GVAR(picture) params ["_pictureUnit", "_before"];

private _known = _pictureUnit isEqualTo _unit;

[
    FUNC(checkReload),
    [_unit, [_newClass, _newRounds], [_class, _rounds], [createHashMap, _before] select _known, _known],
    [CHECK_DELAY_PARTIAL, CHECK_DELAY_EMPTY] select (_rounds == 0)
] call CBA_fnc_waitAndExecute;

nil
