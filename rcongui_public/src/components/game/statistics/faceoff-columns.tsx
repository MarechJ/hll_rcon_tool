import clsx from 'clsx'
import { Header } from './column-header'
import { Faceoff } from '@/types/player'
import { ColumnDef } from '@tanstack/react-table'
import { useTranslation } from 'react-i18next'
import { useGameStatsContext } from "@/components/game/statistics/game-stats-container";
import { Button } from "@/components/ui/button";

const nColSize = 40

export const columns: ColumnDef<Faceoff>[] = [
  {
    accessorKey: 'name',
    header: function NameHeader() {
      const { t } = useTranslation('game')
      return t('playersTable.player')
    },
    cell: (info) => {
      const { focusPlayerBy, players } = useGameStatsContext();
      const faceoff = info.row.original;
      const player = players.find(({ id, name }) =>
        ("id" in faceoff ? id === faceoff.id : name === faceoff.name)
      );
      const displayName = player?.name ?? ("id" in faceoff ? faceoff.id : faceoff.name);
      return <Button
        variant="text"
        className="pl-0 h-0"
        onClick={() => {
          if ("id" in faceoff) {
            focusPlayerBy({ id: faceoff.id })
          } else {
            focusPlayerBy({ name: faceoff.name })
          }
        }}
      >
        {displayName}
      </Button>
    },
  },
  {
    accessorKey: 'kills',
    header: function KillsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          header="K"
          desc={t('playersTable.kills')}
          onClick={() => column.toggleSorting(column.getIsSorted() !== 'desc')}
        />
      )
    },
    cell: (info) => <div className="text-center px-1">{String(info.getValue())}</div>,
    size: nColSize,
  },
  {
    accessorKey: 'deaths',
    header: function DeathsHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          header="D"
          desc={t('playersTable.deaths')}
          onClick={() => column.toggleSorting(column.getIsSorted() !== 'desc')}
        />
      )
    },
    cell: (info) => <div className="text-center px-1">{String(info.getValue())}</div>,
    size: nColSize,
  },
  {
    accessorKey: 'diff',
    header: function DiffHeader({ column }) {
      const { t } = useTranslation('game')
      return (
        <Header
          header="+/-"
          desc={t('playersTable.diff')}
          onClick={() => column.toggleSorting(column.getIsSorted() !== 'desc')}
        />
      )
    },
    cell: (info) => {
      const diff = Number(info.getValue())
      const textColor = diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : ''
      return <div className={clsx(textColor, 'text-center px-1')}>{diff}</div>
    },
    size: nColSize,
  },
]
