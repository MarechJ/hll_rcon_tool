'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Button } from '@shared/components/ui/button';
import { Player, PlayerWithStatus } from './types';
import { IconHeader as Header } from './column-header';
import { isPlayerWithStatus, Status } from './player-status';

const threeDigitsWidth = 60
const fourDigitsWidth = 75

export const columns = (
  handlePlayerClick: (id: string) => void
): ColumnDef<Player | PlayerWithStatus>[] => [
  {
    accessorKey: 'player',
    header: () => <div>Player</div>,
    cell: ({ row }) => {
      const name = String(row.getValue('player'));
      const id = String(row.getValue('player_id'));
      const player = row.original;

      return (
        <div className="flex flex-row items-center gap-1">
          {isPlayerWithStatus(player) && <Status player={player} />}
          <Button
            variant={'link'}
            className="pl-0"
            onClick={() => {
              handlePlayerClick(id);
            }}
          >
            {name}
          </Button>
        </div>
      );
    },
  },
  {
    accessorKey: 'kills',
    size: threeDigitsWidth,
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
    size: fourDigitsWidth,
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
    size: fourDigitsWidth,
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
    size: fourDigitsWidth,
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
    size: fourDigitsWidth,
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
    size: fourDigitsWidth,
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
