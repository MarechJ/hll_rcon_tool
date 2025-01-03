'use client'

import React, {Suspense} from 'react'
import {Outlet, useLoaderData} from 'react-router'
import {gameQueries} from '@/lib/queries/scoreboard-maps'
import {clientLoader} from './clientLoader'
import {QueryErrorResetBoundary, useSuspenseQuery} from '@tanstack/react-query'
import {ErrorBoundary} from 'react-error-boundary'
import {HorizontalGamesList} from "@/pages/games/horizontal-games-list";

export default function GamesLayout() {
  const { page, pageSize } = useLoaderData() as Awaited<ReturnType<ReturnType<typeof clientLoader>>>
  const { data: games } = useSuspenseQuery(gameQueries.list(page, pageSize))

  return (
    <>
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
            <Suspense fallback={<div>Loading...</div>}>
              <HorizontalGamesList games={games}/>
            </Suspense>
          </ErrorBoundary>
        )}
      </QueryErrorResetBoundary>
      <Outlet />
    </>
  )
}
