#include "script_component.hpp"

class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {
            "gmr_main",
            "gmr_items",
            "A3_Anims_F"
        };
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgEventHandlers.hpp"
#include "CfgGestures.hpp"
#include "CfgSounds.hpp"
