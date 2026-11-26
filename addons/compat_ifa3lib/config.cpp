#include "script_component.hpp"

// Calibers and belts of IFA3 Liberation's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "if_weapon_c", "ifa3_box_repack", "ifa3_comp", "IFA3_PPS43", "KA_dagger", "Katana", "MJ_AVS36", "weap_StreetYou_ptrs"};
        skipWhenMissingDependencies = 1;
        author = "Davidaf";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
