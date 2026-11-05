#define COMPONENT handling
#define COMPONENT_BEAUTIFIED GMR - Handling
#include "\z\gmr\addons\main\script_mod.hpp"
#include "\z\gmr\addons\main\script_macros.hpp"

// A hold action nobody starts leaves the scroll menu after this many seconds, so it cannot wait around for a fight.
#define HOLD_TIMEOUT 30

// A belt moves this many rounds per second, and takes at least these many seconds.
#define BELT_ROUNDS_PER_SECOND 6.67
#define BELT_MIN_TIME_LOAD 10
#define BELT_MIN_TIME_UNLOAD 8

// The lists of the unit's own containers in the game's inventory.
#define IDC_LIST_UNIFORM 633
#define IDC_LIST_VEST 638
#define IDC_LIST_BACKPACK 619

// The hold action draws its ring this big; the picture inside it is smaller.
#define HOLD_RING_SIZE 3
#define HOLD_ICON_SIZE 1.5

// The magazine as one holds it to load it: across the body, its broad side to the front, its front towards the right
// hand, its back in the left palm, the fingers around its far side and front, the thumb on its near side. From the
// unit's "lefthand" point to the middle of its back (right, forward, up), the depth the hand is shaped around, the way
// its front points, up, and its broad side. tools/anim/build_load_gesture.py solves the hand for these and prints the
// first of them.
#define MAG_FROM_HAND [-0.0127, -0.0506, -0.0159]
#define MAG_DEPTH 0.065
#define MAG_DIR [0.90, 0.44, 0]
#define MAG_UP [0, 0, 1]
#define MAG_ACROSS [0.44, -0.90, 0]

// Beyond this nobody makes out a magazine in a hand.
#define MAG_VISIBLE_RANGE 300

// A weapon index no weapon has: the game puts the weapon away.
#define NO_WEAPON_MODE 299

// How often the loading gesture looks at its operation.
#define ANIM_CHECK_INTERVAL 0.05

