import React, {useState, useMemo, createContext, useContext} from 'react'
import useMediaQuery from '@/hooks/use-media-query'
import { Player, PlayerWithStatus } from '@/types/player'
import PlayerGameDetail from '@/components/game/statistics/player'
import { MobilePlayerGameDetail, NoPlayerGameDetail } from '@/components/game/statistics/player-detail'

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

interface GameStatsContextProps {
  handlePlayerClickByName: (name: string) => void;
}

const GameStatsContext = createContext<GameStatsContextProps | null>(null);

export function useGameStatsContext() {
  const context = useContext(GameStatsContext);

  if (!context) {
    throw new Error('useGameStatsContext must be used within a <GameStats />');
  }

  return context;
}

export default function GameStatsContainer({ game, children }: GameStatsProps) {
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>()
  const [openDrawer, setOpenDrawer] = useState<boolean>(false)
  const isSmallScreen = useMediaQuery('screen and (max-width: 1023px)')

  const handlePlayerClick = (playerId: string) => {
    setSelectedPlayerId(playerId)
    setOpenDrawer(true)
  }

  const handlePlayerClickByName = (name: string) => {
    const id = game.player_stats.find(player => player.player === name)?.player_id;
    if (id) {
      handlePlayerClick(id);
    }
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
    <GameStatsContext.Provider value={{handlePlayerClickByName}}>
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
    </GameStatsContext.Provider>
  )
}
