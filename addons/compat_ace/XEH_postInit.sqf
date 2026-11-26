#include "script_component.hpp"

// setAmmo reaches other machines only when each of them does it.
[QGVAR(syncAmmo), {
    params ["_unit", "_weapon", "_ammo"];

    _unit setAmmo [_weapon, _ammo];
}] call CBA_fnc_addEventHandler;

// Where the gun is local: what it has no room for, or a gun that changed meanwhile, goes back to who linked it.
[QGVAR(beltLinked), {
    params ["_target", "_unit", "_magazine", "_type", "_rounds"];

    private _weapon = currentWeapon _target;
    private _ammo = _target ammo _weapon;
    private _added = 0;

    if (currentMagazine _target == _magazine && {_ammo > 0}) then {
        _added = (getNumber (configFile >> "CfgMagazines" >> _magazine >> "count") - _ammo) min _rounds max 0;
    };

    if (_added > 0) then {
        [QGVAR(syncAmmo), [_target, _weapon, _ammo + _added]] call CBA_fnc_globalEvent;
    };

    [QGVAR(beltReturned), [_unit, _type, _rounds - _added, _added > 0], _unit] call CBA_fnc_targetEvent;
}] call CBA_fnc_addEventHandler;

[QGVAR(beltReturned), {
    params ["_unit", "_type", "_rounds", "_linked"];

    [_unit, _type, _rounds] call EFUNC(main,giveBelt);

    if (hasInterface && {_unit == ACE_player}) then {
        [[LLSTRING(BeltNotLinked), LLSTRING(BeltLinked)] select _linked] call ace_common_fnc_displayTextStructured;

        if (_linked) then {
            PLAY_SOUND(belt_feed);
        } else {
            PLAY_SOUND(denied);
        };
    };
}] call CBA_fnc_addEventHandler;

if (!hasInterface) exitWith {};

// Counted ahead of the arsenal's first opening. In the editor, where no mission starts, that opening sets it off
// (fnc_arsenalFilter).
call FUNC(countCalibers);
