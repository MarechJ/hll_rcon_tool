'use client';

import { ColumnDef } from '@tanstack/react-table';
import { MatchMap, ScoreboardMap } from '../../utils/queries/types';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@shared/components/ui/button';
import { getGameDuration } from './utils';

dayjs.extend(LocalizedFormat);

export const columns: ColumnDef<ScoreboardMap>[] = [
    {
        accessorKey: 'id',
        header: "ID",
        cell: ({ cell }) => {
          const matchId =  cell.getValue() as string;
          return (
            <Button asChild variant={'link'}>
              <Link href={`/matches/${matchId}`} className='w-10'>{matchId}</Link>
            </Button>
          )
        }
      },
  {
    header: 'Map',
    id: 'map',
    accessorKey: 'map',
    minSize: 200,
    size: 200,
    cell: ({ cell }) => {
      const matchMap = cell.getValue() as MatchMap;
      const size = 60;
      const ratio = 9 / 16;
      return (
        <div className="flex flex-row items-center gap-2 w-max">
            <Image
              src={'/maps/' + matchMap.image_name}
              width={size}
              height={size * ratio}
              alt=""
            />
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
    header: 'Start',
    accessorKey: 'start',
    cell: ({ cell }) => dayjs(cell.getValue() as string).format('L LT'),
  },
  {
    header: 'Duration',
    accessorKey: 'duration',
    cell: ({ row }) => getGameDuration(row.original.start, row.original.end),
  }
];
