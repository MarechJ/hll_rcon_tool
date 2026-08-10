import React, { useState, useMemo, createContext, useContext } from 'react'
import useMediaQuery from '@/hooks/use-media-query'
import { Player, PlayerUnit } from '@/types/player'
import { MatchScore } from '@/types/api'
import PlayerGameDetail from '@/components/game/statistics/player'
import { MobilePlayerGameDetail, NoPlayerGameDetail } from '@/components/game/statistics/player-detail'

interface GameStatsProps {
  game: {
    id: string
    player_stats: Player[]
    cap_flips?: MatchScore[]
    duration_seconds?: number
  }
  children: (props: {
    handlePlayerClick: (playerId: string) => void
    // ... any other props you want to pass
  }) => React.ReactNode
}

export interface GamePlayer {
  name: string
  id: string
  units?: PlayerUnit[]
}

interface GameStatsContextProps {
  players: GamePlayer[]
  capFlips: MatchScore[]
  gameDuration: number
  focusPlayerBy: ({ name, id }: { name?: string; id?: string }) => void
  focusedPlayerId: string | null
  setFocusedPlayerId: React.Dispatch<React.SetStateAction<string | null>>
}

const GameStatsContext = createContext<GameStatsContextProps | null>(null)

export function useGameStatsContext() {
  const context = useContext(GameStatsContext)

  if (!context && process.env.NODE_ENV === 'development') {
    // In development, return a fallback or log a warning instead of throwing an error
    console.warn('useGameStatsContext must be used within a <GameStats />')
    return {
      focusPlayerBy: () => {},
      players: [],
      capFlips: [],
      gameDuration: 0,
      focusedPlayerId: null,
      setFocusedPlayerId: () => null,
    }
  }

  if (!context) {
    throw new Error('useGameStatsContext must be used within a <GameStats />')
  }

  return context
}

function GameStatsContent({
  game,
  children,
  selectedPlayer,
  handlePlayerClick,
  isSmallScreen,
  openDrawer,
  setOpenDrawer,
  focusPlayerBy,
  players,
}: {
  game: GameStatsProps['game']
  children: GameStatsProps['children']
  selectedPlayer?: Player
  handlePlayerClick: (playerId: string) => void
  isSmallScreen: boolean
  openDrawer: boolean
  setOpenDrawer: (open: boolean) => void
  focusPlayerBy: ({ name, id }: { name?: string; id?: string }) => void
  players: GamePlayer[]
}) {
  return (
    <section id={`game-statistics-${game.id}`}>
      <h2 className="sr-only">Game statistics</h2>
      <div className="relative flex flex-col-reverse lg:flex-row">
        <div className="w-full lg:w-2/3">{children({ handlePlayerClick })}</div>
        <aside className="hidden w-full lg:block lg:w-1/3 min-h-32">
          {selectedPlayer ? (
            <PlayerGameDetail
              player={selectedPlayer}
              focusPlayerBy={focusPlayerBy}
              players={players}
              capFlips={game.cap_flips ?? []}
            />
          ) : (
            <NoPlayerGameDetail />
          )}
        </aside>
      </div>
      {isSmallScreen && selectedPlayer && (
        <MobilePlayerGameDetail open={openDrawer} setOpen={setOpenDrawer} player={selectedPlayer} />
      )}
    </section>
  )
}

export default function GameStatsContainer({ game, children }: GameStatsProps) {
  const players = useMemo(
    () =>
      game.player_stats.map((stat) => ({
        name: stat.player,
        id: stat.player_id,
        units: 'units' in stat ? stat.units : undefined,
      })),
    [game.player_stats],
  )
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | undefined>()
  const [focusedPlayerId, setFocusedPlayerId] = useState<string | null>(null)
  const [openDrawer, setOpenDrawer] = useState<boolean>(false)
  const isSmallScreen = useMediaQuery('screen and (max-width: 1023px)')

  const handlePlayerClick = (playerId: string) => {
    setSelectedPlayerId(playerId)
    setOpenDrawer(true)
  }

  const focusPlayerBy = ({ name, id }: { name?: string; id?: string }) => {
    const playerId = game.player_stats.find((player) => {
      if (name !== undefined) {
        return player.player === name
      } else if (id !== undefined) {
        return player.player_id === id
      } else {
        return false
      }
    })?.player_id
    if (playerId) {
      if (isSmallScreen) {
        setSelectedPlayerId(undefined)
      }
      setFocusedPlayerId(playerId)
    }
  }

  const selectedPlayer = useMemo(
    () => game.player_stats.find((player) => player.player_id === selectedPlayerId),
    [game.player_stats, selectedPlayerId],
  )

  return (
    <GameStatsContext.Provider
      value={{
        players,
        capFlips: game.cap_flips ?? [],
        gameDuration: game.duration_seconds ?? 0,
        focusPlayerBy,
        focusedPlayerId,
        setFocusedPlayerId,
      }}
    >
      <GameStatsContent
        game={game}
        selectedPlayer={selectedPlayer}
        handlePlayerClick={handlePlayerClick}
        isSmallScreen={isSmallScreen}
        openDrawer={openDrawer}
        setOpenDrawer={setOpenDrawer}
        focusPlayerBy={focusPlayerBy}
        players={players}
      >
        {children}
      </GameStatsContent>
    </GameStatsContext.Provider>
  )
}
