// ACE's own recordings of a round going into a magazine and a finished one, played from where they lie.
#define SOUND(fileName,file,volume,pitch) class DOUBLES(gmr_handling_sound,fileName) {\
    sound[] = {file, volume, pitch};\
}

#define ROUND_IN "\z\ace\addons\magazinerepack\sounds\magrepack_single.wav"
#define FINISHED "\z\ace\addons\magazinerepack\sounds\magrepack_finished.wav"
#define ACE_CLICK "\z\ace\addons\common\sounds\ACE_click.wav"

class CfgSounds {
    SOUND(round_in_1,ROUND_IN,1,0.94);
    SOUND(round_in_2,ROUND_IN,1,0.97);
    SOUND(round_in_3,ROUND_IN,1,1.0);
    SOUND(round_in_4,ROUND_IN,1,1.03);
    SOUND(round_in_5,ROUND_IN,1,1.06);
    SOUND(round_in_6,ROUND_IN,1,1.09);
    SOUND(round_in_7,ROUND_IN,1,1.12);
    SOUND(round_in_8,ROUND_IN,1,1.15);

    SOUND(magazine_done,FINISHED,1,1);
    SOUND(grab,ACE_CLICK,1,0.8);
};
