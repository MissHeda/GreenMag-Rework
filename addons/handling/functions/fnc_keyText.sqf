#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The name of the key a player has set for one of the mod's keybinds in the CBA controls, as the prompts show it.
 * A keybind without a key falls back to the given text.
 *
 * Arguments:
 * 0: The keybind's name, without the prefix ("keyLoad" or "keyCancel") <STRING>
 * 1: What to show without a key <STRING>
 *
 * Return Value:
 * The key's name <STRING>
 *
 * Example:
 * ["keyLoad", "Space"] call gmr_handling_fnc_keyText;
 *
 * Public: No
 */

params ["_name", "_fallback"];

private _bind = [KEYBIND_CATEGORY, format ["%1_%2", QUOTE(ADDON), _name]] call CBA_fnc_getKeybind;

if (isNil "_bind") exitWith {_fallback};

(_bind select 5) params [["_key", -1], ["_modifiers", [false, false, false]]];

if (_key <= 0) exitWith {_fallback};

private _text = if (isNil "CBA_fnc_localizeKey") then {keyName _key} else {[_key, _modifiers] call CBA_fnc_localizeKey};

_text = _text splitString """" joinString "";

[_text, _fallback] select (_text isEqualTo "")
