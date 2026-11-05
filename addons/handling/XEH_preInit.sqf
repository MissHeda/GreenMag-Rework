#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// Numbers the operations, so a late timeout can tell whether its operation is still the running one.
GVAR(opCounter) = 0;

// Whether the loading gesture is shown for the running operation (fnc_animTick).
GVAR(animPlaying) = false;

// Dragging ammunition onto a magazine in the inventory (fnc_watchDrag).
GVAR(dragWatch) = -1;
GVAR(dragStart) = [];
GVAR(dragDown) = false;

ADDON = true;
