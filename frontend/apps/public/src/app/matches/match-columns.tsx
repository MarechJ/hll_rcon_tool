'use client';

import { ColumnDef } from '@tanstack/react-table';
import { Header } from './../../components/game/column-header';
import { MatchMap, ScoreboardMap } from '../../utils/queries/types';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@shared/components/ui/button';

dayjs.extend(LocalizedFormat);

export const columns: ColumnDef<ScoreboardMap>[] = [
    {
        accessorKey: 'id',
        header: "ID",
        cell: ({ cell }) => {
          const matchId =  cell.getValue() as string;
          return (
            <Button asChild variant={'link'}>
              <Link href={`/matches/${matchId}`}>{matchId}</Link>
            </Button>
          )
        }
      },
  {
    header: 'Map',
    id: 'map',
    accessorKey: 'map',
    cell: ({ cell }) => {
      const matchMap = cell.getValue() as MatchMap;
      const size = 60;
      const ratio = 9 / 16;
      return (
        <div className="flex flex-row items-center gap-2">
          <div>
            <Image
              src={'/maps/' + matchMap.image_name}
              width={size}
              height={size * ratio}
              alt=""
            />
          </div>
          <div className="flex flex-col divide-y-2 p-1">
            <div className="pl-1">{matchMap.map.pretty_name}</div>
            <div className="divide-x-2 text-sm text-muted-foreground">
              <span className="px-1">
                {matchMap.game_mode[0].toUpperCase() +
                  matchMap.game_mode.slice(1)}
              </span>
              <span className="pl-1">{matchMap.environment}</span>
            </div>
          </div>
        </div>
      );
    },
  },
  {
    header: 'Result',
    id: 'result',
    accessorFn: (row) =>
      `${row.result?.allied ?? '?'} - ${row.result?.axis ?? '?'}`,
  },
  {
    accessorKey: 'start',
    cell: ({ cell }) => dayjs(cell.getValue() as string).format('L LT'),
    header: ({ column }) => (
      <Header
        header="Start"
        onClick={() => {
          column.toggleSorting(column.getIsSorted() === 'asc');
        }}
      />
    ),
  },
];
