import { useOutletContext } from 'react-router'
import { ScoreboardMapStats } from '@/types/api'
import { DataTable } from '@/components/game/statistics/game-table'
import { getCompletedGameColumns } from '@/components/game/statistics/game-columns'
import dayjs from 'dayjs'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { TeamStats } from '@/components/game/statistics/team/team-stats'

export default function Charts() {
  const { game } = useOutletContext<{ game: ScoreboardMapStats }>()

  return (
    <GameStatsContainer game={{
      id: String(game.id),
      player_stats: game.player_stats,
    }}>
      {(props) => (
        <TeamStats stats={game.player_stats} handlePlayerClick={props.handlePlayerClick} />
      )}
    </GameStatsContainer>
  )
}
