import { publicInfoQueryOptions } from '@/lib/queries/public-info'
import dayjs from 'dayjs'
import { Helmet } from 'react-helmet'
import duration from 'dayjs/plugin/duration'
import { useTranslation } from 'react-i18next'
import LiveGameInfo from './live-game-info'
import { Spinner } from '@/components/spinner'
import { QueryErrorResetBoundary, useSuspenseQueries, useSuspenseQuery } from '@tanstack/react-query'
import { PlayerWithStatus } from '@/types/player'
import { liveSessionStatsOptions } from '@/lib/queries/live-session-stats'
import { liveGameStatsOptions } from '@/lib/queries/live-game-stats'
import React from "react";
import { ErrorBoundary } from 'react-error-boundary'
import {Outlet} from "react-router";
import {PublicInfo} from "@/types/api";

dayjs.extend(duration)

export interface LiveStats {
  data: PlayerWithStatus[],
  pending: boolean,
}

interface GameLiveLayoutProps {
  liveStats: LiveStats;
  game: PublicInfo,
  isLoading: boolean,
  isError: boolean,
}

export interface GameLiveOutletContext {
  liveStats: LiveStats,
  game: PublicInfo,
}

function GameLiveLayout({liveStats, game, isLoading, isError}: GameLiveLayoutProps) {
  const { t } = useTranslation('navigation')
  const { t: tNotFound } = useTranslation('notfound')

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
                  <LiveGameInfo game={game} />
                </React.Suspense>
              </ErrorBoundary>
            )}
          </QueryErrorResetBoundary>

          <Outlet context={{ liveStats, game }} />
        </>
      )}
    </>
  )
}

export default function Page() {
  const { data: game, isLoading, isError } = useSuspenseQuery(publicInfoQueryOptions);

  const liveStats: { data: PlayerWithStatus[]; pending: boolean } = useSuspenseQueries({
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
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          fallbackRender={({ error, resetErrorBoundary }) => (
            <div>
              <p>An error occurred:</p>
              <pre>{error.message}</pre>
              <button onClick={resetErrorBoundary}>Try again</button>
            </div>
          )}
          onReset={reset}
        >
          <GameLiveLayout liveStats={liveStats} game={game} isLoading={isLoading} isError={isError}/>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}
