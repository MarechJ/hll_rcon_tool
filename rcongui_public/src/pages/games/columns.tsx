'use client'

import { ColumnDef } from '@tanstack/react-table'
import dayjs from 'dayjs'
import LocalizedFormat from 'dayjs/plugin/localizedFormat'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { getGameDuration } from './utils'
import { ScoreboardMap } from '@/types/api'
import { MapLayer } from '@/types/mapLayer'

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
    header: 'Map',
    id: 'map',
    accessorKey: 'map',
    minSize: 200,
    size: 200,
    cell: ({ cell }) => {
      const gameMap = cell.getValue() as MapLayer
      const size = 60
      const ratio = 9 / 16
      return (
        <div className="flex flex-row items-center gap-2 w-max">
          <img src={'/maps/icons/' + gameMap.image_name} width={size} height={size * ratio} alt="" />
          <div className="flex flex-col divide-y-2 p-1">
            <div className="pl-1">{gameMap.map.pretty_name}</div>
            <div className="divide-x-2 text-sm text-muted-foreground">
              <span className="px-1">{gameMap.game_mode[0].toUpperCase() + gameMap.game_mode.slice(1)}</span>
              <span className="pl-1">{gameMap.environment}</span>
            </div>
          </div>
        </div>
      )
    },
  },
  {
    header: 'Result',
    id: 'result',
    accessorFn: (row) => `${row.result?.allied ?? '?'} - ${row.result?.axis ?? '?'}`,
  },
  {
    header: 'Start',
    accessorKey: 'start',
    cell: ({ cell }) => dayjs(cell.getValue() as string).format('L LT'),
  },
  {
    header: 'Duration',
    accessorKey: 'duration',
    cell: ({ row }) => getGameDuration(row.original.start, row.original.end),
  },
]
