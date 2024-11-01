import { cmd } from "@/utils/fetchUtils";
import { normalizePlayerProfile } from "@/utils/lib";

export const playerProfileQueryOptions = (playerId, options) => {
  const { throwRouteError = true } = options;
  return {
    queryKey: ["player", "profile", playerId],
    queryFn: () =>
      cmd.GET_PLAYER({
        params: { player_id: playerId },
        throwRouteError,
      }),
    select: (data) => normalizePlayerProfile(data),
  };
};

export const playerProfileQuery = (playerId, options) => {
  return useQuery({
    ...playerProfileQueryOptions(playerId, options),
  });
};
