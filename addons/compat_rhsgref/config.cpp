#include "script_component.hpp"

// Calibers and belts of RHS: GREF's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "rhsgref_c_weapons"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
