#include "..\script_component.hpp"
/*
 * Author: Davidaf
 * Runs code on the next frame, in the editor too. CBA's frame loop, which CBA_fnc_execNextFrame waits on, only starts
 * with a mission: in the editor's arsenal nothing handed to it would ever run. There the scheduler brings the next
 * frame, and the code still runs in one go, as the frame loop would run it.
 *
 * Arguments:
 * 0: Code <CODE>
 * 1: Its arguments <ANY> (default: [])
 *
 * Return Value:
 * None
 *
 * Example:
 * [{systemChat str _this}, [1, 2]] call gmr_compat_ace_fnc_nextFrame;
 *
 * Public: No
 */

params [["_code", {}, [{}]], ["_arguments", []]];

if (is3DEN) exitWith {
    [_arguments, _code] spawn {
        params ["_arguments", "_code"];

        isNil {_arguments call _code};
    };

    nil
};

[_code, _arguments] call CBA_fnc_execNextFrame;

nil
