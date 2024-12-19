import { cmd } from '@/utils/fetchUtils'
import { normalizePlayerProfile } from '@/utils/lib'

export const playerProfileQueryOptions = (playerId, options) => {
  const { throwRouteError = true } = options
  return {
    queryKey: ['player', 'profile', playerId],
    queryFn: () =>
      cmd.GET_PLAYER({
        params: { player_id: playerId },
        throwRouteError
      }),
    select: (data) => {
      return data ? normalizePlayerProfile(data) : data
    }
  }
}
