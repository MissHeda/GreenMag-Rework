#include "script_component.hpp"

// Loads only when the EFAK framework is there (Enhanced Utility Pouches brings it along, Enhanced First Aid Kits too):
// ammunition in a carried pouch or kit is used from there, without moving it to the inventory first.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "efak_core"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgEventHandlers.hpp"
