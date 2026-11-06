#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Whether a magazine takes this ammunition. Its own kind of round always fits. Another kind only goes into a completely
 * empty magazine, which then becomes that kind's version of the magazine: tracers turn an empty magazine of ball into
 * one of tracers. With a round still inside, only the right kind goes in. The simple system has only one kind of round
 * per caliber, its basic rounds fit any magazine of the caliber. Universal ammunition fits everything.
 *
 * Arguments:
 * 0: Magazine class <STRING>
 * 1: Rounds in it <NUMBER>
 * 2: Round class or belt type <STRING>
 *
 * Return Value:
 * [magazine class it will be, reason in words when it does not fit, else ""] <ARRAY>
 *
 * Example:
 * ["30Rnd_556x45_Stanag", 0, "gmr_round_556x45_tracer"] call gmr_handling_fnc_loadRule;
 *
 * Public: No
 */

params [["_class", "", [""]], ["_rounds", 0, [0]], ["_ammunition", "", [""]]];

if (_ammunition in [UNIVERSAL_ROUND, UNIVERSAL_BELT] && {!EGVAR(main,universalAmmo)}) exitWith {["", LLSTRING(Hint_UniversalOff)]};

if (_ammunition in ["", UNIVERSAL_ROUND, UNIVERSAL_BELT]) exitWith {[_class, ""]};

private _type = ([_class] call EFUNC(main,magazineInfo)) select MAG_TYPE;
private _item = [_ammunition, _ammunition + "1"] select (_ammunition select [count _ammunition - 1] == "_");
private _variant = ([_item] call EFUNC(main,itemInfo)) select ITEM_VARIANT;

if (_variant == _type || {_variant == "basic" && {!EGVAR(main,advancedAmmo)}}) exitWith {[_class, ""]};

if (_rounds > 0) exitWith {["", LLSTRING(Hint_WrongKind)]};

private _sibling = [_class, _variant] call EFUNC(main,siblingMagazine);

if (_sibling isEqualTo "") exitWith {["", LLSTRING(Hint_NoVersion)]};

[_sibling, ""]
