#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The children of "Combine belts": per belt type with two or more belts, combine all of them, or pick one belt and
 * then the one to join it with.
 *
 * Arguments:
 * 0: Player <OBJECT>
 *
 * Return Value:
 * ACE actions <ARRAY>
 *
 * Example:
 * [player] call gmr_handling_fnc_menuCombine;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]]];

private _counts = [_unit] call EFUNC(main,itemCounts);
private _types = createHashMap;

{
    private _facts = [_x] call EFUNC(main,itemInfo);

    if ((_facts select ITEM_KIND) == "belt") then {
        _types set [_facts select ITEM_BELT_TYPE, (_types getOrDefault [_facts select ITEM_BELT_TYPE, 0]) + _y];
    };
} forEach _counts;

private _actions = [];

{
    private _type = _x;

    if (_y >= 2) then {
        // One entry per length; a belt can only join a second one of its length when there are two.
        private _belts = [_unit, _type] call EFUNC(main,beltItems);
        private _lengths = _belts arrayIntersect _belts;
        private _picture = ([(_lengths select 0) select 0] call EFUNC(main,itemInfo)) select ITEM_PICTURE;

        private _children = _lengths apply {
            _x params ["_first", "_firstLength"];

            private _partners = _lengths select {
                (_x select 0) != _first || {{(_x select 0) == _first} count _belts >= 2}
            };

            private _grandchildren = _partners apply {
                _x params ["_second", "_secondLength"];

                private _action = [
                    format ["gmr_combine_%1_%2", _first, _second],
                    format [LLSTRING(CombineWith), _secondLength],
                    _picture,
                    {
                        params ["", "_player", "_params"];
                        _params params ["_type", "_first", "_second"];

                        [_player, _type, _first, _second] call FUNC(combineBelts);
                    },
                    {true},
                    {},
                    [_type, _first, _second]
                ] call ace_interact_menu_fnc_createAction;

                [_action, [], _unit]
            };

            private _action = [
                format ["gmr_combine_%1", _first],
                format ["[%1]", _firstLength],
                _picture,
                {},
                {true}
            ] call ace_interact_menu_fnc_createAction;

            [_action, _grandchildren, _unit]
        };

        private _all = [
            format ["gmr_combine_all_%1", _type],
            LLSTRING(CombineAll),
            _picture,
            {
                params ["", "_player", "_params"];

                [_player, _params select 0] call FUNC(combineBelts);
            },
            {true},
            {},
            [_type]
        ] call ace_interact_menu_fnc_createAction;

        private _top = [
            format ["gmr_combine_type_%1", _type],
            getText (configFile >> "CfgWeapons" >> (_type select [0, count _type - 1]) >> "displayName"),
            _picture,
            {},
            {true}
        ] call ace_interact_menu_fnc_createAction;

        _actions pushBack [_top, [[_all, [], _unit]] + _children, _unit];
    };
} forEach _types;

_actions
