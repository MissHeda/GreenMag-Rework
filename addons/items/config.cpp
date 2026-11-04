#include "script_component.hpp"

class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {
            #include "cfg\public_classes.hpp"
        };
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {
            "gmr_main"
        };
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "cfg\calibers.hpp"
#include "CfgWeapons.hpp"
