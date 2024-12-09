import { usePublicInfo } from '@/lib/queries/public-info'
import dayjs from 'dayjs'
import { Helmet } from 'react-helmet'
import duration from 'dayjs/plugin/duration'
import { useTranslation } from 'react-i18next'
import LiveGameInfo from './live-game-info'
import { Spinner } from '@/components/spinner'
import GameStats from '@/components/game/statistics/game-stats'
import { useQueries } from '@tanstack/react-query'
import { getLiveGameColumns } from '@/components/game/statistics/game-columns'
import { PlayerWithStatus } from '@/types/player'
import { liveSessionStatsOptions } from '@/lib/queries/live-session-stats'
import { liveGameStatsOptions } from '@/lib/queries/live-game-stats'
import React from 'react'

dayjs.extend(duration)

export default function Home() {
  const { t } = useTranslation('navigation')
  const { t: tNotFound } = useTranslation('notfound')

  const [game, { isLoading, isError }] = usePublicInfo()

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

  if (isError) {
    throw new Error(tNotFound('connectionError'))
  }

  return (
    <>
      {isLoading || !game ? (
        <div className="grid place-items-center w-full h-[200px]">
          <Spinner />
        </div>
      ) : (
        <>
          <Helmet>
            <title>{t('currentGame')}</title>
          </Helmet>
          <React.Suspense fallback={<div className="grid place-items-center w-full h-[200px]" />}>
            <LiveGameInfo game={game} />
          </React.Suspense>
          <React.Suspense fallback={<div className="grid place-items-center w-full h-[200px]" />}>
            <GameStats
              stats={liveStats.data.filter((player) => player.time_seconds > 30)}
              getColumns={getLiveGameColumns}
            />
          </React.Suspense>
        </>
      )}
    </>
  )
}
