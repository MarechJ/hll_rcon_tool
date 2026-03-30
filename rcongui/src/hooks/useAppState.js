import { create } from "zustand";
import { persist } from "zustand/middleware";
import siteConfig from "@/config/siteConfig";

const prefix = siteConfig.appName + '.';
const withPrefix = (key) => prefix + key;

export const useAppStore = create(
  persist(
    (set, get) => ({
      colorScheme: "default",
      setColorScheme: (scheme) => set({ colorScheme: scheme }),
      widthMode: "xl",
      toggleWidthMode: () => set({ widthMode: get().widthMode === "xl" ? false : "xl" }),
      openDrawer: true,
      toggleDrawer: () => set({ openDrawer: !get().openDrawer }),
      // Persist which navigation groups are expanded.
      groupOpenState: {},
      toggleMenuGroupOpen: (groupName) =>
        set((state) => ({
          groupOpenState: {
            ...state.groupOpenState,
            [groupName]: !state.groupOpenState?.[groupName],
          },
        })),
    }),
    {
      name: withPrefix("app"),
    }
  )
);

