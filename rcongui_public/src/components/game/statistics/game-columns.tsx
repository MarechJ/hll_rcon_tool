'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Player, PlayerWithStatus } from '@/types/player'
import { IconHeader as Header } from './column-header'
import { Status } from './player-status'
import { isPlayerWithStatus } from './player/utils'
import { Button } from '@/components/ui/button'

const threeDigitsWidth = 40
const fourDigitsWidth = 50

const pointColumns: ColumnDef<Player | PlayerWithStatus>[] = [
  {
    accessorKey: 'kills',
    size: threeDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/infantry.png'}
        desc={'Kills'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
  {
    accessorKey: 'deaths',
    size: fourDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/medic.png'}
        desc={'Deaths'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
  {
    accessorKey: 'combat',
    size: fourDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/score_combat.png'}
        desc={'Combat'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
  {
    accessorKey: 'offense',
    size: fourDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/score_offensive.png'}
        desc={'Offensive'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
  {
    accessorKey: 'defense',
    size: fourDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/score_defensive.png'}
        desc={'Defensive'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
  {
    accessorKey: 'support',
    size: fourDigitsWidth,
    header: ({ column }) => (
      <Header
        src={'/roles/score_support.png'}
        desc={'Support'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc')
        }}
      />
    ),
  },
]

const playerColumn = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus> => ({
  accessorKey: 'player',
  header: () => <div>Player</div>,
  cell: ({ row }) => {
    const name = String(row.getValue('player'))
    const id = String(row.original.player_id)

    return (
      <div className="flex flex-row items-center gap-1">
        <Button
          variant={'text'}
          className="pl-0"
          onClick={() => {
            handlePlayerClick(id)
          }}
        >
          {name}
        </Button>
      </div>
    )
  },
})

const statusColumn: ColumnDef<Player | PlayerWithStatus> = {
  accessorKey: 'is_online',
  meta: {
    filterVariant: 'select',
  },
  header: () => <div className="sr-only w-4">Status</div>,
  size: 20,
  filterFn: (row, columnId, filterValue) => {
    if (!filterValue || filterValue === 'all') {
      return true
    }
    const cellValue = row.getValue(columnId) ? 'online' : 'offline'
    return cellValue === filterValue
  },
  cell: ({ row }) => {
    const player = row.original
    return isPlayerWithStatus(player) ? <Status player={player} className="block" /> : null
  },
}

export const getLiveGameColumns = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus>[] => [
  statusColumn,
  playerColumn(handlePlayerClick),
  ...pointColumns,
]

export const getCompletedGameColumns = (
  handlePlayerClick: (id: string) => void,
): ColumnDef<Player | PlayerWithStatus>[] => [playerColumn(handlePlayerClick), ...pointColumns]
