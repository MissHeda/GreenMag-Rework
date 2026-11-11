#include "script_component.hpp"

// Calibers and belts of NIArms's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "hlcweapons_aks", "hlcweapons_AUG", "hlcweapons_core", "hlcweapons_g3", "hlcweapons_G36", "hlcweapons_M134", "hlcweapons_m14", "hlcweapons_M16A2", "hlcweapons_MG3s", "hlcweapons_mp5", "hlcweapons_SAW", "hlcweapons_SCAR", "hlcweapons_SG550", "hlcweapons_stgw57", "niaweapons_226", "niaweapons_C96", "sp_fwa_mas"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
