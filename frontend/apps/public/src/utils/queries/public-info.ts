import { queryOptions, useSuspenseQuery } from '@tanstack/react-query';
import { getBaseURL } from '@shared/lib/getBaseURL';
import { CRCON_Response, PublicInfo } from './types';

const baseURL = getBaseURL();

export async function fetchPublicInfo() {
  const response = await fetch(
    `${baseURL}/api/get_public_info`, { next: { revalidate: 15 } }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: CRCON_Response<PublicInfo> = await response.json()

  if (data && data.error) {
    throw new Error(data.error);
  }

  return data;
}

export const publicInfoOptions = queryOptions({
  queryKey: [{ queryIdentifier: 'public-info' }],
  queryFn: fetchPublicInfo,
  staleTime: 5 * 1000,
  refetchInterval: 15 * 1000,
});

export function usePublicInfoQuery() {
  const query = useSuspenseQuery(publicInfoOptions);

  return [query.data.result, query] as const;
}
