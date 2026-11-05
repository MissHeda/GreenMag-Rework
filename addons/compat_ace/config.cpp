#include "script_component.hpp"

// Loads only when ACE is there: an addon whose required addons are missing is skipped, and the mod works without it
// through dragging and the inventory's context menu.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {
            "gmr_handling",
            "ace_arsenal",
            "ace_common",
            "ace_interact_menu",
            "ace_interaction",
            "ace_magazinerepack",
            "ace_reload"
        };
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgEventHandlers.hpp"
#include "CfgSounds.hpp"
#include "CfgVehicles.hpp"
