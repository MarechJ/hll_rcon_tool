'use client'

import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table'

import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table'
import React, {Fragment, useState} from 'react'

import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select'

import {Player} from '@/types/player'
import {useTranslation} from 'react-i18next'
import {Button} from '@/components/ui/button'
import {Download} from 'lucide-react'
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip'
import useGameDownload from '@/hooks/use-game-download'
import TagList from "@/components/tag-list";
import {Input} from "@/components/ui/input";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  tableId: string
}

export function DataTable<TData extends Player, TValue>({columns, data, tableId}: DataTableProps<TData, TValue>) {
  const {download} = useGameDownload()
  const [filter, setFilter] = useState<string | number>('');

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

  const {t} = useTranslation('game')

  const hasIsOnline = table.getAllColumns().find((c) => c.id === 'is_online')
  return (
    <div className="border w-full divide-y">
      <div className="flex flex-row justify-between items-center p-2">
        <div className="flex flex-row items-center gap-3">
          {hasIsOnline && (
            <Select onValueChange={(value) => table.getColumn('is_online')?.setFilterValue(value)}>
              <SelectTrigger className="w-24">
                <SelectValue placeholder={t('playersTable.status')}/>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('onlineStatusFilter.all')}</SelectItem>
                <SelectItem value="online">{t('onlineStatusFilter.online')}</SelectItem>
                <SelectItem value="offline">{t('onlineStatusFilter.offline')}</SelectItem>
              </SelectContent>
            </Select>
          )}
          {table.getColumn('player') && (
            <Fragment>
              <Input
                className="grow max-w-60 border shadow rounded"
                onChange={({target}) => {
                  setFilter(target.value);
                }}
                onKeyUp={({key}) => {
                  if (key !== 'Enter' || filter === '' || filter === undefined) {
                    return;
                  }
                  const orig = table.getColumn('player')?.getFilterValue() as [] ?? []
                  table.getColumn('player')?.setFilterValue([...orig, filter]);
                  setFilter('');
                }}
                placeholder={`${t('searchPlayer')}...`}
                value={filter}
                type="text"
              />
              <TagList
                value={((table.getColumn('player')?.getFilterValue() as []) ?? [])}
                onChange={(v) => table.getColumn('player')?.setFilterValue(v)}/>
            </Fragment>
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
                  <Download size={20}/>
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
                  <TableHead key={header.id} style={{width: header.column.getSize()}}>
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
                  <TableCell key={cell.id} className="py-0" style={{width: cell.column.getSize()}}>
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
