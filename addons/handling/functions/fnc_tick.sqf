#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Runs while an operation runs. Each round that has moved by the clock clicks once and the counter changes with it, so
 * sound, counter and the ring or bar all follow the same time. Only sound and picture: the inventory changes at the end
 * (fnc_finish). Over a magazine the click climbs in pitch as the spring tightens.
 *
 * Arguments:
 * 0: [operation id], the per-frame handler's arguments <ARRAY>
 * 1: The per-frame handler <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [[1], 0] call gmr_handling_fnc_tick;
 *
 * Public: No
 */

params ["_args", "_handle"];
_args params ["_id"];

if (isNil QGVAR(op) || {(GVAR(op) get "id") != _id}) exitWith {
    [_handle] call CBA_fnc_removePerFrameHandler;
};

private _need = GVAR(op) get "need";
private _time = (GVAR(op) get "time") max 0.01;
private _done = floor (_need * (((CBA_missionTime - (GVAR(op) get "started")) / _time) min 1));

if (_done <= (GVAR(op) get "played")) exitWith {};

GVAR(op) set ["played", _done];

private _kind = GVAR(op) get "kind";
private _capacity = GVAR(op) get "capacity";
private _shown = 0;
private _left = _done;

if (_kind == "unloadBelt") then {
    _shown = _capacity - _done;
} else {
    private _amounts = GVAR(op) get "amounts";

    {
        private _moves = [_x, _capacity - _x] select (_kind == "fill");

        // On to the next magazine only when this one is through.
        if (_left < _moves || {_forEachIndex == count _amounts - 1}) exitWith {
            _shown = [_x - _left, _x + _left] select (_kind == "fill");
        };

        _left = _left - _moves;
    } forEach _amounts;
};

if (EGVAR(main,sounds)) then {
    private _level = _shown / (_capacity max 1);

    playSound (switch (true) do {
        case (GVAR(op) get "belt"): {format [QGVAR(sound_belt_link_%1), 1 + floor random 4]};
        case (_kind == "fill"): {format [QGVAR(sound_round_in_%1), 1 + (floor (_level * 8) min 7)]};
        default {format [QGVAR(sound_round_out_%1), 1 + (floor (_level * 6) min 5)]};
    });
};

private _counter = GVAR(op) get "counter";

if (!isNull _counter) then {
    _counter ctrlSetStructuredText parseText format ["<t align='center' shadow='2' size='1.3' font='PuristaSemibold'>%1<t size='0.8' color='#c8c8c8'> / %2</t></t>", _shown, _capacity];
};

nil
