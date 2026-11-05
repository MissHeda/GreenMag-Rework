#define SOUND(fileName) class TRIPLES(ADDON,sound,fileName) {\
    name = QUOTE(TRIPLES(ADDON,sound,fileName));\
    sound[] = {QPATHTOF(sounds\fileName.wav), 2, 1};\
    titles[] = {};\
}

class CfgSounds {
    SOUND(round_in_1);
    SOUND(round_in_2);
    SOUND(round_in_3);
    SOUND(round_in_4);
    SOUND(round_out_1);
    SOUND(round_out_2);
    SOUND(round_out_3);
    SOUND(belt_link_1);
    SOUND(belt_link_2);
    SOUND(belt_link_3);
    SOUND(magazine_done);
};
