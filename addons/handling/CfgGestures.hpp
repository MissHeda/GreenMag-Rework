class CfgMovesBasic {
    class ManActions {
        GVAR(load) = QGVAR(load);
        GVAR(stop) = QGVAR(stop);
    };
    class Actions {
        class NoActions: ManActions {
            GVAR(load)[] = {QGVAR(load), "Gesture"};
            GVAR(stop)[] = {QGVAR(stop), "Gesture"};
        };
    };
};

class CfgGesturesMale {
    class Default;
    class States {
        class GestureNod;
        class GVAR(stop): GestureNod {
            file = "a3\anims_f\data\anim\sdr\gst\gestureEmpty.rtm";
            mask = "empty";
            disableWeapons = 0;
            disableWeaponsLong = 0;
            enableOptics = 1;
        };
        class GVAR(load): Default {
            file = QPATHTOF(anims\load.rtm);
            looped = 1;
            speed = 1;
            mask = "handsWeapon_pst_context";
            interpolationSpeed = 3;
            disableWeapons = 1;
            disableWeaponsLong = 1;
            enableOptics = 0;
            canPullTrigger = 0;
            leftHandIKCurve[] = {0};
            rightHandIKCurve[] = {0};
        };
    };
};
