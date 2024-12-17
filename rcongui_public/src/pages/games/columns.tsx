'use client'

import { ColumnDef } from '@tanstack/react-table'
import dayjs from 'dayjs'
import LocalizedFormat from 'dayjs/plugin/localizedFormat'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router'
import { getGameDuration } from './utils'
import { ScoreboardMap } from '@/types/api'
import { MapLayer } from '@/types/mapLayer'
import { useTranslation } from 'react-i18next'

dayjs.extend(LocalizedFormat)

export const columns: ColumnDef<ScoreboardMap>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ cell }) => {
      const gameId = cell.getValue() as string
      return (
        <Button asChild variant={'link'}>
          <Link to={`/games/${gameId}`} className='w-10'>
            {gameId}
          </Link>
        </Button>
      )
    }
  },
  {
    header: function MapHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.map')
    },
    id: 'map',
    accessorKey: 'map',
    minSize: 200,
    size: 200,
    cell: function MapCell({ cell }) {
      const gameMap = cell.getValue() as MapLayer
      const size = 60
      const ratio = 9 / 16

      const { t } = useTranslation('game')

      return (
        <div className='flex flex-row items-center gap-2 w-max'>
          <img src={'/maps/icons/' + gameMap.image_name} width={size} height={size * ratio} alt='' />
          <div className='flex flex-col divide-y-2 p-1'>
            <div className='pl-1'>{gameMap.map.pretty_name}</div>
            <div className='divide-x-2 text-sm text-muted-foreground'>
              <span className='px-1'>{gameMap.game_mode[0].toUpperCase() + gameMap.game_mode.slice(1)}</span>
              <span className='pl-1'>{t(`weather.${gameMap.environment}`)}</span>
            </div>
          </div>
        </div>
      )
    }
  },
  {
    header: function ResultHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.result')
    },
    id: 'result',
    accessorFn: (row) => `${row.result?.allied ?? '?'} - ${row.result?.axis ?? '?'}`
  },
  {
    header: function StartHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.start')
    },
    accessorKey: 'start',
    cell: ({ cell }) => dayjs(cell.getValue() as string).format('L LT')
  },
  {
    header: function DurationHeader() {
      const { t } = useTranslation('game')
      return t('matchTable.duration')
    },
    accessorKey: 'duration',
    cell: ({ row }) => getGameDuration(row.original.start, row.original.end)
  }
]
