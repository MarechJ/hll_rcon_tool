import {
  queryOptions,
  useSuspenseQuery,
} from '@tanstack/react-query';
import { getBaseURL } from '@shared/lib/getBaseURL';
import { CRCON_Response, ScoreboardMap, ScoreboardMaps, ScoreboardMapStats } from './types';

const baseURL = getBaseURL();

export async function fetchGames(page?: number, pageSize?: number) {
  const path = new URL(`${baseURL}/api/get_scoreboard_maps`)
  if (page !== undefined) path.searchParams.append("page", String(page));
  if (pageSize !== undefined) path.searchParams.append("limit", String(pageSize));

  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: CRCON_Response<ScoreboardMaps> = await response.json();

  if (data && data.error) {
    throw new Error(data.error);
  }

  return data;
}

export async function fetchGameDetail(gameId: number) {
  const response = await fetch(
    `${baseURL}/api/get_map_scoreboard?map_id=${gameId}`
  );

  const data: CRCON_Response<ScoreboardMapStats> = await response.json();

  if (data && data.error) {
    throw new Error(data.error);
  }

  return data;
}

export const gameQueries = {
  list: (page?: number, pageSize?: number) => queryOptions({
    queryKey: [{ queryIdentifier: 'scoreboard-maps', page, pageSize }],
    queryFn: () => fetchGames(page ?? 1, pageSize ?? 50),
  }),
  detail: (gameId: number) =>
    queryOptions({
      queryKey: [{ queryIdentifier: 'map-scoreboard', gameId }],
      queryFn: () => fetchGameDetail(gameId),
    }),
};

export function useGamesQuery() {
  const query = useSuspenseQuery(gameQueries.list());

  return [query.data.result, query] as const;
}

export function useGameDetailQuery(gameId: number) {
  const query = useSuspenseQuery(gameQueries.detail(gameId));

  return [query.data.result, query] as const;
}
