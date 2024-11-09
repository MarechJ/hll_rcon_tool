import { useGlobalStore } from "@/hooks/useGlobalState";
import { extractPlayers } from "@/utils/extractPlayers";
import { cmd } from "@/utils/fetchUtils";
import { normalizePlayerProfile } from "@/utils/lib";

export const teamsLiveQueryOptions = {
  queryKey: ["teams", "live"],
  queryFn: cmd.GET_LIVE_TEAMS,
  select: (data) => {
    // Think of this as a middleware that transforms the player data
    // in case the API returns something different than what we expect
    const onlinePlayers = extractPlayers(data).map((player) => ({
      ...player,
      profile: normalizePlayerProfile(player.profile),
    }));
    useGlobalStore.setState(() => ({ onlinePlayers }));
    return data;
  },
};

export const teamsLiveQuery = (options) => {
  return useQuery({
    ...teamsLiveQueryOptions,
    ...options,
  });
};
