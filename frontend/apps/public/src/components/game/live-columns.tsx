'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Button } from '@shared/components/ui/button';
import { Player } from './types';
import { useLivePageStore } from '../../utils/stores/useLivePageStore';
import { IconHeader as Header } from './column-header';

export const columns: ColumnDef<Player>[] = [
  {
    accessorKey: 'player',
    header: () => <div>Player</div>,
    cell: ({ row, column }) => {
      const setPlayer = useLivePageStore((state) => state.setPlayer);
      const name = String(row.getValue('player'));
      const id = String(row.getValue('player_id'));

      return (
        <Button
          variant={'link'}
          className="pl-0"
          onClick={() => {
            setPlayer(id);
          }}
        >
          {name}
        </Button>
      );
    },
  },
  {
    accessorKey: 'kills',
    header: ({ column }) => (
      <Header
        src={'/roles/infantry.png'}
        desc={'Kills'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'deaths',
    header: ({ column }) => (
      <Header
        src={'/roles/medic.png'}
        desc={'Deaths'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'combat',
    header: ({ column }) => (
      <Header
        src={'/roles/score_combat.png'}
        desc={'Combat'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'offense',
    header: ({ column }) => (
      <Header
        src={'/roles/score_offensive.png'}
        desc={'Offensive'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'defense',
    header: ({ column }) => (
      <Header
        src={'/roles/score_defensive.png'}
        desc={'Defensive'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'support',
    header: ({ column }) => (
      <Header
        src={'/roles/score_support.png'}
        desc={'Support'}
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
  {
    accessorKey: 'player_id',
  },
];
