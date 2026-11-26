#define COMPONENT compat_ace
#define COMPONENT_BEAUTIFIED GMR - ACE
#include "\z\gmr\addons\main\script_mod.hpp"
#include "\z\gmr\addons\main\script_macros.hpp"

// The side buttons of ACE Arsenal, each with its background at the id before it.
#define ARSENAL_BUTTON_MAG 30
#define ARSENAL_BUTTON_MAG_ALL 32
#define ARSENAL_BUTTON_THROW 34
#define ARSENAL_BUTTON_PUT 36
#define ARSENAL_BUTTON_MISC 38

// This mod's two tabs there: the ammunition the unit's weapons take, and all of it. A tab ACE had no slot for is -1.
#define TAB_FITTING (61 + GVAR(arsenalSlotFitting) * 2)
#define TAB_ALL (61 + GVAR(arsenalSlot) * 2)

// The list of items, and the colour of what fits one of the unit's weapons.
#define ARSENAL_ITEM_LIST 15
#define ARSENAL_SORT 17
#define ARSENAL_FITS_COLOR [0.45, 0.95, 0.45, 1]

// As long as ACE takes to link a box into a machine gun.
#define LINK_BELT_TIME 4
