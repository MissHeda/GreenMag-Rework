#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The player's magazines as last seen outside a reload (fnc_watch): [unit, snapshot].
GVAR(picture) = [objNull, createHashMap];

// [weapon, magazine class] of the player's weapons that hold an empty magazine (fnc_watch).
GVAR(emptySlots) = [];

// When the player's unit last reloaded.
GVAR(lastReload) = -100;

ADDON = true;
