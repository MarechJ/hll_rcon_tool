import { gameQueries } from "@/lib/queries/scoreboard-maps"
import { QueryClient } from "@tanstack/react-query"
import { LoaderFunctionArgs } from "react-router"

export const clientLoader = (queryClient: QueryClient) => async ({ params }: LoaderFunctionArgs) => {
  const { id } = params
  if (!id || !Number.isInteger(Number(id))) {
    throw new Error(`Invalid game ID: ${id}`)
  }
  const gameId = Number(id)
  await queryClient.ensureQueryData(gameQueries.detail(gameId))
  return { gameId }
}
