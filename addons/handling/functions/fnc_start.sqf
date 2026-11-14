#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Sets up loading or unloading and shows it (fnc_uiCreate). With "Hold to load" it waits for the key to be held, and leaves
 * on its own if nobody does; otherwise, and in the minigame, it starts at once. One clock runs it all (fnc_tick). Nothing in
 * the inventory changes before the end (fnc_finish).
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: "fill", "unload", "unloadBelt" or "refillBelt" (loose rounds and clips of its kind onto a belt item) <STRING>
 * 2: Magazine class, or the belt item for "unloadBelt" and "refillBelt" <STRING>
 * 3: The rounds of each magazine, in the order to work through them <ARRAY>
 * 4: Ammunition to refill from, a round class or belt type; "" chooses by the caliber (optional, default: "") <STRING>
 * 5: Where the rounds come from: "loose" (rounds dragged onto the magazine), "clips" (a clip or carton of clips dragged
 *    onto it) or "auto" (the menus: whole clips when the speedloader takes them, else loose rounds and then clips)
 *    (optional, default: "auto") <STRING>
 *
 * Return Value:
 * Whether it started <BOOL>
 *
 * Example:
 * [player, "fill", "30Rnd_556x45_Stanag", [12]] call gmr_handling_fnc_start;
 *
 * Public: No
 */

params [
    ["_unit", objNull, [objNull]], ["_kind", "fill", [""]], ["_class", "", [""]], ["_amounts", [], [[]]], ["_ammunition", "", [""]],
    ["_from", "auto", [""]]
];

if (!EGVAR(main,enabled) || {!alive _unit}) exitWith {false};

// One that should have ended by now was cut off by something else, a respawn for one.
if (!isNil QGVAR(op)) then {
    if (
        (GVAR(op) get "unit") isNotEqualTo _unit
        || {!alive (GVAR(op) get "unit")}
        || {CBA_missionTime > (GVAR(op) get "seen") + 5}
    ) then {
        [false] call FUNC(finish);
    };
};

if (!isNil QGVAR(op)) exitWith {
    hintSilent LLSTRING(Hint_Busy);
    false
};

private _belt = false;
private _need = 0;
private _speedload = false;
private _source = "";
private _name = "";
private _picture = "";
private _becomes = "";
private _refused = "";
private _capacity = 0;

if (_kind == "unloadBelt") then {
    private _facts = [_class] call EFUNC(main,itemInfo);

    _belt = true;
    _need = _facts select ITEM_ROUNDS;
    _capacity = _need;
    _name = _facts select ITEM_NAME;
    _picture = _facts select ITEM_PICTURE;
} else {
    if (_kind == "refillBelt") exitWith {
        private _facts = [_class] call EFUNC(main,itemInfo);

        _belt = true;

        // Its own rounds, or universal ones (setting); a dragged item brings its own choice in _ammunition.
        _source = if (_ammunition isEqualTo "") then {
            ([_unit, _class, ""] call FUNC(beltRefillSource)) params ["_round", "", "_why"];

            _refused = _why;
            _round
        } else {
            _ammunition
        };
        _capacity = BELT_MAX;
        _need = BELT_MAX - (_facts select ITEM_ROUNDS);
        _amounts = [_facts select ITEM_ROUNDS];
        _name = _facts select ITEM_NAME;
        _picture = _facts select ITEM_PICTURE;
    };

    private _facts = [_class] call EFUNC(main,magazineInfo);

    _capacity = _facts select MAG_CAPACITY;
    _belt = _facts select MAG_BELT;
    _name = _facts select MAG_NAME;
    _picture = _facts select MAG_PICTURE;
    _speedload = _facts select MAG_SPEEDLOAD;
    _source = [_facts select MAG_ROUND, _facts select MAG_BELT_TYPE] select _belt;

    // A magazine of no known caliber unloads into universal ammunition.
    if (_source isEqualTo "") then {
        _source = [UNIVERSAL_ROUND, UNIVERSAL_BELT] select _belt;
    };

    if (_kind == "fill") then {
        _source = [_ammunition, [_unit, _class] call FUNC(ammoSource)] select (_ammunition isEqualTo "");

        // What does not take this ammunition stays out, and says why if that leaves nothing.
        if (!EGVAR(main,freeRefill)) then {
            _amounts = _amounts select {
                ([_class, _x, _source] call FUNC(loadRule)) params ["_target", "_why"];

                if (_target isEqualTo "") then {
                    _refused = _why;
                } else {
                    if (_target != _class) then {
                        _becomes = _target;
                    };
                };

                _target isNotEqualTo ""
            };

            if (_amounts isNotEqualTo []) then {
                _refused = "";
            };
        };

        {_need = _need + (_capacity - _x)} forEach _amounts;
    } else {
        {_need = _need + _x} forEach _amounts;
    };
};

private _counts = [_unit] call EFUNC(main,itemCounts);

// Rounds on stripper clips count as rounds. Where they come from is the player's choice: what was dragged onto the
// magazine, or from the menus whole clips when the speedloader presses them in, else loose rounds first (fnc_takeRounds).
private _clips = [];
private _clipRounds = 0;
private _loose = _counts getOrDefault [_source, 0];

if ((_kind == "fill" && {!_belt} || {_kind == "refillBelt"}) && {_from != "loose"}) then {
    _clips = [_unit, _source] call FUNC(clipsOf);
    {_clipRounds = _clipRounds + (_x select 1) * (_x select 2)} forEach _clips;
};

// What the speedloader does (setting): 0 whole clips at once, 1 every loose round faster, 2 both.
private _speedloader = _kind == "fill" && {_speedload} && {"gmr_speedloader" in _counts};
private _clipsWhole = _speedloader && {_clips isNotEqualTo []} && {EGVAR(main,speedloaderMode) != 1};

// From the menus: whole clips whenever the speedloader takes them, ten rounds at a time; else loose rounds first.
if (_from == "auto") then {
    _from = ["mixed", "clips"] select _clipsWhole;
};

private _clipLoading = _clipsWhole && {_from == "clips"};
private _looseBoost = [1, EGVAR(main,speedloaderLooseFactor)] select (_speedloader && {EGVAR(main,speedloaderMode) != 0});

if (_kind in ["fill", "refillBelt"] && {!EGVAR(main,freeRefill) || {_kind == "refillBelt"}}) then {
    private _have = 0;

    if (_belt && {_kind == "fill"}) then {
        if (_source isNotEqualTo "") then {
            {_have = _have + (_x select 1)} forEach ([_unit, _source] call EFUNC(main,beltItems));
        };
    } else {
        _have = switch (_from) do {
            case "loose": {_loose};
            case "clips": {_clipRounds};
            default {_loose + _clipRounds};
        };
    };

    if (_have < _need && {_have > 0}) then {
        hintSilent LLSTRING(Hint_Short);
    };

    _need = _need min _have;
};

// Pressed in whole: one step per clip, magazine by magazine; the last clip into a magazine may have more on it than
// there is room for, the rest comes back loose.
private _steps = [];

if (_clipLoading) then {
    private _supply = [];

    {
        _x params ["", "_count", "_per"];

        for "_i" from 1 to _count do {
            _supply pushBack _per;
        };
    } forEach _clips;

    private _left = _need;

    {
        private _space = (_capacity - _x) min _left;

        while {_space > 0 && {_supply isNotEqualTo []}} do {
            private _take = (_supply deleteAt 0) min _space;

            _steps pushBack _take;
            _space = _space - _take;
            _left = _left - _take;
        };
    } forEach _amounts;

    _need = 0;
    {_need = _need + _x} forEach _steps;
};

if (_refused isNotEqualTo "") exitWith {
    hintSilent _refused;
    PLAY_SOUND(denied);
    false
};

if (_need <= 0) exitWith {
    hintSilent LLSTRING(Hint_NoAmmo);
    PLAY_SOUND(denied);
    false
};

// The time: per round for a magazine, a steady rate for a belt (a long fixed minimum made topping up a nearly full belt
// crawl). Whole clips take the clip factor of it, loose rounds the loose-round factor while the speedloader
// works on them.
private _time = if (_belt) then {
    ((_need / BELT_ROUNDS_PER_SECOND) max BELT_MIN_TIME)
        * EGVAR(main,beltTimeFactor)
        * (_unit getVariable [QEGVAR(main,beltTime), 1])
} else {
    _need * ([_looseBoost, EGVAR(main,speedloaderFactor)] select _clipLoading) * EGVAR(main,timePerRound)
        * (_unit getVariable [QEGVAR(main,magazineTime), 1])
};

GVAR(opCounter) = GVAR(opCounter) + 1;

// What the display starts from: the first magazine's rounds, or the whole belt item.
private _startShown = if (_kind == "unloadBelt") then {_capacity} else {_amounts param [0, 0]};
private _game = EGVAR(main,loadGame) && {!_belt} && {EGVAR(main,loadDisplay) == 0};
// Whole clips have their own minigame (fnc_clipGameTick), pressed at the clip's pace rather than a round's.
private _clipGame = _game && {_clipLoading};

// Clips that go in round by round say why: no speedloader, or the server set it to loose rounds only.
if (_from == "clips" && {!_clipLoading} && {_clipRounds > 0}) then {
    hintSilent ([LLSTRING(Hint_NoSpeedloader), LLSTRING(Hint_SpeedloaderLoose)] select _speedloader);
};

// Why loading took the way it did, for when it is not the one expected (the RPT).
if (_kind == "fill" && {!_belt}) then {
    INFO_8("Fill %1 from %2: %3 rounds loose, %4 on clips, speedloader %5 (mode %6), whole clips %7, clip minigame %8.",_class,_from,_loose,_clipRounds,_speedloader,EGVAR(main,speedloaderMode),_clipLoading,_clipGame);
};
private _beat = [(_time / _need) max GAME_MIN_BEAT, _time / _need] select _clipGame;

if (_game) then {
    _time = _beat * _need;
};

// The rounds on one clip, as the minigame draws it (fnc_clipGameOpen).
private _clipSize = if (_clips isEqualTo []) then {10} else {_clips select 0 select 2};

GVAR(op) = createHashMapFromArray [
    ["id", GVAR(opCounter)],
    ["unit", _unit],
    ["kind", _kind],
    ["class", _class],
    ["amounts", _amounts],
    ["need", _need],
    ["capacity", _capacity],
    ["played", 0],
    ["shown", _startShown],
    ["shownAtStart", _startShown],
    ["time", _time],
    ["progress", 0],
    ["belt", _belt],
    ["source", _source],
    ["becomes", _becomes],
    ["from", _from],
    ["clipLoading", _clipLoading],
    ["steps", _steps],
    ["clipGame", _clipGame],
    // How much faster the speedloader makes loose rounds, shown in the display (fnc_uiCreate); 1 when it does not.
    ["boost", [1, 1 / (_looseBoost max 0.01)] select (_kind == "fill" && {!_belt} && {!_clipLoading} && {_looseBoost < 1})],
    ["clipSize", _clipSize],
    ["stage", "place"],
    ["stepIndex", 0],
    ["stepsDone", 0],
    ["pushed", 0],
    ["title", format [[LLSTRING(Title_Unload), LLSTRING(Title_Fill)] select (_kind in ["fill", "refillBelt"]), _name]],
    ["picture", _picture],
    ["created", CBA_missionTime],
    ["seen", CBA_missionTime],
    ["started", -1],
    ["last", CBA_missionTime],
    ["hold", EGVAR(main,holdToLoad) && {!_game}],
    ["pressed", false],
    ["game", _game],
    ["mustHit", EGVAR(main,gameMustHit)],
    ["beat", _beat],
    ["phase", 0],
    ["rounds", 0],
    ["attempt", 0],
    ["attemptShown", -1],
    ["combo", 0],
    ["bonusText", ""],
    ["bonusUntil", -1],
    ["tried", false],
    ["zone", 0],
    ["zoneSize", 0],
    ["stall", 0],
    ["ui", createHashMap],
    ["handle", -1],
    ["keys", -1]
];

// A key let go while a dialog had the keyboard never reports it, so each loading starts with it up.
GVAR(keyHeld) = false;

call FUNC(uiCreate);

GVAR(op) set ["keys", (findDisplay 46) displayAddEventHandler ["KeyDown", {
    params ["", "_key"];

    if (_key == 1 && {!isNil QGVAR(op)}) then {
        [false] call FUNC(finish);
        true
    } else {
        false
    };
}]];
GVAR(op) set ["handle", [FUNC(tick), 0, [GVAR(opCounter)]] call CBA_fnc_addPerFrameHandler];

if !(GVAR(op) get "hold") then {
    call FUNC(begin);
};

true
