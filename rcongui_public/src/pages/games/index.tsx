import GamesList from './list'
import { useLoaderData } from 'react-router'
import { Helmet } from 'react-helmet'
import { useTranslation } from 'react-i18next'
import { QueryErrorResetBoundary, useSuspenseQuery } from '@tanstack/react-query'
import { clientLoader } from './clientLoader'
import { gameQueries } from '@/lib/queries/scoreboard-maps'
import { ErrorBoundary } from 'react-error-boundary'

export default function GamesPage() {
  const { page, pageSize } = useLoaderData() as Awaited<ReturnType<ReturnType<typeof clientLoader>>>
  const { data: games } = useSuspenseQuery(gameQueries.list(page, pageSize))
  const { t } = useTranslation('navigation')

  return (
    <>
      <Helmet>
        <title>{t('gameHistory')}</title>
      </Helmet>
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
          >
            <GamesList games={games} page={page} pageSize={pageSize} />
          </ErrorBoundary>
        )}
      </QueryErrorResetBoundary>
    </>
  )
}
