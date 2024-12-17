import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';
import { getBaseURL } from '@shared/lib/getBaseURL';
import { Broken_CRCON_Response, LiveGameStats } from './types';

const baseURL = getBaseURL();

export async function fetchLiveSessionStats() {
  const response = await fetch(
    `${baseURL}/api/get_live_scoreboard`, { next: { revalidate: 15 } }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: Broken_CRCON_Response<LiveGameStats> = await response.json()

  if (data && data.error) {
    if (data.error[0]) {
        throw new Error(data.error[0]);
    }
  }

  return data;
}

export const liveSessionStatsOptions = queryOptions({
  queryKey: [{ queryIdentifier: 'live-session-stats' }],
  queryFn: fetchLiveSessionStats,
  staleTime: 5 * 1000,
  refetchInterval: 15 * 1000,
});

export function useLiveSessionStatsQuery() {
  const query = useSuspenseQuery(liveSessionStatsOptions);

  return [query.data.result, query] as const;
}
