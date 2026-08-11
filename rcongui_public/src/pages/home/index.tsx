import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import { getLiveGameColumns } from '@/components/game/statistics/game-columns'
import { useOutletContext } from 'react-router'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { DataTable } from '@/components/game/statistics/game-table'
import React from 'react'
import { QueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'
import { GameLiveOutletContext } from '@/pages/home/layout'

dayjs.extend(localizedFormat)

export default function GameDetailLive() {
  const { liveStats, game } = useOutletContext<GameLiveOutletContext>()
  const livePlayers = liveStats.stats
    .filter((player) => player.time_seconds > 15)
    .toSorted((a, b) => {
      const online = (player: typeof a) => (player.status === 'online' ? 0 : 1)
      const team = (player: typeof a) => (player.status === 'online' && player.team ? 0 : 1)
      return online(a) - online(b) || team(a) - team(b) || b.kills - a.kills
    })

  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ error, resetErrorBoundary }) => (
            <div className="grid place-items-center w-full h-[200px]">
              <div className="text-red-500">{error.message}</div>
              <button onClick={resetErrorBoundary}>Try again</button>
            </div>
          )}
        >
          <React.Suspense fallback={<div className="grid place-items-center w-full h-[200px]" />}>
            <GameStatsContainer
              game={{
                id: `live_${dayjs(game.current_map.start * 1000).format('YYYYMMDD-HHmm')}`,
                player_stats: livePlayers,
                cap_flips: game.cap_flips,
                duration_seconds: Math.max(0, liveStats.snapshot_timestamp - game.current_map.start),
              }}
            >
              {(props) => (
                <DataTable
                  columns={getLiveGameColumns(props.handlePlayerClick)}
                  data={livePlayers}
                  tableId={`live_${dayjs(game.current_map.start * 1000).format('YYYYMMDD-HHmm')}`}
                />
              )}
            </GameStatsContainer>
          </React.Suspense>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}
