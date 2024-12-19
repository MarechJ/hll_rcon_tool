import { useOutletContext } from 'react-router'
import { ScoreboardMapStats } from '@/types/api'
import React, { useState, useMemo } from 'react'
import useMediaQuery from '@/hooks/use-media-query'
import { Player, PlayerWithStatus } from '@/types/player'
import { calcTeam } from '@/components/game/statistics/utils'
import PlayerGameDetail from '@/components/game/statistics/player'
import { MobilePlayerGameDetail, NoPlayerGameDetail } from '@/components/game/statistics/player-detail'
import { TeamStats } from '@/components/game/statistics/team/team-stats'

interface GameStatsProps {
  game: {
    id: string;
    player_stats: Player[] | PlayerWithStatus[];
  };
  children: (props: {
    handlePlayerClick: (playerId: string) => void;
    // ... any other props you want to pass
  }) => React.ReactNode;
}

export default function GameStatsContainer({ game, children }: GameStatsProps) {
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>()
  const [openDrawer, setOpenDrawer] = useState<boolean>(false)
  const isSmallScreen = useMediaQuery('screen and (max-width: 1023px)')

  const handlePlayerClick = (playerId: string) => {
    setSelectedPlayerId(playerId)
    setOpenDrawer(true)
  }

  const selectedPlayer = useMemo(
    () => game.player_stats.find((player) => player.player_id === selectedPlayerId),
    [game.player_stats, selectedPlayerId],
  )

  const childProps = {
    handlePlayerClick,
    selectedPlayer,
  }

  return (
    <section id={`game-statistics-${game.id}`}>
      <h2 className="sr-only">Game statistics</h2>
      <div className="relative flex flex-col-reverse lg:flex-row">
        <div className="w-full lg:w-2/3">
          {children(childProps)}
        </div>
        <aside className="hidden w-full lg:block lg:w-1/3 min-h-32">
          {selectedPlayer ? <PlayerGameDetail player={selectedPlayer} /> : <NoPlayerGameDetail />}
        </aside>
      </div>
      {isSmallScreen && selectedPlayer && (
        <MobilePlayerGameDetail open={openDrawer} setOpen={setOpenDrawer} player={selectedPlayer} />
      )}
    </section>
  )
}
