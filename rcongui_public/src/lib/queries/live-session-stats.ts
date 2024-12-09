import { queryOptions, useQuery } from '@tanstack/react-query'
import { LiveGameStats } from '@/types/api'
import { fetchApi } from '../api'
import { STALE_TIME, REFETCH_INTERVAL } from '../constants'
import { queryKeys } from '../queryKeys'

export async function fetchLiveSessionStats() {
  const response = await fetchApi<LiveGameStats>('/get_live_scoreboard')

  if (response.error && Array.isArray(response.error) && response.error[0] !== null) {
    throw new Error(response.error[0])
  }

  return response.result
}

export const liveSessionStatsOptions = queryOptions({
  queryKey: queryKeys.liveSessions,
  queryFn: fetchLiveSessionStats,
  staleTime: STALE_TIME,
  refetchInterval: REFETCH_INTERVAL,
})

export function useLiveSessionStats() {
  const { data, ...rest } = useQuery({
    ...liveSessionStatsOptions,
  })

  return [data, rest] as const
}
