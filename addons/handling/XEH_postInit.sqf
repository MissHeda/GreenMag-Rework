#include "script_component.hpp"

if (!hasInterface) exitWith {};

// The magazine in the hand of whoever is loading one.
[QGVAR(magazineShown), {_this call FUNC(holdMagazine)}] call CBA_fnc_addEventHandler;
[QGVAR(magazineHidden), {
    params ["_unit"];

    deleteVehicle (_unit getVariable [QGVAR(heldMagazine), objNull]);
    deleteVehicle (_unit getVariable [QGVAR(heldRound), objNull]);
}] call CBA_fnc_addEventHandler;

call FUNC(addContextMenus);
