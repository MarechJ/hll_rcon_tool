import { publicInfoQueryOptions } from '@/lib/queries/public-info'
import dayjs from 'dayjs'
import { Helmet } from 'react-helmet'
import duration from 'dayjs/plugin/duration'
import { useTranslation } from 'react-i18next'
import LiveGameInfo from './live-game-info'
import { Spinner } from '@/components/spinner'
import { QueryErrorResetBoundary, useSuspenseQuery } from '@tanstack/react-query'
import { liveGameStatsOptions } from '@/lib/queries/live-game-stats'
import React from "react";
import { ErrorBoundary } from 'react-error-boundary'
import {Outlet} from "react-router";
import {LiveGameStats, PublicInfo} from "@/types/api";

dayjs.extend(duration)

interface GameLiveLayoutProps {
  liveStats: LiveGameStats;
  game: PublicInfo,
  isLoading: boolean,
  isError: boolean,
}

export interface GameLiveOutletContext {
  liveStats: LiveGameStats,
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
  const { data: stats } = useSuspenseQuery(liveGameStatsOptions);

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
          <GameLiveLayout liveStats={stats} game={game} isLoading={isLoading} isError={isError}/>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}
