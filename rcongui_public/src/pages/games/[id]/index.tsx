import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import MapFigure from '@/components/game/map-figure'
import { useGameDetail } from '@/lib/queries/scoreboard-maps'
import { getGameDuration } from '../utils'
import GameOverview from '@/components/game/overview'
import GameStats from '@/components/game/statistics/game-stats'
import { getCompletedGameColumns } from '@/components/game/statistics/game-columns'
import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet'
import { useTranslation } from 'react-i18next'

dayjs.extend(localizedFormat)

export default function GameDetail() {
  const { id: gameId } = useParams()
  const { t: tNavigation } = useTranslation('navigation')
  const { t: tGame } = useTranslation('game')

  const [game, { isLoading, isError }] = useGameDetail(Number(gameId), !!gameId && !Number.isNaN(Number(gameId)))

  if (isLoading) {
    return (
      <>
        <Helmet>
          <title>{`${tNavigation('gameDetail')} - ${gameId} - ${tGame('loading')}`}</title>
        </Helmet>
        <div>{tGame('loading')}</div>
      </>
    )
  }

  if (!game || isError) {
    return (
      <>
        <Helmet>
          <title>{`${tNavigation('gameDetail')} - ${gameId} - ${tGame('gameNotFound', { id: gameId })}`}</title>
        </Helmet>
        <h1>{tGame('gameNotFound', { id: gameId })}</h1>
      </>
    )
  }

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
      <GameStats stats={game.player_stats} getColumns={getCompletedGameColumns} />
    </>
  )
}
