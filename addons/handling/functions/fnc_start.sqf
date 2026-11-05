#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Sets up loading or unloading and shows what it takes to do it: a hold action that leaves on its own if nobody
 * starts it, or ACE's progress bar. Nothing in the inventory changes before the end (fnc_finish).
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: "fill", "unload" or "unloadBelt" <STRING>
 * 2: Magazine class, or the belt item for "unloadBelt" <STRING>
 * 3: The rounds of each magazine, in the order to work through them <ARRAY>
 * 4: Ammunition to refill from, a round class or belt type; "" chooses by the caliber (optional, default: "") <STRING>
 *
 * Return Value:
 * Whether it started <BOOL>
 *
 * Example:
 * [player, "fill", "30Rnd_556x45_Stanag", [12]] call gmr_handling_fnc_start;
 *
 * Public: No
 */

params [["_unit", objNull, [objNull]], ["_kind", "fill", [""]], ["_class", "", [""]], ["_amounts", [], [[]]], ["_ammunition", "", [""]]];

if (!EGVAR(main,enabled) || {!alive _unit}) exitWith {false};

// One that should have ended by now was cut off by something else, a respawn for one.
if (!isNil QGVAR(op)) then {
    if (
        (GVAR(op) get "unit") isNotEqualTo _unit
        || {!alive (GVAR(op) get "unit")}
        || {(GVAR(op) get "started") >= 0 && {CBA_missionTime > (GVAR(op) get "started") + (GVAR(op) get "time") + 5}}
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

if (_kind == "fill" && {!EGVAR(main,freeRefill)}) then {
    private _have = 0;

    if (_belt) then {
        if (_source isNotEqualTo "") then {
            {_have = _have + (_x select 1)} forEach ([_unit, _source] call EFUNC(main,beltItems));
        };
    } else {
        _have = _counts getOrDefault [_source, 0];
    };

    if (_have < _need && {_have > 0}) then {
        hintSilent LLSTRING(Hint_Short);
    };

    _need = _need min _have;
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

// The time: per round for a magazine, a steady rate with a minimum for a belt.
private _time = if (_belt) then {
    (ceil (_need / BELT_ROUNDS_PER_SECOND) max ([BELT_MIN_TIME_UNLOAD, BELT_MIN_TIME_LOAD] select (_kind == "fill")))
        * EGVAR(main,beltTimeFactor)
        * (_unit getVariable [QEGVAR(main,beltTime), 1])
} else {
    _need * EGVAR(main,timePerRound)
        * (_unit getVariable [QEGVAR(main,magazineTime), 1])
        * ([1, EGVAR(main,speedloaderFactor)] select (_kind == "fill" && {_speedload} && {"gmr_speedloader" in _counts}))
};

GVAR(opCounter) = GVAR(opCounter) + 1;

GVAR(op) = createHashMapFromArray [
    ["id", GVAR(opCounter)],
    ["unit", _unit],
    ["kind", _kind],
    ["class", _class],
    ["amounts", _amounts],
    ["need", _need],
    ["capacity", _capacity],
    ["played", 0],
    ["counter", controlNull],
    ["time", _time],
    ["belt", _belt],
    ["source", _source],
    ["becomes", _becomes],
    ["started", -1],
    ["tick", -1],
    ["hold", -1],
    ["cancel", -1]
];

private _title = format [[LLSTRING(Hold_Unload), LLSTRING(Hold_Fill)] select (_kind == "fill"), _name];

if (!EGVAR(main,holdToLoad)) then {
    call FUNC(begin);

    if (HAS_ACE) then {
        [
            _time,
            [],
            {[true] call FUNC(finish)},
            {[false] call FUNC(finish)},
            _title,
            {true},
            ["isNotInside", "isNotSitting", "isNotSwimming"]
        ] call ace_common_fnc_progressBar;
    } else {
        // Without ACE's bar: it runs by itself, and the scroll menu has the way out.
        GVAR(op) set ["cancel", _unit addAction [LLSTRING(Cancel), {[false] call FUNC(finish)}, nil, 100000, true, true]];

        [
            {
                params ["_id"];

                if (!isNil QGVAR(op) && {(GVAR(op) get "id") == _id}) then {
                    [true] call FUNC(finish);
                };
            },
            [GVAR(opCounter)],
            _time
        ] call CBA_fnc_waitAndExecute;
    };
} else {
    // The picture of what is being worked on, in the ring. The game draws a plain path at the ring's full size, so
    // the icon comes as text of its own, centred by a spacer above it.
    GVAR(holdIcon) = format [
        "<t size='%1'>&#160;</t><br/><img size='%2' color='#ffffff' image='%3'/>",
        (HOLD_RING_SIZE - HOLD_ICON_SIZE) / 2, HOLD_ICON_SIZE, _picture
    ];

    private _icon = {missionNamespace getVariable [QGVAR(holdIcon), ""]};

    private _hold = [
        _unit,
        _title,
        _icon,
        _icon,
        "alive _this",
        "alive _caller",
        {call FUNC(begin)},
        {},
        {[true] call FUNC(finish)},
        {[false] call FUNC(finish)},
        [],
        _time,
        100000,
        true,
        false
    ] call BIS_fnc_holdActionAdd;

    GVAR(op) set ["hold", _hold];

    // Not started in time: it leaves. Nothing has changed yet, so nothing is lost.
    [
        {
            params ["_id"];

            if (!isNil QGVAR(op) && {(GVAR(op) get "id") == _id} && {(GVAR(op) get "started") < 0}) then {
                [false] call FUNC(finish);
            };
        },
        [GVAR(opCounter)],
        HOLD_TIMEOUT
    ] call CBA_fnc_waitAndExecute;
};

true
