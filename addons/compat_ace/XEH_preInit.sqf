#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The view of the ammunition tabs picked in the sort list (fnc_arsenalViews): "round", "pack", "belt" or "all".
GVAR(arsenalView) = "all";
GVAR(viewsBusy) = false;

// Whether the calibers the loaded mods use are being counted or have been (fnc_countCalibers).
GVAR(countingCalibers) = false;

// Tabs of their own in ACE Arsenal, which takes these items out of its Misc list. Other mods' items join them with
// gmr_arsenal = 1 in their config (ammo cans, bandoliers and the like); ACE keeps only those that are misc items.
private _items = [
    #include "\z\gmr\addons\items\cfg\public_classes.hpp"
];

{
    _items append ((toString {getNumber (_x >> "gmr_arsenal") == 1 && {getNumber (_x >> "scope") == 2}} configClasses (configFile >> _x)) apply {configName _x});
} forEach ["CfgWeapons", "CfgMagazines"];

_items = _items arrayIntersect _items;

// Two tabs, as ACE has two for magazines: the ammunition the weapons the unit carries take, then all of it.
GVAR(arsenalSlotFitting) = [
    _items,
    LLSTRING(ArsenalTabFitting),
    QPATHTOF(data\action_round.paa),
    -1,
    true
] call ace_arsenal_fnc_addRightPanelButton;

GVAR(arsenalSlot) = [
    _items,
    LLSTRING(ArsenalTab),
    QPATHTOF(data\action_ammo.paa),
    -1,
    true
] call ace_arsenal_fnc_addRightPanelButton;

// The arsenal's tabs are put in place and its lists filtered as ACE fills them. Set up here and not once the mission
// has started, so it also holds in the editor's arsenal, where none runs.
if (hasInterface) then {
    // ACE builds its side buttons as this event goes out, so they are moved a frame later.
    ["ace_arsenal_rightPanelContainer", {
        [FUNC(arrangeArsenal), _this] call FUNC(nextFrame);
    }] call CBA_fnc_addEventHandler;

    ["ace_arsenal_rightPanelFilled", {
        params ["_display", "", "_button"];

        if !(_button in [TAB_FITTING, TAB_ALL]) exitWith {};

        [_display] call FUNC(arsenalFilter);
        [_display, _button == TAB_FITTING] call FUNC(arsenalViews);

        // In the tab of the fitting ammunition everything fits.
        if (_button == TAB_ALL && {EGVAR(main,arsenalHighlight)}) then {
            [_display] call FUNC(arsenalHighlight);
        };
    }] call CBA_fnc_addEventHandler;
};

ADDON = true;
