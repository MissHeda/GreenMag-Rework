#include "script_component.hpp"

// Calibers and belts of IFA3 AIO's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "WW2_Assets_c_Vehicles_Weapons_c", "WW2_Assets_c_Weapons_InfantryWeapons_c"};
        skipWhenMissingDependencies = 1;
        author = "Davidaf";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
