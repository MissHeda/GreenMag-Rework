// Real recordings: the rounds going in, the grab and the full magazine from a CC0 recording in this mod, the rest the
// game's own, played from where they lie. The clicks climb in pitch as the spring tightens.
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
#define RATTLE QPATHTOF(soundsattle.ogg)
#define SEAT QPATHTOF(sounds\seat.ogg)
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

    SOUND(round_out_1,BRASS_1,1.5,0.92);
    SOUND(round_out_2,BRASS_2,1.5,0.96);
    SOUND(round_out_3,BRASS_3,1.5,1.0);
    SOUND(round_out_4,BRASS_4,1.5,1.0);
    SOUND(round_out_5,BRASS_6,1.5,1.04);
    SOUND(round_out_6,BRASS_7,1.5,1.08);

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
