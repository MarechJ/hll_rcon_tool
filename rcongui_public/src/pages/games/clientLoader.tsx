import { gameQueries } from '@/lib/queries/scoreboard-maps'
import { QueryClient } from '@tanstack/react-query'
import { LoaderFunctionArgs } from 'react-router'

export const clientLoader =
  (queryClient: QueryClient) =>
  async ({ request }: LoaderFunctionArgs) => {
    const url = new URL(request.url)
    const pageParam = url.searchParams.get('page')
    const pageSizeParam = url.searchParams.get('pageSize')
    const page = pageParam ? parseInt(pageParam) : 1
    const pageSize = pageSizeParam ? parseInt(pageSizeParam) : 50

    await queryClient.ensureQueryData(gameQueries.list(page, pageSize))

    return { page, pageSize }
  }
