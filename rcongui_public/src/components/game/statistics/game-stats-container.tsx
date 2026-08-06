import React, {useState, useMemo, createContext, useContext} from 'react'
import useMediaQuery from '@/hooks/use-media-query'
import { Player } from '@/types/player'
import PlayerGameDetail from '@/components/game/statistics/player'
import { MobilePlayerGameDetail, NoPlayerGameDetail } from '@/components/game/statistics/player-detail'

interface GameStatsProps {
  game: {
    id: string;
    player_stats: Player[];
  };
  children: (props: {
    handlePlayerClick: (playerId: string) => void;
    // ... any other props you want to pass
  }) => React.ReactNode;
}

export interface GamePlayer {
  name: string;
  id: string;
}

interface GameStatsContextProps {
  players: GamePlayer[];
  focusPlayerBy: ({ name, id } : { name?: string, id?: string }) => void;
  focusedPlayerId: string | null;
  setFocusedPlayerId: React.Dispatch<React.SetStateAction<string | null>>;
}

const GameStatsContext = createContext<GameStatsContextProps | null>(null);

export function useGameStatsContext() {
  const context = useContext(GameStatsContext);

  if (!context && process.env.NODE_ENV === "development") {
    // In development, return a fallback or log a warning instead of throwing an error
    console.warn(
      'useGameStatsContext must be used within a <GameStats />'
    );
    return {
      focusPlayerBy: ({ name, id } : { name?: string, id?: string }) => {},
      players: [],
      focusedPlayerId: null,
      setFocusedPlayerId: () => null,
    };
  }

  if (!context) {
    throw new Error('useGameStatsContext must be used within a <GameStats />');
  }

  return context;
}

export default function GameStatsContainer({ game, children }: GameStatsProps) {
  const players = useMemo(
    () => game.player_stats.map(({ player, player_id }) => ({ name: player, id: player_id })),
    [game.player_stats],
  )
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>()
  const [focusedPlayerId, setFocusedPlayerId] = useState<string | null>(null);
  const [openDrawer, setOpenDrawer] = useState<boolean>(false)
  const isSmallScreen = useMediaQuery('screen and (max-width: 1023px)')

  const handlePlayerClick = (playerId: string) => {
    setSelectedPlayerId(playerId)
    setOpenDrawer(true)
  }

  const focusPlayerBy = ({ name, id } : { name?: string, id?: string }) => {
    const playerId = game.player_stats.find(player => {
      if (name !== undefined) {
        return player.player === name
      } else if (id !== undefined) {
        return player.player_id === id
      } else {
        return false
      }
    })?.player_id;
    if (playerId) {
      if (isSmallScreen) {
        setSelectedPlayerId(undefined);
      }
      setFocusedPlayerId(playerId);
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
    <GameStatsContext.Provider value={{players, focusPlayerBy, focusedPlayerId, setFocusedPlayerId}}>
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
