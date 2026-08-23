import { cmd } from "@/utils/fetchUtils";
import { gameSwitch } from "@/utils/lib";
import { queryClient } from "@/queryClient";
import { mapsManagerQueryOptions } from "../queries";

const HLL_Loader = async () => {
  const objectives = await cmd.GET_MAP_OBJECTIVES();
  const gameState = await cmd.GET_GAME_STATE();
  return { objectives, gameState };
};

const HLL_V_Loader = async () => {
  await Promise.all([
    queryClient.ensureQueryData(mapsManagerQueryOptions.gameLayouts()),
    queryClient.ensureQueryData(mapsManagerQueryOptions.mapsWithObjectives()),
  ]);
  return null;
};

export const loader = gameSwitch(HLL_Loader, HLL_V_Loader);
