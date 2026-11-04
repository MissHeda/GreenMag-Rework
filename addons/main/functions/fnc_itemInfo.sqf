#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * What an item of this mod is, worked out once on first use.
 *
 * Arguments:
 * 0: Item class <STRING>
 *
 * Return Value:
 * Facts, see the ITEM_* macros; the kind is "round", "pack", "belt" or "" for anything else <ARRAY>
 *
 * Example:
 * ["gmr_pack_556x45_basic_30"] call gmr_main_fnc_itemInfo;
 *
 * Public: No
 */

params [["_class", "", [""]]];

private _key = toLowerANSI _class;
private _known = GVAR(itemCache) getOrDefault [_key, []];

if (_known isNotEqualTo []) exitWith {_known};

private _config = configFile >> "CfgWeapons" >> _class;
private _facts = [];

_facts set [ITEM_KIND, getText (_config >> "gmr_kind")];
_facts set [ITEM_ROUNDS, getNumber (_config >> "gmr_rounds")];
_facts set [ITEM_ROUND, getText (_config >> "gmr_round")];
_facts set [ITEM_BELT_TYPE, getText (_config >> "gmr_beltType")];
_facts set [ITEM_NAME, getText (_config >> "displayName")];
_facts set [ITEM_PICTURE, getText (_config >> "picture")];
_facts set [ITEM_MASS, getNumber (_config >> "ItemInfo" >> "mass")];
_facts set [ITEM_CALIBER, getText (_config >> "gmr_caliber")];
_facts set [ITEM_VARIANT, getText (_config >> "gmr_variant")];

GVAR(itemCache) set [_key, _facts];

_facts
