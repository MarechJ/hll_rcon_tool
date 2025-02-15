'use client'

import { ColumnDef } from '@tanstack/react-table'
import { Header } from './column-header'
import { useTranslation } from 'react-i18next'

const nColSize = 40

type WeaponKillCount = {
  name: string
  count: number
}

export const killByColumns: ColumnDef<WeaponKillCount>[] = [
  {
    accessorKey: 'name',
    header: function NameHeader() {
      const { t } = useTranslation('game')
      return t('playerStats.weapon')
    },
  },
  {
    accessorKey: 'count',
    header: function KillsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          header={'K'}
          desc={t('playersTable.kills')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() !== 'desc')
          }}
        />
      )
    },
    cell: ({ cell }) => <div className="text-center px-1">{String(cell.getValue())}</div>,
    size: nColSize,
  },
]

export const deathByColumns: ColumnDef<WeaponKillCount>[] = [
  {
    accessorKey: 'name',
    header: function NameHeader() {
      const { t } = useTranslation('game')
      return t('playerStats.weapon')
    },
  },
  {
    accessorKey: 'count',
    header: function DeathsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          header={'D'}
          desc={t('playersTable.deaths')}
          onClick={() => {
            column.toggleSorting(column.getIsSorted() !== 'desc')
          }}
        />
      )
    },
    cell: ({ cell }) => <div className="text-center px-1">{String(cell.getValue())}</div>,
    size: nColSize,
  },
]
