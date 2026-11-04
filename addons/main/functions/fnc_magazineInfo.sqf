#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * What this mod knows about a magazine class, worked out once on first use. A magazine's own gmr_* config entries
 * win; otherwise the caliber is looked for in its class name, then its ammo's, then its description, and whether it
 * is a belt follows from its name and size.
 *
 * Arguments:
 * 0: Magazine class <STRING>
 *
 * Return Value:
 * Facts, see the MAG_* macros <ARRAY>
 *
 * Example:
 * ["30Rnd_556x45_Stanag"] call gmr_main_fnc_magazineInfo;
 *
 * Public: No
 */

params [["_class", "", [""]]];

private _key = toLowerANSI _class;
private _known = GVAR(magazineCache) getOrDefault [_key, []];

if (_known isNotEqualTo []) exitWith {_known};

private _config = configFile >> "CfgMagazines" >> _class;
private _ammo = getText (_config >> "ammo");
private _ammoConfig = configFile >> "CfgAmmo" >> _ammo;
private _capacity = getNumber (_config >> "count");
private _simulation = toLowerANSI getText (_ammoConfig >> "simulation");

private _ok = isClass _config
    && {_capacity > 0}
    && {_simulation in ["shotbullet", "shotspread"]}
    && {getNumber (_config >> "gmr_disabled") != 1};

// Lowercase, without dots and spaces: "Caliber: 5.56x45 mm" reads caliber:556x45mm.
private _fnc_clean = {(toLowerANSI _this) regexReplace ["[. ]", ""]};
private _sources = [_class call _fnc_clean, _ammo call _fnc_clean, getText (_config >> "descriptionShort") call _fnc_clean];

private _caliber = getText (_config >> "gmr_caliber");

if (_ok && {_caliber isEqualTo ""}) then {
    {
        private _text = _x;
        private _at = GVAR(calibers) findIf {((_x select 1) findIf {_x in _text}) >= 0};

        if (_at >= 0) exitWith {
            _caliber = (GVAR(calibers) select _at) select 0;
        };
    } forEach _sources;
};

private _caliberAt = GVAR(calibers) findIf {(_x select 0) == _caliber};

if (_caliberAt < 0) then {
    _caliber = "";
};

// The variant: only the advanced system tells them apart.
private _variant = "basic";

if (_caliber isNotEqualTo "" && {GVAR(advancedAmmo)}) then {
    private _variants = (GVAR(calibers) select _caliberAt) select 2;
    private _ids = _variants apply {_x select 0};
    private _names = (_sources select 0) + "|" + (_sources select 1);
    private _wanted = getText (_config >> "gmr_variant");

    if (_wanted isEqualTo "") then {
        private _at = _variants findIf {((_x select 1) findIf {_x in _names}) >= 0};

        _wanted = switch (true) do {
            case (_at >= 0): {(_variants select _at) select 0};
            case (getNumber (_ammoConfig >> "nvgOnly") == 1): {"irtracer"};
            case (getNumber (_config >> "tracersEvery") == 1): {"tracer"};
            default {"basic"};
        };
    };

    if (_wanted in _ids) then {
        _variant = _wanted;
    };
};

// A belt: stated in its config, declared at runtime, or by its name and size.
private _belt = if (isNumber (_config >> "gmr_belt")) then {
    getNumber (_config >> "gmr_belt") == 1
} else {
    _key in GVAR(registeredBelts)
    || {_capacity >= 130}
    || {((["belt", "_box", "pouch", "_saw"]) findIf {_x in _key}) >= 0}
};

// Only a caliber with belts can be refilled from them; a magazine of another one takes loose rounds.
private _beltType = "";

if (_belt && {_caliber isNotEqualTo ""}) then {
    {
        if (isClass (configFile >> "CfgWeapons" >> format ["gmr_belt_%1_%2_1", _caliber, _x])) exitWith {
            _beltType = format ["gmr_belt_%1_%2_", _caliber, _x];
        };
    } forEach [_variant, "basic"];

    if (_beltType isEqualTo "") then {
        _belt = false;
    };
};

if (_belt && {!GVAR(beltsEnabled)}) then {
    _ok = false;
};

private _roundClass = format ["gmr_round_%1_%2", _caliber, _variant];

if (_caliber isEqualTo "" || {!isClass (configFile >> "CfgWeapons" >> _roundClass)}) then {
    _roundClass = "";
};

private _speedload = if (isNumber (_config >> "gmr_speedload")) then {
    getNumber (_config >> "gmr_speedload") == 1
} else {
    !_belt && {_capacity >= 5} && {_capacity <= 60}
};

private _facts = [];

_facts set [MAG_OK, _ok];
_facts set [MAG_CALIBER, _caliber];
_facts set [MAG_VARIANT, _variant];
_facts set [MAG_BELT, _belt];
_facts set [MAG_CAPACITY, _capacity];
_facts set [MAG_SPEEDLOAD, _speedload];
_facts set [MAG_ROUND, _roundClass];
_facts set [MAG_BELT_TYPE, _beltType];
_facts set [MAG_NAME, getText (_config >> "displayName")];
_facts set [MAG_PICTURE, getText (_config >> "picture")];

GVAR(magazineCache) set [_key, _facts];

_facts
