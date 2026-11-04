// Warnings and errors go straight to the RPT rather than through CBA_fnc_log.
#define DEBUG_SYNCHRONOUS
#include "\x\cba\addons\main\script_macros_common.hpp"
#include "\x\cba\addons\xeh\script_xeh.hpp"

// Functions are compiled through CBA, which caches them and lets them be recompiled while testing with file patching.
#undef PREP
#define PREP(fncName) [QPATHTOF(functions\DOUBLES(fnc,fncName).sqf), QFUNC(fncName)] call CBA_fnc_compileFunction

// The unit the player controls, a unit taken over in Zeus included.
#define PLAYER_UNIT (missionNamespace getVariable ["ACE_player", player])

// The settings' categories in CBA's Addon Options.
#define CBA_SETTINGS_SERVER "GreenMag Rework - Server"
#define CBA_SETTINGS_CLIENT "GreenMag Rework - Client"

// Raised on the local machine after this mod changed a unit's magazines, so the reload guard's picture stays right.
#define EVENT_CHANGED "gmr_main_changed"

// The longest belt item there is (tools/generate_items.py).
#define BELT_MAX 200

// The fields of a magazine's facts (gmr_main_fnc_magazineInfo).
#define MAG_OK 0
#define MAG_CALIBER 1
#define MAG_VARIANT 2
#define MAG_BELT 3
#define MAG_CAPACITY 4
#define MAG_SPEEDLOAD 5
#define MAG_ROUND 6
#define MAG_BELT_TYPE 7
#define MAG_NAME 8
#define MAG_PICTURE 9

// The fields of our items' facts (gmr_main_fnc_itemInfo).
#define ITEM_KIND 0
#define ITEM_ROUNDS 1
#define ITEM_ROUND 2
#define ITEM_BELT_TYPE 3
#define ITEM_NAME 4
#define ITEM_PICTURE 5
#define ITEM_MASS 6
#define ITEM_CALIBER 7
#define ITEM_VARIANT 8
