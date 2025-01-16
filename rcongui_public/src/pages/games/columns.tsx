'use client'

import {ColumnDef} from '@tanstack/react-table'
import dayjs from 'dayjs'
import LocalizedFormat from 'dayjs/plugin/localizedFormat'
import {Button} from '@/components/ui/button'
import {Link} from 'react-router'
import {getGameDuration} from './utils'
import {ScoreboardMap} from '@/types/api'
import {MapLayer} from '@/types/mapLayer'
import {useTranslation} from 'react-i18next'
import {dayjsLocal} from "@/lib/utils";
import WeatherIcon from "@/components/game/weather-icon";

dayjs.extend(LocalizedFormat)

export const columns: ColumnDef<ScoreboardMap>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ cell }) => {
      const gameId = cell.getValue() as string
      return (
        <Button asChild variant={'link'}>
          <Link to={`/games/${gameId}`} className="w-10">
            {gameId}
          </Link>
        </Button>
      )
    },
  },
  {
    header: function MapHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.map')
    },
    id: 'map',
    accessorKey: 'map',
    cell: function MapCell({ cell }) {
      const gameMap = cell.getValue() as MapLayer
      const size = 60
      const ratio = 9 / 16

      return (
        <div className="flex flex-row items-center gap-2 w-max">
          <img src={'/maps/icons/' + gameMap.image_name} width={size} height={size * ratio} alt=""/>
          <span>{gameMap.map.pretty_name}</span>
          <WeatherIcon environment={gameMap.environment} className="text-muted-foreground"/>
        </div>
      )
    },
  },
  {
    header: function Mode() {
      const {t} = useTranslation('game')
      return t('matchTable.mode')
    },
    id: 'map',
    accessorKey: 'map',
    cell: function MapCell({cell}) {
      const gameMap = cell.getValue() as MapLayer

      return (
        <div>
          <span>{gameMap.game_mode[0].toUpperCase() + gameMap.game_mode.slice(1)}</span>
          {gameMap.attackers &&
            <span> ({gameMap.map[gameMap.attackers].name.toUpperCase()})</span>
          }
        </div>
      )
    },
  },
  {
    header: function ResultHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.result')
    },
    id: 'result',
    accessorFn: (row) => `${row.result?.allied ?? '?'} - ${row.result?.axis ?? '?'}`,
  },
  {
    header: function WeekdayHeader() {
      const { t } = useTranslation('translation')
      return t('time.weekday')
    },
    accessorKey: 'start',
    cell: ({ cell }) => {
      const globalLocaleData = dayjs.localeData();
      return globalLocaleData.weekdaysShort()[dayjsLocal(cell.getValue() as string).day()];
    },
  },
  {
    header: function StartHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.start')
    },
    accessorKey: 'start',
    cell: ({ cell }) => dayjsLocal(cell.getValue() as string).format('L LT'),
  },
  {
    header: function DurationHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.duration')
    },
    accessorKey: 'duration',
    cell: ({ row }) => getGameDuration(row.original.start, row.original.end),
  },
]
