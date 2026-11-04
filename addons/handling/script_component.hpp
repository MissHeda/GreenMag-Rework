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

// Any weapon slot off the weapons: the game puts the weapon away.
#define NO_WEAPON_MODE 900
