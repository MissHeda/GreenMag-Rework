class CfgWeapons {
    class CBA_MiscItem;
    class CBA_MiscItem_ItemInfo;

    class gmr_item_base: CBA_MiscItem {
        author = "Miss Heda";
        scope = 1;
        scopeArsenal = 1;
        scopeCurator = 1;
        displayName = "";
        descriptionShort = "";
        model = "\A3\weapons_F\ammo\mag_univ.p3d";
        icon = "iconObject_circle";
        mapSize = 0.034;

        class ItemInfo: CBA_MiscItem_ItemInfo {
            mass = 1;
        };
    };

    // The context menu's "Unpack" hangs on the pack base, the menus tell the kinds apart by gmr_kind.
    class gmr_round_base: gmr_item_base {
        model = QPATHTOF(data\drop_round.p3d);
        gmr_kind = "round";
        gmr_rounds = 1;
    };
    class gmr_pack_base: gmr_item_base {
        gmr_kind = "pack";
        scope = 2;
    };
    // A stripper clip: stripped like a pack, or pressed into a magazine whole with the speedloader.
    class gmr_clip_base: gmr_item_base {
        gmr_kind = "clip";
        scope = 2;
        scopeArsenal = 2;
        scopeCurator = 2;
        descriptionShort = CSTRING(Clip_Desc);
    };
    class gmr_belt_base: gmr_item_base {
        model = QPATHTOF(data\drop_belt.p3d);
        gmr_kind = "belt";
    };

    class gmr_speedloader: gmr_item_base {
        scope = 2;
        scopeArsenal = 2;
        scopeCurator = 2;
        displayName = CSTRING(Speedloader);
        descriptionShort = CSTRING(Speedloader_Desc);
        picture = QPATHTOF(data\speedloader.paa);
        model = QPATHTOF(data\drop_speedloader.p3d);

        class ItemInfo: CBA_MiscItem_ItemInfo {
            mass = 2;
        };
    };

    #include "cfg\rounds.hpp"
    #include "cfg\clips.hpp"
    #include "cfg\belts.hpp"
};
