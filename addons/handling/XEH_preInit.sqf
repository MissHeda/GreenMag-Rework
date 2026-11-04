#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// Numbers the operations, so a late timeout can tell whether its operation is still the running one.
GVAR(opCounter) = 0;

ADDON = true;
