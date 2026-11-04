#include "script_component.hpp"

class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {
            "gmr_main"
        };
        author = "Miss Heda";
        VERSION_CONFIG;
    };
};

#include "CfgEventHandlers.hpp"
