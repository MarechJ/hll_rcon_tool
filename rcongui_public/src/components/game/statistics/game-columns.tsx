'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Player, PlayerWithStatus } from '@/types/player'
import { IconHeader as Header } from './column-header'
import { Status } from './player-status'
import { isPlayerWithStatus } from './player/utils'
import { Button } from '@/components/ui/button'
import { useTranslation } from 'react-i18next'

const threeDigitsWidth = 40
const fourDigitsWidth = 50

const pointColumns: ColumnDef<Player | PlayerWithStatus>[] = [
  {
    accessorKey: 'kills',
    size: threeDigitsWidth,
    header: function KillsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/infantry.png'}
          desc={t('playersTable.kills')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
  {
    accessorKey: 'deaths',
    size: fourDigitsWidth,
    header: function DeathsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/medic.png'}
          desc={t('playersTable.deaths')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
  {
    accessorKey: 'combat',
    size: fourDigitsWidth,
    header: function CombatHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/score_combat.png'}
          desc={t('playersTable.combat')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
  {
    accessorKey: 'offense',
    size: fourDigitsWidth,
    header: function OffenseHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/score_offensive.png'}
          desc={t('playersTable.offense')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
  {
    accessorKey: 'defense',
    size: fourDigitsWidth,
    header: function DefenseHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/score_defensive.png'}
          desc={t('playersTable.defense')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
  {
    accessorKey: 'support',
    size: fourDigitsWidth,
    header: function SupportHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          src={'/roles/score_support.png'}
          desc={t('playersTable.support')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() === 'asc')
          }}
        />
      )
    },
  },
]

const playerColumn = (handlePlayerClick: (id: string) => void): ColumnDef<Player | PlayerWithStatus> => ({
  accessorKey: 'player',
  header: function NameHeader() {
    const { t } = useTranslation('game')
    return <div>{t('playersTable.player')}</div>
  },
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
  header: function StatusHeader() {
    const { t } = useTranslation('game')
    return <div className="sr-only w-4">{t('playersTable.status')}</div>
  },
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
