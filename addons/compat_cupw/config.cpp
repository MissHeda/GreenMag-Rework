#include "script_component.hpp"

// Calibers and belts of CUP Weapons's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "CUP_Weapons_Ammunition", "CUP_Weapons_DynamicLoadout", "CUP_Weapons_Galil", "CUP_Weapons_M17", "CUP_Weapons_P30"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
