import { liveGameStatsOptions } from "@/lib/queries/live-game-stats"
import { liveSessionStatsOptions } from "@/lib/queries/live-session-stats"
import { publicInfoQueryOptions } from "@/lib/queries/public-info"
import { QueryClient } from "@tanstack/react-query"

export const clientLoader = (queryClient: QueryClient) => async () => {
  await queryClient.ensureQueryData(publicInfoQueryOptions)
  await queryClient.ensureQueryData(liveGameStatsOptions)
  await queryClient.ensureQueryData(liveSessionStatsOptions)
  return {}
}

