// Settings are ordered by topic, and within a topic numbers, then switches, then lists, then text boxes.

private _timing = LLSTRING(Topic_Timing);
private _rules = LLSTRING(Topic_Rules);
private _magazines = LLSTRING(Topic_Magazines);
private _menu = LLSTRING(Topic_Menu);
private _arsenal = LLSTRING(Topic_Arsenal);

// What a magazine or belt counts as depends on these two, so what is known about magazines starts over.
private _fnc_resetFacts = {GVAR(magazineCache) = createHashMap};

// ----- Server: timing -----
// Numbers
[
    QGVAR(timePerRound), "SLIDER", [LLSTRING(Setting_TimePerRound), LLSTRING(Setting_TimePerRound_Desc)],
    [CBA_SETTINGS_SERVER, _timing], [0.05, 3, 1, 2], 1
] call CBA_fnc_addSetting;

[
    QGVAR(beltTimeFactor), "SLIDER", [LLSTRING(Setting_BeltTimeFactor), LLSTRING(Setting_BeltTimeFactor_Desc)],
    [CBA_SETTINGS_SERVER, _timing], [0.1, 3, 1, 2], 1
] call CBA_fnc_addSetting;

[
    QGVAR(speedloaderFactor), "SLIDER", [LLSTRING(Setting_SpeedloaderFactor), LLSTRING(Setting_SpeedloaderFactor_Desc)],
    [CBA_SETTINGS_SERVER, _timing], [0.1, 1, 0.5, 2], 1
] call CBA_fnc_addSetting;

// ----- Server: rules -----
// Switches
[
    QGVAR(enabled), "CHECKBOX", [LLSTRING(Setting_Enabled), LLSTRING(Setting_Enabled_Desc)],
    [CBA_SETTINGS_SERVER, _rules], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(beltsEnabled), "CHECKBOX", [LLSTRING(Setting_BeltsEnabled), LLSTRING(Setting_BeltsEnabled_Desc)],
    [CBA_SETTINGS_SERVER, _rules], true, 1, _fnc_resetFacts
] call CBA_fnc_addSetting;

[
    QGVAR(freeRefill), "CHECKBOX", [LLSTRING(Setting_FreeRefill), LLSTRING(Setting_FreeRefill_Desc)],
    [CBA_SETTINGS_SERVER, _rules], false, 1
] call CBA_fnc_addSetting;

[
    QGVAR(allowPacking), "CHECKBOX", [LLSTRING(Setting_AllowPacking), LLSTRING(Setting_AllowPacking_Desc)],
    [CBA_SETTINGS_SERVER, _rules], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(packsMustOpen), "CHECKBOX", [LLSTRING(Setting_PacksMustOpen), LLSTRING(Setting_PacksMustOpen_Desc)],
    [CBA_SETTINGS_SERVER, _rules], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(disableAceRepack), "CHECKBOX", [LLSTRING(Setting_DisableAceRepack), LLSTRING(Setting_DisableAceRepack_Desc)],
    [CBA_SETTINGS_SERVER, _rules], true, 1
] call CBA_fnc_addSetting;

// Lists
[
    QGVAR(advancedAmmo), "LIST", [LLSTRING(Setting_AmmoSystem), LLSTRING(Setting_AmmoSystem_Desc)],
    [CBA_SETTINGS_SERVER, _rules],
    [[false, true], [LLSTRING(Setting_AmmoSystem_Simple), LLSTRING(Setting_AmmoSystem_Advanced)], 0], 1, _fnc_resetFacts
] call CBA_fnc_addSetting;

// Text boxes
[
    QGVAR(ammoRules), "EDITBOX", [LLSTRING(Setting_AmmoRules), LLSTRING(Setting_AmmoRules_Desc)],
    [CBA_SETTINGS_SERVER, _rules], "", 1, {call FUNC(parseAmmoRules)}
] call CBA_fnc_addSetting;

// ----- Server: magazines -----
// Switches
[
    QGVAR(keepEmpties), "CHECKBOX", [LLSTRING(Setting_KeepEmpties), LLSTRING(Setting_KeepEmpties_Desc)],
    [CBA_SETTINGS_SERVER, _magazines], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(emptiesForAI), "CHECKBOX", [LLSTRING(Setting_EmptiesForAI), LLSTRING(Setting_EmptiesForAI_Desc)],
    [CBA_SETTINGS_SERVER, _magazines], false, 1
] call CBA_fnc_addSetting;

[
    QGVAR(reloadGuard), "CHECKBOX", [LLSTRING(Setting_ReloadGuard), LLSTRING(Setting_ReloadGuard_Desc)],
    [CBA_SETTINGS_SERVER, _magazines], true, 1
] call CBA_fnc_addSetting;

// Lists
[
    QGVAR(emptyContainer), "LIST", [LLSTRING(Setting_EmptyContainer), LLSTRING(Setting_EmptyContainer_Desc)],
    [CBA_SETTINGS_SERVER, _magazines],
    [
        [0, 1, 2, 3],
        [LLSTRING(Setting_Container_Auto), LLSTRING(Setting_Container_Uniform), LLSTRING(Setting_Container_Vest), LLSTRING(Setting_Container_Backpack)],
        0
    ], 1
] call CBA_fnc_addSetting;

// ----- Server: what ACE Arsenal shows -----
// Switches
[
    QGVAR(arsenalBelts), "CHECKBOX", [LLSTRING(Setting_ArsenalBelts), LLSTRING(Setting_ArsenalBelts_Desc)],
    [CBA_SETTINGS_SERVER, _arsenal], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(arsenalPacks), "CHECKBOX", [LLSTRING(Setting_ArsenalPacks), LLSTRING(Setting_ArsenalPacks_Desc)],
    [CBA_SETTINGS_SERVER, _arsenal], true, 1
] call CBA_fnc_addSetting;

[
    QGVAR(arsenalRounds), "CHECKBOX", [LLSTRING(Setting_ArsenalRounds), LLSTRING(Setting_ArsenalRounds_Desc)],
    [CBA_SETTINGS_SERVER, _arsenal], false, 1
] call CBA_fnc_addSetting;

// ----- Client: menu -----
// Numbers
[
    QGVAR(maxMagazines), "SLIDER", [LLSTRING(Setting_MaxMagazines), LLSTRING(Setting_MaxMagazines_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], [0, 10, 0, 0], 0
] call CBA_fnc_addSetting;

// Switches
[
    QGVAR(arsenalHighlight), "CHECKBOX", [LLSTRING(Setting_ArsenalHighlight), LLSTRING(Setting_ArsenalHighlight_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(dragToLoad), "CHECKBOX", [LLSTRING(Setting_DragToLoad), LLSTRING(Setting_DragToLoad_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(holdToLoad), "CHECKBOX", [LLSTRING(Setting_HoldToLoad), LLSTRING(Setting_HoldToLoad_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(holster), "CHECKBOX", [LLSTRING(Setting_Holster), LLSTRING(Setting_Holster_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(loadGame), "CHECKBOX", [LLSTRING(Setting_LoadGame), LLSTRING(Setting_LoadGame_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], false, 0
] call CBA_fnc_addSetting;

[
    QGVAR(loadAnimation), "CHECKBOX", [LLSTRING(Setting_LoadAnimation), LLSTRING(Setting_LoadAnimation_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(roundCounter), "CHECKBOX", [LLSTRING(Setting_RoundCounter), LLSTRING(Setting_RoundCounter_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(sounds), "CHECKBOX", [LLSTRING(Setting_Sounds), LLSTRING(Setting_Sounds_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], true, 0
] call CBA_fnc_addSetting;

[
    QGVAR(guardNotice), "CHECKBOX", [LLSTRING(Setting_GuardNotice), LLSTRING(Setting_GuardNotice_Desc)],
    [CBA_SETTINGS_CLIENT, _menu], false, 0
] call CBA_fnc_addSetting;
