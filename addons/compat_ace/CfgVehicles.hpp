class CfgVehicles {
    class Man;
    class CAManBase: Man {
        class ACE_SelfActions {
            class GVAR(refill) {
                displayName = ECSTRING(handling,Refill);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_fill.paa);
                insertChildren = QUOTE([ARR_2(_player,'fill')] call EFUNC(handling,menuMagazines));
            };
            class GVAR(unload) {
                displayName = ECSTRING(handling,Unload);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_unload.paa);
                insertChildren = QUOTE([ARR_2(_player,'unload')] call EFUNC(handling,menuMagazines));
            };
            class GVAR(unpack) {
                displayName = ECSTRING(handling,Unpack);
                condition = QEGVAR(main,enabled);
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_unpack.paa);
                insertChildren = QUOTE([_player] call EFUNC(handling,menuUnpack));
            };
            class GVAR(pack) {
                displayName = ECSTRING(handling,Pack);
                condition = QUOTE(EGVAR(main,enabled) && {EGVAR(main,allowPacking)});
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_pack.paa);
                insertChildren = QUOTE([_player] call EFUNC(handling,menuPack));
            };
            class GVAR(combine) {
                displayName = ECSTRING(handling,Combine);
                condition = QUOTE(EGVAR(main,enabled) && {EGVAR(main,beltsEnabled)});
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_belt.paa);
                insertChildren = QUOTE([_player] call EFUNC(handling,menuCombine));
            };

            class GVAR(split) {
                displayName = ECSTRING(handling,SplitBelt);
                condition = QUOTE(EGVAR(main,enabled) && {EGVAR(main,beltsEnabled)});
                exceptions[] = {"isNotInside", "isNotSitting", "isNotSwimming"};
                statement = "";
                icon = QPATHTOEF(handling,data\action_split.paa);
                insertChildren = QUOTE([_player] call EFUNC(handling,menuSplit));
            };
            class GVAR(linkBeltSelf) {
                displayName = CSTRING(LinkBelt);
                condition = QUOTE(([ARR_2(_player,_player)] call FUNC(linkBeltSource)) isNotEqualTo []);
                exceptions[] = {"isNotInside"};
                statement = QUOTE([ARR_2(_player,_player)] call FUNC(startLinkBelt));
                icon = QPATHTOEF(handling,data\action_link.paa);
            };

            class ACE_RepackMagazines {
                condition = QUOTE(!(EGVAR(main,enabled) && {EGVAR(main,disableAceRepack)}));
            };
        };

        class ACE_Actions {
            class ACE_Weapon {
                class GVAR(linkBelt) {
                    displayName = CSTRING(LinkBelt);
                    distance = 2;
                    condition = QUOTE(([ARR_2(_player,_target)] call FUNC(linkBeltSource)) isNotEqualTo []);
                    statement = QUOTE([ARR_2(_player,_target)] call FUNC(startLinkBelt));
                    exceptions[] = {"isNotInside"};
                    icon = QPATHTOEF(handling,data\action_link.paa);
                };
            };
        };
    };
};
