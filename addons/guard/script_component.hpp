#define COMPONENT guard
#define COMPONENT_BEAUTIFIED GMR - Guard
#include "\z\gmr\addons\main\script_mod.hpp"
#include "\z\gmr\addons\main\script_macros.hpp"

// How often the picture of the player's magazines is renewed, in seconds.
#define WATCH_INTERVAL 0.5

// How long after a reload the inventory is looked at: an empty magazine only has to be added, a partly used one has
// to have had its chance to come back by itself, also over the network.
#define CHECK_DELAY_EMPTY 0.5
#define CHECK_DELAY_PARTIAL 1.5

// A magazine leaving an empty weapon this soon after a reload belongs to that reload.
#define RELOAD_QUIET_TIME 3
