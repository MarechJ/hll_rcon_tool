'use client'

import dayjs from 'dayjs'
import { columns } from './columns'
import { DataTable as MatchTable } from './table'
import MatchPagination from './pagination'
import { ScoreboardMap } from '@/types/api'
import { useGames } from '@/lib/queries/scoreboard-maps'
import { Suspense } from 'react'

export function validMatch(match: ScoreboardMap) {
  const start = dayjs(match.start)
  const end = dayjs(match.end)
  const diffMinutes = end.diff(start, 'minutes')
  const isDraw = (match.result?.allied ?? 0) + (match.result?.axis ?? 0) === 4

  return diffMinutes < 100 && diffMinutes > 9 && !isDraw
}

export default function MatchesList({ page, pageSize }: { page: number; pageSize: number }) {
  const [games, { isLoading }] = useGames(page, pageSize)

  if (isLoading || !games) return <div>Loading...</div>

  const totalGames = games.total
  const maxPages = Math.ceil(totalGames / pageSize)

  const filteredGames = games.maps.filter(validMatch)

  return (
    <>
      <Suspense fallback={<div>Loading...</div>}>
        <MatchPagination page={page} maxPages={maxPages} className="justify-end" />
        <MatchTable data={filteredGames} columns={columns} />
        <MatchPagination page={page} maxPages={maxPages} />
      </Suspense>
    </>
  )
}
