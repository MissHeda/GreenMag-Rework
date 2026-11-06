#include "script_component.hpp"
#include "round_path.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// Numbers the operations, so a late timeout can tell whether its operation is still the running one.
GVAR(opCounter) = 0;

// Where the round in the right hand is through the loading gesture (tools/anim/build_load_gesture.py).
GVAR(roundPath) = ROUND_PATH;
GVAR(roundPathTop) = ROUND_PATH_TOP;

// Whether the loading gesture is shown for the running operation (fnc_animTick).
GVAR(animPlaying) = false;

// Dragging ammunition onto a magazine in the inventory (fnc_watchDrag).
GVAR(dragWatch) = -1;
GVAR(dragStart) = [];
GVAR(dragDown) = false;

ADDON = true;
