#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// This mod's items in the unit's pouches and kits count as carried, and are used up from there once its uniform, vest and
// backpack have none left (gmr_main_fnc_itemCounts, gmr_main_fnc_removeItem).
EGVAR(main,itemSources) pushBack [FUNC(kitCounts), FUNC(kitRemove)];

ADDON = true;
