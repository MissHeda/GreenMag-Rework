#include "script_component.hpp"

// Calibers and belts of 3CB Factions's magazines. Loads only when that mod is there.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"gmr_main", "UK3CB_Factions_Weapons2_AA12", "UK3CB_Factions_Weapons2_AEK971", "UK3CB_Factions_Weapons2_AK12", "UK3CB_Factions_Weapons2_AR18", "UK3CB_Factions_Weapons2_P320", "UK3CB_Factions_Weapons2_RK62", "UK3CB_Factions_Weapons2_Saiga", "UK3CB_Factions_Weapons2_TMG", "UK3CB_Factions_Weapons_ACR", "UK3CB_Factions_Weapons_AK47", "UK3CB_Factions_Weapons_AR10", "UK3CB_Factions_Weapons_AUG", "UK3CB_Factions_Weapons_BHP", "UK3CB_Factions_Weapons_Bren", "UK3CB_Factions_Weapons_CGM45", "UK3CB_Factions_Weapons_CZ75", "UK3CB_Factions_Weapons_Enfield", "UK3CB_Factions_Weapons_FAMAS", "UK3CB_Factions_Weapons_FNFAL", "UK3CB_Factions_Weapons_G3", "UK3CB_Factions_Weapons_G36", "UK3CB_Factions_Weapons_HS50", "UK3CB_Factions_Weapons_Khaybar", "UK3CB_Factions_Weapons_M14", "UK3CB_Factions_Weapons_M16", "UK3CB_Factions_Weapons_MAT49", "UK3CB_Factions_Weapons_MG3", "UK3CB_Factions_Weapons_MP5", "UK3CB_Factions_Weapons_P90", "UK3CB_Factions_Weapons_PC9_ZOAF", "UK3CB_Factions_Weapons_QB", "UK3CB_Factions_Weapons_RPD", "UK3CB_Factions_Weapons_RPK", "UK3CB_Factions_Weapons_Sten", "UK3CB_Factions_Weapons_STGW", "UK3CB_Factions_Weapons_SVD_OLD", "UK3CB_Factions_Weapons_Tec9", "UK3CB_Factions_Weapons_UKM", "UK3CB_Factions_Weapons_USP", "UK3CB_Factions_Weapons_Uzi"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgMagazines.hpp"
