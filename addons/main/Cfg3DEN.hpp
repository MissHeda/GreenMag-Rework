class Cfg3DEN {
    class Attributes {
        class Default;
        class Title: Default {
            class Controls {
                class Title;
            };
        };
        class Slider: Title {
            class Controls: Controls {
                class Title;
                class Value;
                class Edit;
            };
        };
        class SliderMultiplier: Slider {
            class Controls: Controls {
                class Title;
                class Value;
                class Edit;
            };
        };
        class GVAR(skillSlider): SliderMultiplier {
            class Controls: Controls {
                class Title: Title {};
                class Value: Value {
                    sliderRange[] = {0.25, 2};
                };
                class Edit: Edit {};
            };
        };
    };
    class Object {
        class AttributeCategories {
            class GVAR(attributes) {
                displayName = "GreenMag Rework";
                collapsed = 1;
                class Attributes {
                    class GVAR(magazineTime) {
                        displayName = CSTRING(Eden_MagazineTime);
                        tooltip = CSTRING(Eden_MagazineTime_Desc);
                        property = QGVAR(magazineTime);
                        control = QGVAR(skillSlider);
                        expression = QUOTE(_this setVariable [ARR_3(QQGVAR(magazineTime),_value,true)]);
                        defaultValue = 1;
                        unique = 0;
                        condition = "objectControllable";
                        typeName = "NUMBER";
                    };
                    class GVAR(beltTime) {
                        displayName = CSTRING(Eden_BeltTime);
                        tooltip = CSTRING(Eden_BeltTime_Desc);
                        property = QGVAR(beltTime);
                        control = QGVAR(skillSlider);
                        expression = QUOTE(_this setVariable [ARR_3(QQGVAR(beltTime),_value,true)]);
                        defaultValue = 1;
                        unique = 0;
                        condition = "objectControllable";
                        typeName = "NUMBER";
                    };
                };
            };
        };
    };
};
