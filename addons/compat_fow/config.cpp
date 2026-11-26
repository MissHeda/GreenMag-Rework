#include "script_component.hpp"

// Calibers and belts of Faces of War's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "fow_veh_weapons_c", "fow_weapons_c"};
        skipWhenMissingDependencies = 1;
        author = "Davidaf";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
