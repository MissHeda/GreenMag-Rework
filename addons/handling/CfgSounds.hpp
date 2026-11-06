// Real recordings: the rounds going in and out, the grab and the full magazine from CC0 recordings in this mod, the rest
// the game's own, played from where they lie. The clicks climb in pitch as the spring tightens.
#define SOUND(fileName,file,volume,pitch) class TRIPLES(ADDON,sound,fileName) {\
    name = QUOTE(TRIPLES(ADDON,sound,fileName));\
    sound[] = {file, volume, pitch};\
    titles[] = {};\
}

#define CLICK "A3\Sounds_F\weapons\Reloads\kohoutek1"

// Cut by tools/cut_sounds.py from BigSoundBank's "Gun, loading #4" (CC0): single clicks of a magazine being loaded,
// the rattle of handling it, the clack of it seating.
#define CLICK_1 QPATHTOF(sounds\click_1.ogg)
#define CLICK_2 QPATHTOF(sounds\click_2.ogg)
#define CLICK_3 QPATHTOF(sounds\click_3.ogg)
#define CLICK_4 QPATHTOF(sounds\click_4.ogg)
#define RATTLE QPATHTOF(sounds\rattle.ogg)
#define SEAT QPATHTOF(sounds\seat.ogg)

// BigSoundBank's cartridge cases falling on concrete (CC0): a round falling out while unloading.
#define DROP_1 QPATHTOF(sounds\drop_1.ogg)
#define DROP_2 QPATHTOF(sounds\drop_2.ogg)
#define DROP_3 QPATHTOF(sounds\drop_3.ogg)
#define DROP_4 QPATHTOF(sounds\drop_4.ogg)
#define DROP_5 QPATHTOF(sounds\drop_5.ogg)
#define BOLT_1 "A3\Sounds_F\weapons\Other\reload_bolt_1"
#define BOLT_2 "A3\Sounds_F\weapons\Other\reload_bolt_2"
#define BOLT_3 "A3\Sounds_F\weapons\Other\reload_bolt_3"
#define BRASS_1 "A3\Sounds_F\weapons\Shells\5_56\metal_556_01"
#define BRASS_2 "A3\Sounds_F\weapons\Shells\5_56\metal_556_02"
#define BRASS_3 "A3\Sounds_F\weapons\Shells\5_56\metal_556_03"
#define BRASS_4 "A3\Sounds_F\weapons\Shells\5_56\metal_556_04"
#define BRASS_5 "A3\Sounds_F\weapons\Shells\5_56\metal_556_05"
#define BRASS_6 "A3\Sounds_F\weapons\Shells\5_56\metal_556_06"
#define BRASS_7 "A3\Sounds_F\weapons\Shells\5_56\metal_556_07"
#define BRASS_8 "A3\Sounds_F\weapons\Shells\5_56\metal_556_08"

class CfgSounds {
    SOUND(round_in_1,CLICK_1,1.6,0.94);
    SOUND(round_in_2,CLICK_4,1.6,0.97);
    SOUND(round_in_3,CLICK_3,1.6,1.0);
    SOUND(round_in_4,CLICK_1,1.6,1.03);
    SOUND(round_in_5,CLICK_4,1.6,1.06);
    SOUND(round_in_6,CLICK_2,1.6,1.09);
    SOUND(round_in_7,CLICK_3,1.6,1.12);
    SOUND(round_in_8,CLICK_4,1.6,1.15);

    SOUND(round_out_1,DROP_1,1.4,0.97);
    SOUND(round_out_2,DROP_2,1.4,1.0);
    SOUND(round_out_3,DROP_3,1.4,0.98);
    SOUND(round_out_4,DROP_4,1.4,1.02);
    SOUND(round_out_5,DROP_5,1.4,1.0);
    SOUND(round_out_6,DROP_1,1.4,1.04);

    SOUND(belt_link_1,BRASS_5,1.5,0.72);
    SOUND(belt_link_2,BRASS_6,1.5,0.76);
    SOUND(belt_link_3,BRASS_7,1.5,0.72);
    SOUND(belt_link_4,BRASS_8,1.5,0.78);

    SOUND(magazine_done,SEAT,1.8,1);
    SOUND(magazine_empty,BOLT_2,1.5,1);
    SOUND(belt_done,BOLT_3,2,0.9);
    SOUND(belt_feed,BOLT_3,2.5,0.8);
    SOUND(belt_split,BOLT_2,1.5,1.2);
    SOUND(belt_combine,BOLT_1,1.5,1.1);

    SOUND(grab,RATTLE,1.4,1);
    SOUND(cancel,CLICK,1,0.6);
    SOUND(denied,CLICK,1.5,0.5);
    SOUND(drop_item,CLICK_4,1.4,1.05);

    SOUND(pack_open,"A3\Sounds_F_Decade\Assets\Props\LinkTerminal_01_node_2_F\Link_Terminal02_Box_Lock_Open",1.5,1);
    SOUND(pack_close,"A3\Sounds_F_Decade\Assets\Props\LinkTerminal_01_node_2_F\Link_Terminal02_Box_Lock_Close",1.5,1);
};
