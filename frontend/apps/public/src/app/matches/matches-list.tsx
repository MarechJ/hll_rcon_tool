'use client';

import dayjs from 'dayjs';
import { useGamesQuery } from '../../utils/queries/scoreboard-maps';
import { ScoreboardMap } from '../../utils/queries/types';
import { columns } from './match-columns';
import { DataTable as MatchTable } from './match-table';
import MatchPagination from './match-pagination';

export function validMatch(match: ScoreboardMap) {
  const start = dayjs(match.start);
  const end = dayjs(match.end);
  const diffMinutes = end.diff(start, 'minutes');
  const isDraw = (match.result?.allied ?? 0) + (match.result?.axis ?? 0) === 4;

  return diffMinutes < 100 && diffMinutes > 9 && !isDraw;
}

export default function MatchesList({
  page,
  pageSize,
}: {
  page: number;
  pageSize: number;
}) {
  const [matches] = useGamesQuery(page, pageSize);

  const totalMatches = matches.total;
  const maxPages = Math.ceil(totalMatches / pageSize);

  const filteredMatches = matches.maps.filter(validMatch);

  return (
    <>
      <MatchPagination
        page={page}
        maxPages={maxPages}
        className="justify-end"
      />
      <MatchTable data={filteredMatches} columns={columns} />
      <MatchPagination page={page} maxPages={maxPages} />
    </>
  );
}
