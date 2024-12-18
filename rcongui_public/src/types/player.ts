import { Weapon, WeaponCategory } from './weapon'

type Team = {
  name: string
  side: 'allies' | 'axis'
  score: number
  img: string
  country: string
}

type Teams = {
  home: Team
  away: Team
}

type League = {
  name: string
  img: string
}

type LinkBase = {
  url: string
  title: string
  author: string
  date: string
  description: string
}

type TwitchLink = LinkBase & {
  type: 'twitch'
}

type YoutubeLink = LinkBase & {
  type: 'youtube'
}

type Link = TwitchLink | YoutubeLink

interface MatchBase {
  id: number
  date: string
  time: string
  league: League
  format: string
  aside: string
  teams: Teams
  links?: Link[]
  map: string
}

interface CompletedMatch extends MatchBase {
  length: number
  completed: true
  points?: string[]
}

interface ScheduledMatch extends MatchBase {
  completed: false
}

export type Match = CompletedMatch | ScheduledMatch

export interface ServerFinalStats {
  result: Result
  command: string
  arguments?: null
  failed: boolean
  error?: null
  forwards_results?: null
}

export interface Result {
  id: number
  creation_time: string
  start: string
  end: string
  server_number: number
  map_name: string
  player_stats?: Player[] | null
}

// Base player interface with common properties
export interface PlayerBase {
  id: number
  player_id: string
  steam_id_64: string
  player: string
  steaminfo?: Steaminfo
  map_id: number
  kills: number
  kills_streak: number
  deaths: number
  deaths_without_kill_streak: number
  teamkills: number
  teamkills_streak: number
  deaths_by_tk: number
  deaths_by_tk_streak: number
  nb_vote_started: number
  nb_voted_yes: number
  nb_voted_no: number
  time_seconds: number
  kills_per_minute: number
  deaths_per_minute: number
  kill_death_ratio: number
  longest_life_secs: number
  shortest_life_secs: number
  combat: number
  offense: number
  defense: number
  support: number
  most_killed: Record<string, number>
  death_by: Record<string, number>
  weapons: Record<Weapon, number>
  death_by_weapons: Record<Weapon, number> | null
  team?: TeamEnum
}

export enum TeamEnum {
  AXIS = 'AXIS',
  ALLIES = 'ALLIES',
  MIXED = 'MIXED',
  UNKNOWN = 'UNKNOWN',
}

// Live player interface with online status
export interface LivePlayer extends PlayerBase {
  is_online: boolean
}

export type Player = PlayerBase
export type PlayerWithStatus = LivePlayer

export interface Steaminfo {
  id: number
  created: string
  updated: string | null
  profile: Profile | null
  country: string | null
  bans: {
    active: boolean
    reason: string
    time_left: number
  } | null
  has_bans: boolean
}

export interface Profile {
  avatar: string
  gameid: string
  steamid: string
  realname: string
  loccityid: number
  avatarfull: string
  avatarhash: string
  lastlogoff: number
  profileurl: string
  personaname: string
  timecreated: number
  avatarmedium: string
  gameserverip: string
  locstatecode: string
  personastate: number
  profilestate: number
  gameextrainfo: string
  primaryclanid: string
  loccountrycode: string
  gameserversteamid: string
  personastateflags: number
  communityvisibilitystate: number
}

type TeamsStats = {
  kills: number
  deaths: number
  weaponCategories: Partial<Record<WeaponCategory, number>>
  killsCategory: {
    infantry: number
    armor: number
    artillery: number
    other: number
  }
  points: {
    combat: number
    support: number
    offensive: number
    defensive: number
  }
  players: Player[]
}

export type MatchStats = {
  allies: TeamsStats
  axis: TeamsStats
  weapons: Partial<Record<Weapon, number>>
}

export type Faceoff = {
  name: string
  kills: number
  deaths: number
  diff: number
}
