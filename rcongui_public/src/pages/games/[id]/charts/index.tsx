import { useOutletContext } from 'react-router'
import { ScoreboardMapStats } from '@/types/api'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { TeamStats } from '@/components/game/statistics/team/team-stats'
import dayjs from 'dayjs'

export default function Charts() {
  const { game } = useOutletContext<{ game: ScoreboardMapStats }>()

  return (
    <GameStatsContainer
      game={{
        id: String(game.id),
        player_stats: game.player_stats,
        cap_flips: game.cap_flips,
        duration_seconds: dayjs(game.end).diff(dayjs(game.start), 'second'),
      }}
    >
      {(props) => <TeamStats stats={game.player_stats} handlePlayerClick={props.handlePlayerClick} />}
    </GameStatsContainer>
  )
}
