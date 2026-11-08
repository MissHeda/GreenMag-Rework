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

// Whether the load key (CBA keybind gmr_handling_keyLoad) is down right now, read by fnc_tick.
GVAR(keyHeld) = false;

if (hasInterface) then {
    // The keys of the loading and its minigame, set in the CBA controls. They only take the key while something loads.
    [KEYBIND_CATEGORY, QGVAR(keyLoad), [LLSTRING(Key_Load), LLSTRING(Key_Load_Desc)], {
        GVAR(keyHeld) = true;
        !isNil QGVAR(op)
    }, {
        GVAR(keyHeld) = false;
        !isNil QGVAR(op)
    }, [57, [false, false, false]]] call CBA_fnc_addKeybind; // Space

    [KEYBIND_CATEGORY, QGVAR(keyCancel), [LLSTRING(Key_Cancel), LLSTRING(Key_Cancel_Desc)], {
        if (isNil QGVAR(op)) exitWith {false};

        [false] call FUNC(finish);
        true
    }, {}, [14, [false, false, false]]] call CBA_fnc_addKeybind; // Backspace
};

ADDON = true;
