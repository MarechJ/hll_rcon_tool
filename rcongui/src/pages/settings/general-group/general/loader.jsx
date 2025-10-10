import { cmd } from "@/utils/fetchUtils";

export const loader = async () => {
  const settings = await cmd.GET_SERVER_SETTINGS();
  settings["votekick_thresholds"] = JSON.parse(settings["votekick_thresholds"]);
  const autokickSettings = await cmd.GET_VOTEKICK_AUTOTOGGLE_CONFIG();
  return { settings, autokickSettings };
};
