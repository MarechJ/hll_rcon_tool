import { Player, PlayerWithStatus } from '@/types/player'
import { ScaleIcon, ZapIcon, SkullIcon, HeartCrackIcon } from 'lucide-react'

export const points = [
  { key: 'kills', label: 'K', icon: '/roles/infantry.png' },
  { key: 'deaths', label: 'D', icon: '/roles/medic.png' },
  { key: 'combat', label: 'C', icon: '/roles/score_combat.png' },
  { key: 'offense', label: 'O', icon: '/roles/score_offensive.png' },
  { key: 'defense', label: 'D', icon: '/roles/score_defensive.png' },
  { key: 'support', label: 'S', icon: '/roles/score_support.png' },
] as const

export const scores = [
  { key: 'kill_death_ratio', label: 'K/D', icon: ScaleIcon },
  { key: 'kills_streak', label: 'Killstreak', icon: ZapIcon },
  { key: 'deaths_without_kill_streak', label: 'Deathstreak', icon: SkullIcon },
  { key: 'teamkills', label: 'Teamkills', icon: HeartCrackIcon },
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
