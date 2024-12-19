import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import { getCompletedGameColumns } from '@/components/game/statistics/game-columns'
import { ScoreboardMapStats } from '@/types/api'
import { useOutletContext } from 'react-router'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { DataTable } from '@/components/game/statistics/game-table'

dayjs.extend(localizedFormat)

export default function GameDetail() {
  const { game } = useOutletContext<{ game: ScoreboardMapStats }>()

  return (
    <GameStatsContainer game={{
      id: String(game.id),
      player_stats: game.player_stats,
    }}>
      {(props) => (
        <DataTable
          columns={getCompletedGameColumns(props.handlePlayerClick)}
          data={game.player_stats}
          tableId={`${game.id}_${dayjs(game.start).format('YYYYMMDD-HHmm')}`}
        />
      )}
    </GameStatsContainer>
  )
}
