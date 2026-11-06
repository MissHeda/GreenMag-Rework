#define COMPONENT handling
#define COMPONENT_BEAUTIFIED GMR - Handling
#include "\z\gmr\addons\main\script_mod.hpp"
#include "\z\gmr\addons\main\script_macros.hpp"

// A loading nobody starts by holding the key goes away after this many seconds, so it cannot wait around for a fight.
#define HOLD_TIMEOUT 30

// A belt moves this many rounds per second, and takes at least these many seconds.
#define BELT_ROUNDS_PER_SECOND 6.67
#define BELT_MIN_TIME_LOAD 10
#define BELT_MIN_TIME_UNLOAD 8

// The lists of the unit's own containers in the game's inventory.
#define IDC_LIST_UNIFORM 633
#define IDC_LIST_VEST 638
#define IDC_LIST_BACKPACK 619

// The display while loading (fnc_uiCreate): place and size in screen units, its colours, and the most segments in its strip.
#define UI_WIDTH 0.46
#define UI_PAD 0.014
#define UI_GAP 0.012
#define UI_TILE_HEIGHT 0.07
#define UI_TOP 0.78
#define UI_RADIUS 0.014
#define UI_STRIP_HEIGHT 0.014
#define UI_MAX_SEGMENTS 50
#define UI_SPARK_TIME 0.22
#define UI_HIT_TIME 0.3
#define UI_PANEL_COLOR [0.086, 0.094, 0.114, 0.88]
#define UI_TILE_COLOR [1, 1, 1, 0.07]
#define UI_ON_COLOR [0.42, 0.92, 0.42, 1]
#define UI_OLD_COLOR [0.20, 0.46, 0.22, 1]
#define UI_OFF_COLOR [1, 1, 1, 0.10]
#define UI_ZONE_COLOR [0.42, 0.92, 0.42, 0.28]
#define UI_ROUND_COLOR [0.96, 0.72, 0.30, 1]
#define UI_MISS_COLOR [1, 0.3, 0.2, 1]

// The minigame: its track, how long a miss holds the hand, the opening's share of the track, and the fastest a round may fly.
#define UI_GAME_HEIGHT 0.044
#define UI_PROMPT_HEIGHT 0.03
#define UI_TRACK_HEIGHT 0.006
#define UI_ZONE_HEIGHT 0.026
#define UI_STACK_MAX 12

// The classic display: the game's hold-action ring, its width in screen units and how far below the middle it sits.
#define UI_RING_SIZE 0.09
#define UI_RING_DROP 0.06
#define GAME_MISS_STALL 0.5
#define GAME_ZONE_START 0.30
#define GAME_ZONE_SHRINK 0.02
#define GAME_ZONE_MIN 0.12
#define GAME_MIN_BEAT 0.25

// The magazine as one holds it to load it: across the body, its broad side to the front, its front towards the right
// hand, its back in the left palm, the fingers around its far side and front, the thumb on its near side. From the
// unit's "lefthand" point to the middle of its back (right, forward, up), the depth the hand is shaped around, the way
// its front points, up, and its broad side. tools/anim/build_load_gesture.py solves the hand for these and prints the
// first of them.
#define MAG_FROM_HAND [-0.0264, -0.0337, -0.0094]
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

