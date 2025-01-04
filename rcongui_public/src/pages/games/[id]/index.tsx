import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import { extraColumns, getCompletedGameColumns } from "@/components/game/statistics/game-columns";
import { ScoreboardMapStats } from '@/types/api'
import { useOutletContext } from 'react-router'
import GameStatsContainer from '@/components/game/statistics/game-stats-container'
import { DataTable, ExtraColumnDef } from "@/components/game/statistics/game-table";
import { useState } from "react";
import { useTranslation } from "react-i18next";

dayjs.extend(localizedFormat)

export default function GameDetail() {
  const { game } = useOutletContext<{ game: ScoreboardMapStats }>()
  const { t } = useTranslation('game')
  const [extraColumns, setExtraColumns] = useState<ExtraColumnDef<extraColumns>[]>([{
    id: 'kpm',
    label: t('playersTable.killsPerMinute'),
    displayed: false,
  }, {
    id: 'dpm',
    label: t('playersTable.deathsPerMinute'),
    displayed: false,
  }]);

  return (
    <GameStatsContainer game={{
      id: String(game.id),
      player_stats: game.player_stats,
    }}>
      {(props) => (
        <DataTable
          columns={getCompletedGameColumns(props.handlePlayerClick, extraColumns.filter((e) => e.displayed).map((e) => e.id))}
          extraColumns={extraColumns}
          onExtraColumnChange={(extra) => {
            setExtraColumns((current) => {
              return current.map((c) => ({
                ...c,
                displayed: extra.includes(c.id),
              }));
            })
          }}
          data={game.player_stats}
          tableId={`${game.id}_${dayjs(game.start).format('YYYYMMDD-HHmm')}`}
        />
      )}
    </GameStatsContainer>
  )
}
