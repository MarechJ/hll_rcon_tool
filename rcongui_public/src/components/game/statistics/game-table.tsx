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
  VisibilityState,
} from '@tanstack/react-table'

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import React, { useEffect, useMemo, useState } from 'react'

import {
  PlainSelectTrigger,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import { Player, TeamEnum } from '@/types/player'
import { useTranslation } from 'react-i18next'
import { List } from 'lucide-react'
import { getTeamFromAssociation } from '@/components/game/statistics/utils'
import { TeamIndicator } from '@/components/game/statistics/team-indicator'
import SelectBox from '@/components/ui/select-box'
import { Checkbox } from '@/components/ui/checkbox'
import { useStorageState } from '@/hooks/use-storage-state'
import { DownloadButton } from "@/components/game/statistics/download-button";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  tableId: string
}

export function DataTable<TData extends Player, TValue>({ columns, data, tableId }: DataTableProps<TData, TValue>) {
  const [playerFilter, setPlayerFilter] = useState<string[]>([])

  useEffect(() => {
    table.getColumn('player')?.setFilterValue(playerFilter)
  }, [playerFilter])

  // Adding selected players as option to keep the selected options visible when switching between different games
  // Otherwise selected option would be not visible e.g. a selected player is in game1, but not in game2
  const playerFilterOptions = data
    .map((player) => ({ value: player.player, label: player.player }))
    .concat(
      playerFilter
        .filter((name) => !data.some((player) => player.player === name))
        .map((name) => ({ value: name, label: name })),
    )

  const [sorting, setSorting] = React.useState<SortingState>([
    {
      id: 'kills',
      desc: true,
    },
  ])

  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])

  const [columnVisibility, setColumnVisibility] = useStorageState<VisibilityState>('column-visibility', {
    ['combat']: false,
    ['defense']: false,
    ['offense']: false,
    ['support']: false,
  })

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
      columnVisibility,
    },
    onColumnVisibilityChange: setColumnVisibility,
  })

  const { t } = useTranslation('game')

  const hasIsOnline = table.getAllColumns().find((c) => c.id === 'is_online')
  const hasTeam = table.getAllColumns().find((c) => c.id === 'team')
  const teamOptions = ['axis', 'allies', 'mixed', 'unknown'] as const
  const teamCounts = useMemo(
    () => teamOptions.map((team) => data.filter((player) => getTeamFromAssociation(player.team) === team).length),
    [data],
  )

  return (
    <div className="border w-full divide-y">
      <div className="flex flex-row justify-between items-start p-2 gap-3">
        <div className="flex flex-row items-start gap-3 flex-1">
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
          {hasTeam && (
            <Select onValueChange={(value) => table.getColumn('team')?.setFilterValue(value)}>
              <SelectTrigger className="max-w-40">
                <SelectValue placeholder={t('playersTable.team')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  <div className={'pl-5'}>
                    {t('onlineStatusFilter.all')} ({data.length})
                  </div>
                </SelectItem>
                {teamOptions.map((option, index) => (
                  <SelectItem key={option} value={option}>
                    <div className="flex">
                      <TeamIndicator team={option as TeamEnum} className="block m-auto" />
                      <div className="pl-3">
                        {t(option)} ({teamCounts[index]})
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {table.getColumn('player') && (
            <SelectBox
              options={playerFilterOptions}
              multiple
              value={playerFilter}
              onChange={(values) => Array.isArray(values) && setPlayerFilter(values)}
              placeholder={`${t('searchPlayer')}...`}
            />
          )}
        </div>
        <div className={'inline-flex gap-3'}>
          <DownloadButton data={data} tableId={tableId}/>
          {!!table.getAllColumns().find((col) => col.getCanHide()) && (
            <Select>
              <PlainSelectTrigger className={'rounded-md border border-input bg-background px-3 py-2 hover:bg-accent'}>
                <List size={20} />
              </PlainSelectTrigger>
              <SelectContent className={'py-2'}>
                {table
                  .getAllColumns()
                  .filter((col) => col.getCanHide())
                  .map((column) => (
                    <div
                      key={column.id}
                      onClick={column.getToggleVisibilityHandler()}
                      className="px-2 flex items-center cursor-pointer select-none hover:bg-accent"
                    >
                      <Checkbox checked={column.getIsVisible()} disabled={!column.getCanHide()} />
                      <span className="pl-3">{column.columnDef.meta?.label}</span>
                    </div>
                  ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </div>
      <Table id={tableId} style={{ height: '100%' }}>
        <TableHeader className="h-12">
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              <TableHead className="w-4 text-center pr-0">{'#'}</TableHead>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id} style={{ width: header.column.getSize() }} className="px-1.5">
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
                <TableCell className="w-4 text-center pr-0">{index + 1}</TableCell>
                {row.getVisibleCells().map((cell) => (
                  <TableCell
                    key={cell.id}
                    className="py-0"
                    style={{ width: cell.column.getSize(), textAlign: 'right' }}
                  >
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
