import { cmd } from "@/utils/fetchUtils";
import { queryOptions } from "@tanstack/react-query";

export const gameQueryOptions = {
  list: (page, pageSize) =>
    queryOptions({
      queryKey: [{ queryIdentifier: "scoreboard-maps", page, pageSize }],
      queryFn: () =>
        cmd.GET_COMPLETED_GAMES({
          params: { page: page ?? 1, limit: pageSize ?? 50 },
        }),
    }),
  detail: (gameId) =>
    queryOptions({
      queryKey: [{ queryIdentifier: "map-scoreboard", gameId }],
      queryFn: () => cmd.GET_COMPLETED_GAME_DETAIL({ params: { gameId } }),
    }),
  live: () =>
    queryOptions({
      queryKey: [{ queryIdentifier: "get_live_game_stats" }],
      queryFn: () => cmd.GET_LIVE_GAME(),
      refetchInterval: 15 * 1000,
    }),
  sessions: () =>
    queryOptions({
      queryKey: [{ queryIdentifier: "get_live_scoreboard" }],
      queryFn: () => cmd.GET_LIVE_SESSIONS(),
      refetchInterval: 15 * 1000,
    }),
};

export const useGameDetailQuery = (gameId) => {
  return useQuery({
    ...gameQueryOptions.detail(gameId),
  });
};

export const useLiveGameQuery = () => {
  return useQuery({
    ...gameQueryOptions.live(),
  });
};

export const useLiveSessionsQuery = () => {
  return useQuery({
    ...gameQueryOptions.sessions(),
  });
};

export const useGameListQuery = (page, pageSize) => {
  return useQuery({
    ...gameQueryOptions.list(page, pageSize),
  });
};
