#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The version of a magazine for another kind of round: 30Rnd_556x45_Stanag and 30Rnd_556x45_Stanag_Tracer_Red are the
 * same magazine. Magazines count as one when their class names match without the words that only name the round, and
 * they hold the same number of rounds. The names of all magazines are read once, on first use.
 *
 * Arguments:
 * 0: Magazine class <STRING>
 * 1: Kind of round, a variant of its caliber <STRING>
 *
 * Return Value:
 * Magazine class, "" when there is no such version <STRING>
 *
 * Example:
 * ["30Rnd_556x45_Stanag", "tracer"] call gmr_main_fnc_siblingMagazine;
 *
 * Public: No
 */

params [["_class", "", [""]], ["_variant", "basic", [""]]];

private _fnc_key = {
    private _words = (toLowerANSI _this) splitString "_";

    (_words select {!(_x in ["tracer", "tracers", "trc", "t", "ir", "irtracer", "red", "green", "yellow", "white", "orange", "ball"])}) joinString "_"
};

if (isNil QGVAR(magazineFamilies)) then {
    GVAR(magazineFamilies) = createHashMap;

    {
        private _name = configName _x;

        (GVAR(magazineFamilies) getOrDefault [_name call _fnc_key, [], true]) pushBack _name;
    } forEach ("getNumber (_x >> 'scope') >= 2" configClasses (configFile >> "CfgMagazines"));
};

private _capacity = getNumber (configFile >> "CfgMagazines" >> _class >> "count");
private _family = GVAR(magazineFamilies) getOrDefault [_class call _fnc_key, []];
private _at = _family findIf {
    getNumber (configFile >> "CfgMagazines" >> _x >> "count") == _capacity
    && {(([_x] call FUNC(magazineInfo)) select MAG_TYPE) == _variant}
};

if (_at < 0) exitWith {""};

_family select _at
