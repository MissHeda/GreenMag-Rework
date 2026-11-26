#include "script_component.hpp"

// Calibers and belts of CSA38's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "CSA38II_weapons2_c", "csa38ii_weapons_c"};
        skipWhenMissingDependencies = 1;
        author = "Davidaf";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
