#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// A tab of its own in ACE Arsenal, which takes these items out of its Misc list.
GVAR(arsenalSlot) = [
    [
        #include "\z\gmr\addons\items\cfg\public_classes.hpp"
    ],
    LLSTRING(ArsenalTab),
    QPATHTOF(data\action_ammo.paa),
    -1,
    true
] call ace_arsenal_fnc_addRightPanelButton;

ADDON = true;
