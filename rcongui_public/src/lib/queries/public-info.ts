import { PublicInfo } from '@/types/api'
import { fetchApi } from '../api'
import { queryOptions, useQuery } from '@tanstack/react-query'
import { queryKeys } from '../queryKeys'
import { REFETCH_INTERVAL, STALE_TIME } from '../constants'

export const fetchPublicInfo = async (): Promise<PublicInfo> => {
  const response = await fetchApi<PublicInfo>('/get_public_info')

  if (response.error) {
    throw new Error(response.error)
  }

  return response.result
}

export const publicInfoQueryOptions = queryOptions({
  queryKey: queryKeys.publicInfo,
  queryFn: fetchPublicInfo,
  staleTime: STALE_TIME,
  refetchInterval: REFETCH_INTERVAL
})

export const usePublicInfo = () => {
  const { data, ...rest } = useQuery({
    ...publicInfoQueryOptions
  })

  return [data, rest] as const
}
