import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';
import { getBaseURL } from '@shared/lib/getBaseURL';
import { CRCON_Response, LiveGameStats } from './types';

const baseURL = getBaseURL();

export async function fetchLiveGameStats() {
  const response = await fetch(
    `${baseURL}/api/get_live_game_stats`, { next: { revalidate: 15 } }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: CRCON_Response<LiveGameStats> = await response.json()

  if (data && data.error) {
    throw new Error(data.error);
  }

  return data;
}

export const liveGameStatsOptions = queryOptions({
  queryKey: [{ queryIdentifier: 'live-game-stats' }],
  queryFn: fetchLiveGameStats,
  staleTime: 5 * 1000,
  refetchInterval: 15 * 1000,
});

export function useLiveGameStatsQuery() {
  const query = useSuspenseQuery(liveGameStatsOptions);

  return [query.data.result, query] as const;
}
