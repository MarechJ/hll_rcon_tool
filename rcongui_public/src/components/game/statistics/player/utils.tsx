import { Player, PlayerWithStatus } from '@/types/player'
import {ScaleIcon, ZapIcon, SkullIcon, HeartOffIcon} from 'lucide-react'

export const points = [
  { key: 'kills', label: 'K', icon: '/roles/infantry.png', transKey: 'playersTable.kills' },
  { key: 'deaths', label: 'D', icon: '/roles/medic.png', transKey: 'playersTable.deaths' },
  { key: 'combat', label: 'C', icon: '/roles/score_combat.png', transKey: 'playersTable.combat' },
  { key: 'offense', label: 'O', icon: '/roles/score_offensive.png', transKey: 'playersTable.offense' },
  { key: 'defense', label: 'D', icon: '/roles/score_defensive.png', transKey: 'playersTable.defense' },
  { key: 'support', label: 'S', icon: '/roles/score_support.png', transKey: 'playersTable.support' },
] as const

export const scores = [
  { key: 'kill_death_ratio', label: 'K/D', icon: ScaleIcon, transKey: 'score.k/d' },
  { key: 'kills_streak', label: 'Killstreak', icon: ZapIcon, transKey: 'score.killstreak' },
  { key: 'deaths_without_kill_streak', label: 'Deathstreak', icon: SkullIcon, transKey: 'score.deathstreak' },
  { key: 'teamkills', label: 'Teamkills', icon: HeartOffIcon, transKey: 'score.teamkills' },
] as const

export function isSteamPlayer(player: Player) {
  const { player_id: id } = player
  return id.length === 17 && !Number.isNaN(Number(id))
}

export function getSteamProfileUrl(id: string) {
  return `https://steamcommunity.com/profiles/${id}`
}

export function getXboxProfileUrl(playerName: string) {
  return `https://xboxgamertag.com/search/${playerName}`
}

export function isPlayerWithStatus(player: Player | PlayerWithStatus): player is PlayerWithStatus {
  return (player as PlayerWithStatus).is_online !== undefined
}
