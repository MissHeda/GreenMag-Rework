class CfgVehicles {
    class Man;
    class CAManBase: Man {
        class ACE_SelfActions {
            class GVAR(refill) {
                displayName = CSTRING(Refill);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOF(data\action_fill.paa);
                insertChildren = QUOTE([ARR_2(_player,'fill')] call FUNC(menuMagazines));
            };
            class GVAR(unload) {
                displayName = CSTRING(Unload);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOF(data\action_unload.paa);
                insertChildren = QUOTE([ARR_2(_player,'unload')] call FUNC(menuMagazines));
            };
            class GVAR(unpack) {
                displayName = CSTRING(Unpack);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOF(data\action_unpack.paa);
                insertChildren = QUOTE([_player] call FUNC(menuUnpack));
            };
            class GVAR(pack) {
                displayName = CSTRING(Pack);
                condition = QUOTE(EGVAR(main,enabled) && {EGVAR(main,allowPacking)});
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOF(data\action_pack.paa);
                insertChildren = QUOTE([_player] call FUNC(menuPack));
            };
            class GVAR(combine) {
                displayName = CSTRING(Combine);
                condition = QUOTE(EGVAR(main,enabled) && {EGVAR(main,beltsEnabled)});
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOF(data\action_belt.paa);
                insertChildren = QUOTE([_player] call FUNC(menuCombine));
            };

            class ACE_RepackMagazines {
                condition = QUOTE(!(EGVAR(main,enabled) && {EGVAR(main,disableAceRepack)}));
            };
        };
    };
};
