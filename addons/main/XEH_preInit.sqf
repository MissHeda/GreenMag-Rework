#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// What has been worked out about a magazine or item class - looked up once, on first use, never all at once.
GVAR(magazineCache) = createHashMap;
GVAR(itemCache) = createHashMap;

// Magazines declared belts at runtime (fnc_registerBelts), lowercase.
GVAR(registeredBelts) = createHashMap;

// The calibers as data: [id, tokens, [[variant id, tokens], ...]]. Any mod can add classes to gmr_calibers.
GVAR(calibers) = ("true" configClasses (configFile >> "gmr_calibers")) apply {
    [
        configName _x,
        getArray (_x >> "tokens"),
        ("true" configClasses (_x >> "variants")) apply {[configName _x, getArray (_x >> "tokens")]}
    ]
};

#include "initSettings.inc.sqf"

ADDON = true;
