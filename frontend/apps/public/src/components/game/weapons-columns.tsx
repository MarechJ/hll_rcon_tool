'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Header } from './column-header';

const nColSize = 40;

type WeaponKillCount = {
  name: string;
  count: number;
};

export const killByColumns: ColumnDef<WeaponKillCount>[] = [
  {
    accessorKey: 'name',
    header: 'Weapon',
  },
  {
    accessorKey: 'count',
    header: ({ column }) => (
      <Header
        header={'K'}
        desc={'Kills'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
    cell: ({ cell }) => (
      <div className="text-center px-1">{String(cell.getValue())}</div>
    ),
    size: nColSize,
  },
];

export const deathByColumns: ColumnDef<WeaponKillCount>[] = [
  {
    accessorKey: 'name',
    header: 'Weapon',
  },
  {
    accessorKey: 'count',
    header: ({ column }) => (
      <Header
        header={'D'}
        desc={'Deaths'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
    cell: ({ cell }) => (
      <div className="text-center px-1">{String(cell.getValue())}</div>
    ),
    size: nColSize,
  },
];
