#include "script_component.hpp"

// Calibers and belts of BWMod's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "bwa3_g28", "bwa3_g29", "bwa3_g36", "bwa3_g82", "bwa3_mg3", "bwa3_mg4", "bwa3_mg5", "bwa3_mp7", "bwa3_p12", "bwa3_p8", "bwa3_pylon", "bwa3_weapons"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
