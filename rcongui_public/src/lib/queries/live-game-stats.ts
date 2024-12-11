import { queryOptions, useQuery } from '@tanstack/react-query'
import { LiveGameStats } from '@/types/api'
import { fetchApi } from '../api'
import { STALE_TIME, REFETCH_INTERVAL } from '../constants'
import { queryKeys } from '../queryKeys'

export async function fetchLiveGameStats() {
  const response = await fetchApi<LiveGameStats>('/get_live_game_stats')

  if (response.error) {
    throw new Error(response.error)
  }

  return response.result
}

export const liveGameStatsOptions = queryOptions({
  queryKey: queryKeys.liveStats,
  queryFn: fetchLiveGameStats,
  staleTime: STALE_TIME,
  refetchInterval: REFETCH_INTERVAL,
})

export function useLiveGameStats() {
  const { data, ...rest } = useQuery({
    ...liveGameStatsOptions,
  })

  return [data, rest] as const
}
