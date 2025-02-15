import dayjs from 'dayjs'
import { getCompletedGameColumns } from "@/components/game/statistics/game-columns";
import { ScoreboardMapStats } from '@/types/api'
import { useOutletContext } from 'react-router'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { DataTable } from "@/components/game/statistics/game-table";
import React, {useMemo} from "react";
import {Player} from "@/types/player";
import {enrichPlayersWithAwards} from "@/pages/games/utils";

interface Award {
  type: string,
  amount: number,
}

export type PlayerBaseWithAwards = Player & { awards: Award[] }

export default function GameDetail() {
  const { game } = useOutletContext<{ game: ScoreboardMapStats }>()

  const playersWithAwards = useMemo(() => enrichPlayersWithAwards(game), [game]);

  return (
    <GameStatsContainer game={{
      id: String(game.id),
      player_stats: game.player_stats,
    }}>
      {(props) => (
        <DataTable
          columns={getCompletedGameColumns(props.handlePlayerClick)}
          data={playersWithAwards}
          tableId={`${game.id}_${dayjs(game.start).format('YYYYMMDD-HHmm')}`}
        />
      )}
    </GameStatsContainer>
  )
}
