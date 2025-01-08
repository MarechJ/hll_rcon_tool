'use client'

import dayjs from 'dayjs'
import { columns } from './columns'
import { DataTable as MatchTable } from './table'
import MatchPagination from './pagination'
import { ScoreboardMap, ScoreboardMaps } from '@/types/api'
import {GameMode} from "@/types/mapLayer";

export function validGame(game: ScoreboardMap) {
  const modeToTime: Record<GameMode, number> = {
    ['warfare']: 90,
    ['offensive']: 150,
    ['skirmish']: 30,
    ['control']: 30,
  }

  const start = dayjs(game.start)
  const end = dayjs(game.end)
  const diffMinutes = end.diff(start, 'minutes')
  const isDraw = (game.result?.allied ?? 0) + (game.result?.axis ?? 0) === 4

  return diffMinutes < (modeToTime[game.map.game_mode] ?? 90) + 10 && diffMinutes > 9 && !isDraw
}

export default function GamesList({
  games,
  page,
  pageSize,
}: {
  games: ScoreboardMaps
  page: number
  pageSize: number
}) {
  const totalGames = games.total
  const maxPages = Math.ceil(totalGames / pageSize)

  const filteredGames = games.maps.filter(validGame)

  return (
    <>
      <MatchPagination page={page} maxPages={maxPages} className="justify-end" />
      <MatchTable data={filteredGames} columns={columns} />
      <MatchPagination page={page} maxPages={maxPages} />
    </>
  )
}
