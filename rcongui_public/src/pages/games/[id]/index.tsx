import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import MapFigure from '@/components/game/map-figure'
import { gameQueries } from '@/lib/queries/scoreboard-maps'
import { getGameDuration } from '../utils'
import GameOverview from '@/components/game/overview'
import GameStats from '@/components/game/statistics/game-stats'
import { getCompletedGameColumns } from '@/components/game/statistics/game-columns'
import { useLoaderData } from 'react-router'
import { Helmet } from 'react-helmet'
import { useTranslation } from 'react-i18next'
import { clientLoader } from './clientLoader'
import { QueryErrorResetBoundary, useSuspenseQuery } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'
import { ScoreboardMapStats } from '@/types/api'

dayjs.extend(localizedFormat)

const GameDetail = ({ game }: { game: ScoreboardMapStats }) => {
  const { t: tNavigation } = useTranslation('navigation')

  const gameOverviewProps = {
    map: game.map,
    time: getGameDuration(game.start, game.end),
    axis: game.map.map.axis,
    allies: game.map.map.allies,
    mapName: game.map.pretty_name,
    mode: game.map.game_mode,
    score: {
      allies: game.result?.allied,
      axis: game.result?.axis,
    },
  }

  return (
    <>
      <Helmet>
        <title>{`${tNavigation('gameDetail')} - ${dayjs(game.start).format('L')} - ${game.map.map.pretty_name}`}</title>
      </Helmet>
      <div className="flex flex-col-reverse lg:flex-row divide-y lg:divide-y-0">
        <GameOverview {...gameOverviewProps} />
        <aside className="flex flex-row w-full lg:w-1/3 divide-x">
          <MapFigure
            text={dayjs(game.start).format('LLL')}
            src={`/maps/${game.map.image_name}`}
            name={game.map.map.pretty_name}
            className="w-full h-32 lg:h-full"
          />
        </aside>
      </div>
      <GameStats stats={game.player_stats} getColumns={getCompletedGameColumns} gameId={`${game.id}_${dayjs(game.start).format('YYYYMMDD-HHmm')}`} />
    </>
  )
}

export default function Page() {
  const { gameId } = useLoaderData() as Awaited<ReturnType<ReturnType<typeof clientLoader>>>
  const { data: game } = useSuspenseQuery(gameQueries.detail(gameId))

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
          <GameDetail game={game} />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}
