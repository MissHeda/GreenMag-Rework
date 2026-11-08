// The loading panel and the minigame can be moved in Arma's layout editor (Options > Game > Layout). The editor keeps
// the place in the profile as IGUI_gmr_handling_grid_X and _Y, which fnc_uiCreate and fnc_clipGameOpen read (UI_LAYOUT_X,
// UI_LAYOUT_Y). Only the position is saved, the size stays the panel's own.
class CfgUIGrids {
    class IGUI {
        class Presets {
            class Arma3 {
                class Variables {
                    GVAR(grid)[] = {{QUOTE(UI_DEFAULT_X), QUOTE(UI_DEFAULT_Y), QUOTE(UI_WIDTH), QUOTE(UI_LAYOUT_HEIGHT)}, QUOTE(GUI_GRID_W), QUOTE(GUI_GRID_H)};
                };
            };
        };

        class Variables {
            class GVAR(grid) {
                displayName = CSTRING(IGUI_Name);
                description = CSTRING(IGUI_Description);
                preview = "#(argb,8,8,3)color(0.086,0.094,0.114,0.88)";
                saveToProfile[] = {0, 1};
                canResize = 0;
            };
        };
    };
};
