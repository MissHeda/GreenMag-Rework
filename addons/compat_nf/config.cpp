#include "script_component.hpp"

// Calibers and belts of Northern Fronts's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "NORTH_StaticWeapons_cfg", "NORTH_vehicles_cfg", "NORTH_weapons_cfg"};
        skipWhenMissingDependencies = 1;
        author = "Davidaf";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
