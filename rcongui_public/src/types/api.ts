import { MapLayer } from './mapLayer'
import { Player } from './player'

type UNIX_Timestamp = number
type ISO_8601_Timestamp = string
type TIME_SECONDS = number

export type ScoreboardMap = {
  id: number
  creation_time: string
  start: ISO_8601_Timestamp
  end: ISO_8601_Timestamp
  map: MapLayer
  result: {
    allied: number
    axis: number
  } | null
  player_stats: []
  server_number: number
}

// TODO
// Fix after https://github.com/MarechJ/hll_rcon_tool/issues/657 issue has been resolved
export type ScoreboardMapStats = Omit<ScoreboardMap, 'player_stats'> & {
  player_stats: Player[]
  // map_name: string;
}

export type CRCON_Response<T> = {
  arguments: string | null
  command: string
  error: string | null
  failed: boolean
  forward_results: boolean | null
  result: T
  version: string
}

export type Broken_CRCON_Response<T> = Omit<CRCON_Response<T>, 'error'> & {
  error: null[] | string[]
}

export type PublicInfo = {
  max_player_count: number
  player_count: number
  player_count_by_team: {
    allied: number
    axis: number
  }
  score: {
    allied: number
    axis: number
  }
  time_remaining: TIME_SECONDS
  name: {
    name: string
    short_name: string
    public_stats_port: number
    public_stats_port_https: number
  }
  current_map: {
    id: string
    map: MapLayer
    start: UNIX_Timestamp
  }
  next_map: {
    id: string
    map: MapLayer
    start: UNIX_Timestamp
  }
  vote_status: {
    map: MapLayer
    // TODO fix voters type
    voters: string[]
  }[]
}

export type LiveGameStats = {
  refresh_interval_sec: number
  snapshot_timestamp: UNIX_Timestamp
  stats: Player[]
}

export type ScoreboardMaps = {
  page: number
  page_size: number
  total: number
  maps: ScoreboardMap[]
}

export type MapScoreboard = ScoreboardMapStats
