'use client'

import GameStats from '@/components/game/statistics/game-stats'
import { useQueries } from '@tanstack/react-query'
import { getLiveGameColumns } from '@/components/game/statistics/game-columns'
import { PlayerWithStatus } from '@/types/player'
import { liveSessionStatsOptions } from '@/lib/queries/live-session-stats'
import { liveGameStatsOptions } from '@/lib/queries/live-game-stats'

export default function LiveGameStats() {
  const liveStats: { data: PlayerWithStatus[]; pending: boolean } = useQueries({
    queries: [liveGameStatsOptions, liveSessionStatsOptions],
    combine: (results) => {
      const allPlayers = results[0].data?.stats ?? []
      const onlinePlayers = results[1].data?.stats?.map((player) => player.player_id) ?? []

      const onlinePlayersSet = new Set(onlinePlayers)

      const data = allPlayers?.map((player) => ({
        ...player,
        is_online: onlinePlayersSet.has(player.player_id),
      }))

      return {
        data: data,
        pending: results.some((result) => result.isPending),
      }
    },
  })

  return (
    <GameStats stats={liveStats.data.filter((player) => player.time_seconds > 30)} getColumns={getLiveGameColumns} />
  )
}
