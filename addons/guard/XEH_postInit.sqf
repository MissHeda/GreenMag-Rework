#include "script_component.hpp"

// Runs where the unit is local, also on a server or headless client for its AI.
["CAManBase", "Reloaded", {_this call FUNC(onReloaded)}] call CBA_fnc_addClassEventHandler;

if (!hasInterface) exitWith {};

// This mod changed the magazines itself: the picture is renewed at once, no reload is looked for in the change.
[EVENT_CHANGED, {
    private _unit = PLAYER_UNIT;

    GVAR(picture) = [_unit, [_unit] call FUNC(snapshot)];
}] call CBA_fnc_addEventHandler;

[FUNC(watch), WATCH_INTERVAL] call CBA_fnc_addPerFrameHandler;
