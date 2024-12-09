import clsx from 'clsx'
import { Header } from './column-header'
import { Faceoff } from '@/types/player'
import { ColumnDef } from '@tanstack/react-table'

const nColSize = 40

export const columns: ColumnDef<Faceoff>[] = [
  {
    accessorKey: 'name',
    header: 'Player',
  },
  {
    accessorKey: 'kills',
    header: ({ column }) => (
      <Header header="K" desc="Kills" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')} />
    ),
    cell: (info) => <div className="text-center px-1">{String(info.getValue())}</div>,
    size: nColSize,
  },
  {
    accessorKey: 'deaths',
    header: ({ column }) => (
      <Header header="D" desc="Deaths" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')} />
    ),
    cell: (info) => <div className="text-center px-1">{String(info.getValue())}</div>,
    size: nColSize,
  },
  {
    accessorKey: 'diff',
    header: ({ column }) => (
      <Header header="+/-" desc="Difference" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')} />
    ),
    cell: (info) => {
      const diff = Number(info.getValue())
      const textColor = diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : ''
      return <div className={clsx(textColor, 'text-center px-1')}>{diff}</div>
    },
    size: nColSize,
  },
]
