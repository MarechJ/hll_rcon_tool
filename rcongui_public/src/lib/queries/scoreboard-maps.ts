import { queryOptions, useQuery } from '@tanstack/react-query'
import { fetchApi } from '../api'
import { ScoreboardMaps, ScoreboardMapStats } from '@/types/api'
import { queryKeys } from '../queryKeys'
import { calcTeam } from '@/components/game/statistics/utils'

const DEFAULT_PAGE = 1
const DEFAULT_PAGE_SIZE = 50

export async function fetchGames(page?: number, pageSize?: number) {
  const response = await fetchApi<ScoreboardMaps>(
    `/get_scoreboard_maps?page=${page ?? DEFAULT_PAGE}&limit=${pageSize ?? DEFAULT_PAGE_SIZE}`,
  )

  if (response.error) {
    throw new Error(response.error)
  }

  return response.result
}

export async function fetchGameDetail(gameId: number) {
  const response = await fetchApi<ScoreboardMapStats>(`/get_map_scoreboard?map_id=${gameId}`)

  if (response.error) {
    throw new Error(response.error)
  }

  return response.result
}

export const gameQueries = {
  list: (page?: number | undefined, pageSize?: number | undefined) =>
    queryOptions({
      queryKey: queryKeys.games(page ?? DEFAULT_PAGE, pageSize ?? DEFAULT_PAGE_SIZE),
      queryFn: () => fetchGames(page ?? DEFAULT_PAGE, pageSize ?? DEFAULT_PAGE_SIZE),
    }),
  detail: (gameId: number, enabled?: boolean) =>
    queryOptions({
      queryKey: queryKeys.gameDetail(gameId),
      queryFn: async () => {
        // Minimum time to be considered in the game
        // This is to avoid showing players that are just in the game for a few seconds
        const MIN_TIME_SECONDS = 15
        const game = await fetchGameDetail(gameId)
        const playerStatsWithTeam = game.player_stats
          .filter(player => player.time_seconds > MIN_TIME_SECONDS)
          .map(player => ({
            ...player,
            team: calcTeam(player.kills, player.weapons),
          }))
        return {
          ...game,
          player_stats: playerStatsWithTeam,
        }
      },
      enabled: enabled ?? true,
    }),
}

export function useGames(page = DEFAULT_PAGE, pageSize = DEFAULT_PAGE_SIZE) {
  const { data, ...rest } = useQuery(gameQueries.list(page, pageSize))

  return [data, rest] as const
}

export function useGameDetail(gameId: number, enabled?: boolean) {
  const { data, ...rest } = useQuery(gameQueries.detail(gameId, enabled))

  return [data, rest] as const
}
