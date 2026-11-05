#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The model to show in the hand for a magazine: its own where it has one, which is modelSpecial for those a weapon
 * shows as a part of its own, or a model of its own instead of the game's generic pouch. Most magazines have neither,
 * their look is a fixed part of the weapon's model and cannot be taken out, so one of this mod's shapes stands in: of
 * the kind of weapon its caliber has and of its size.
 *
 * Arguments:
 * 0: Magazine class <STRING>
 *
 * Return Value:
 * Model path <STRING>
 *
 * Example:
 * ["30Rnd_556x45_Stanag"] call gmr_handling_fnc_handModel;
 *
 * Public: No
 */

params [["_class", "", [""]]];

private _config = configFile >> "CfgMagazines" >> _class;
private _facts = [_class] call EFUNC(main,magazineInfo);

// A belt box often inherits the model of the magazine it was made from, the MK200's box that of the MX SW's: a box only
// shows a model its own class sets.
private _fnc_model = if (_facts select MAG_BELT) then {
    {
        private _name = toLowerANSI _this;
        private _own = configProperties [_config, "isText _x", false];
        private _at = _own findIf {toLowerANSI configName _x == _name};

        if (_at < 0) then {""} else {getText (_own select _at)}
    }
} else {
    {getText (_config >> _this)}
};

private _special = "modelSpecial" call _fnc_model;

if (_special isNotEqualTo "") exitWith {_special};

private _own = "model" call _fnc_model;
private _ownLower = toLowerANSI _own;

if (_own isNotEqualTo "" && {!("mag_univ" in _ownLower)} && {!("dummy" in _ownLower)} && {!("ammo\mag_" in _ownLower)}) exitWith {_own};

private _caliber = _facts select MAG_CALIBER;

if (_facts select MAG_BELT) exitWith {QPATHTOF(data\mag_box.p3d)};

// The family of magazine its caliber's weapons have, and of the sizes made for it (tools/make_mag_models.py) the
// smallest that holds it, so a magazine of ten looks short and one of forty long.
private _family = switch (true) do {
    case (_caliber in ["9x19", "9x21", "9x18", "762x25", "45acp", "46x30", "570x28"]): {["pistol", [7, 15, 30]]};
    case (_caliber in ["545x39", "762x39", "762x54", "9x39"]): {["ak", [10, 20, 30, 45]]};
    case (_caliber in ["762x51", "792x57", "303"]): {["battle", [5, 10, 20, 30]]};
    case (_caliber in ["93x64", "338", "408", "127x54"]): {["heavy", [5, 10]]};
    case (_caliber in ["127x99", "127x108"]): {["fifty", [5, 10]]};
    case (_caliber == "12g"): {["shell", [5, 10]]};
    default {["rifle", [10, 20, 30, 40]]};
};

_family params ["_name", "_sizes"];

private _capacity = _facts select MAG_CAPACITY;
private _at = _sizes findIf {_x >= _capacity};
private _size = if (_at < 0) then {selectMax _sizes} else {_sizes select _at};

format ["%1\mag_%2_%3.p3d", QPATHTOF(data), _name, _size]
