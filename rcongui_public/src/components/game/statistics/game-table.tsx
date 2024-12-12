'use client'

import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import React from 'react'

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { Player } from '@/types/player'
import DebouncedInput from '@/components/debounced-input'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import useGameDownload from '@/hooks/use-game-download'

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  tableId: string
}

export function DataTable<TData extends Player, TValue>({ columns, data, tableId }: DataTableProps<TData, TValue>) {
  const { download } = useGameDownload()

  const [sorting, setSorting] = React.useState<SortingState>([
    {
      id: 'kills',
      desc: true,
    },
  ])

  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnFiltersChange: setColumnFilters,
    filterFns: {},
    state: {
      sorting,
      columnFilters,
    },
  })

  const { t } = useTranslation('game')

  const hasIsOnline = table.getAllColumns().find((c) => c.id === 'is_online')
  return (
    <div className="border w-full divide-y">
      <div className="flex flex-row justify-between items-center p-2">
        <div className="flex flex-row items-center gap-1">
          {hasIsOnline && (
            <Select onValueChange={(value) => table.getColumn('is_online')?.setFilterValue(value)}>
              <SelectTrigger className="w-24">
                <SelectValue placeholder={t('playersTable.status')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('onlineStatusFilter.all')}</SelectItem>
                <SelectItem value="online">{t('onlineStatusFilter.online')}</SelectItem>
                <SelectItem value="offline">{t('onlineStatusFilter.offline')}</SelectItem>
              </SelectContent>
            </Select>
          )}
          {table.getColumn('player') && (
            <DebouncedInput
              className="w-60 border shadow rounded"
              onChange={(value) => {
                table.getColumn('player')?.setFilterValue(value)
              }}
              placeholder={`${t('searchPlayer')}...`}
              type="text"
              value={(table.getColumn('player')?.getFilterValue() ?? '') as string}
            />
          )}
        </div>
        <div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  aria-label={t('downloadTable')}
                  size={'icon'}
                  onClick={() => download(data, `game-table-${tableId}`)}
                >
                  <Download size={20} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <span>{t('downloadTable')}</span>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
      <Table id={tableId}>
        <TableHeader className="h-12">
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              <TableHead className="w-4">{'#'}</TableHead>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id} style={{ width: header.column.getSize() }}>
                    {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row, index) => (
              <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'} className="text-sm h-10">
                <TableCell className="w-4">{index + 1}</TableCell>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="py-0" style={{ width: cell.column.getSize() }}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              {/* +1 for the index column */}
              <TableCell colSpan={columns.length + 1} className="h-24 text-center">
                {t('noPlayersFound')}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
