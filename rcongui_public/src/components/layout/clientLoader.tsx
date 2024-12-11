import { publicInfoQueryOptions } from "@/lib/queries/public-info"
import { QueryClient } from "@tanstack/react-query"

export const clientLoader = (queryClient: QueryClient) => async () => {
    await queryClient.ensureQueryData(publicInfoQueryOptions)
  return {}
}
