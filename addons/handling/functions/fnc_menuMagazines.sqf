#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The children of "Refill" and "Unload": one entry per magazine type, under it its magazines and, when there are
 * several, all of them at once. Unload lists the belt items as well. What is chosen is read again when it is done
 * (fnc_applyFill, fnc_applyUnload), so nothing here is kept as the truth.
 *
 * Arguments:
 * 0: Player <OBJECT>
 * 1: "fill" or "unload" <STRING>
 *
 * Return Value:
 * ACE actions <ARRAY>
 *
 * Example:
 * [player, "fill"] call gmr_handling_fnc_menuMagazines;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_mode", "fill", [""]]];

private _fill = _mode == "fill";
private _types = createHashMap;

{
    _x params ["_class", "_rounds"];

    private _facts = [_class] call EFUNC(main,magazineInfo);

    if (
        (_facts select MAG_OK)
        && {[_rounds > 0, _rounds < (_facts select MAG_CAPACITY)] select _fill}
    ) then {
        private _list = _types getOrDefault [_class, [], true];

        _list pushBack _rounds;
    };
} forEach (magazinesAmmoCargo uniformContainer _unit + magazinesAmmoCargo vestContainer _unit + magazinesAmmoCargo backpackContainer _unit);

private _limit = round EGVAR(main,maxMagazines);
private _classes = keys _types;

_classes sort true;

private _actions = _classes apply {
    private _class = _x;
    private _facts = [_class] call EFUNC(main,magazineInfo);
    private _capacity = _facts select MAG_CAPACITY;
    private _picture = _facts select MAG_PICTURE;
    private _amounts = _types get _class;

    // The fullest first to refill, the emptiest first to unload.
    _amounts sort !_fill;

    private _shown = if (_limit > 0) then {_amounts select [0, _limit]} else {_amounts};
    private _children = [];

    if (count _amounts > 1) then {
        private _action = [
            format ["gmr_%1_all", _class],
            format [LLSTRING(All), count _amounts],
            _picture,
            {
                params ["", "_player", "_params"];
                _params params ["_mode", "_class", "_amounts"];

                [_player, _mode, _class, _amounts] call FUNC(start);
            },
            {true},
            {},
            [_mode, _class, _amounts]
        ] call ace_interact_menu_fnc_createAction;

        _children pushBack [_action, [], _unit];
    };

    {
        private _action = [
            format ["gmr_%1_%2", _class, _forEachIndex],
            format ["[%1/%2]", _x, _capacity],
            _picture,
            {
                params ["", "_player", "_params"];
                _params params ["_mode", "_class", "_rounds"];

                [_player, _mode, _class, [_rounds]] call FUNC(start);
            },
            {true},
            {},
            [_mode, _class, _x]
        ] call ace_interact_menu_fnc_createAction;

        _children pushBack [_action, [], _unit];
    } forEach _shown;

    private _top = [
        format ["gmr_%1", _class],
        _facts select MAG_NAME,
        _picture,
        {},
        {true}
    ] call ace_interact_menu_fnc_createAction;

    [_top, _children, _unit]
};

// Refill: belt items with room, when there are rounds for them.
if (_fill) exitWith {
    {
        private _facts = [_x] call EFUNC(main,itemInfo);

        if ((_facts select ITEM_KIND) == "belt" && {(([_unit, _x, ""] call FUNC(beltRefillSource)) select 0) isNotEqualTo ""}) then {
            private _action = [
                format ["gmr_refill_%1", _x],
                format ["%1 [%2/%3]", _facts select ITEM_NAME, _facts select ITEM_ROUNDS, BELT_MAX],
                _facts select ITEM_PICTURE,
                {
                    params ["", "_player", "_params"];

                    [_player, "refillBelt", _params select 0, []] call FUNC(start);
                },
                {true},
                {},
                [_x]
            ] call ace_interact_menu_fnc_createAction;

            _actions pushBack [_action, [], _unit];
        };
    } forEach (keys ([_unit] call EFUNC(main,itemCounts)));

    _actions
};

// Unload: the belt items, each type with its belts.
private _beltTypes = createHashMap;

{
    private _facts = [_x] call EFUNC(main,itemInfo);

    if ((_facts select ITEM_KIND) == "belt") then {
        (_beltTypes getOrDefault [_facts select ITEM_BELT_TYPE, [], true]) pushBack _x;
    };
} forEach (keys ([_unit] call EFUNC(main,itemCounts)));

{
    private _type = _x;
    private _belts = _y;

    _belts sort false;

    private _shown = if (_limit > 0) then {_belts select [0, _limit]} else {_belts};

    private _children = _shown apply {
        private _facts = [_x] call EFUNC(main,itemInfo);
        private _action = [
            format ["gmr_unload_%1", _x],
            format ["[%1]", _facts select ITEM_ROUNDS],
            _facts select ITEM_PICTURE,
            {
                params ["", "_player", "_params"];

                [_player, "unloadBelt", _params select 0, []] call FUNC(start);
            },
            {true},
            {},
            [_x]
        ] call ace_interact_menu_fnc_createAction;

        [_action, [], _unit]
    };

    private _facts = [_belts select 0] call EFUNC(main,itemInfo);
    private _top = [
        format ["gmr_unload_%1", _type],
        getText (configFile >> "CfgWeapons" >> (_type select [0, count _type - 1]) >> "displayName"),
        _facts select ITEM_PICTURE,
        {},
        {true}
    ] call ace_interact_menu_fnc_createAction;

    _actions pushBack [_top, _children, _unit];
} forEach _beltTypes;

_actions
