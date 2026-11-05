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

// Which calibers the loaded mods' magazines use, for the arsenal. Thousands of classes, so in the background: it would be a
// noticeable hang on the arsenal's first opening. Universal ammunition is there for the magazines nothing else fits.
[] spawn {
    private _used = createHashMapFromArray [["universal", true]];

    {
        private _facts = [configName _x] call EFUNC(main,magazineInfo);

        if (_facts select MAG_OK) then {
            _used set [_facts select MAG_CALIBER, true];
        };
    } forEach ("getNumber (_x >> 'scope') > 0" configClasses (configFile >> "CfgMagazines"));

    GVAR(usedCalibers) = _used;
};

// ACE builds its side buttons as this event goes out, so they are moved a frame later.
["ace_arsenal_rightPanelContainer", {
    [FUNC(arrangeArsenal), _this] call CBA_fnc_execNextFrame;
}] call CBA_fnc_addEventHandler;

["ace_arsenal_rightPanelFilled", {
    params ["_display", "", "_button"];

    if (_button != 61 + GVAR(arsenalSlot) * 2) exitWith {};

    [_display] call FUNC(arsenalFilter);

    if (EGVAR(main,arsenalHighlight)) then {
        [_display] call FUNC(arsenalHighlight);
    };
}] call CBA_fnc_addEventHandler;
