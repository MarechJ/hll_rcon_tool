import {Faceoff, Player, PlayerTeamAssociation,TeamEnum } from '@/types/player'
import colors from 'tailwindcss/colors'

export function mergeKillsDeaths(player: Player) {
  const { most_killed: killsByPlayer, death_by: deathsByPlayer } = player
  const allPlayerNames = new Set(Object.keys(killsByPlayer).concat(Object.keys(deathsByPlayer)))
  const merged: Faceoff[] = []
  allPlayerNames.forEach((name) => {
    merged.push({
      name: name,
      kills: killsByPlayer[name] ?? 0,
      deaths: deathsByPlayer[name] ?? 0,
      diff: (killsByPlayer[name] ?? 0) - (deathsByPlayer[name] ?? 0),
    })
  })
  merged.sort((a, b) => b.kills - a.kills)
  return merged
}

const teamColors: Record<TeamEnum, string> = {
  [TeamEnum.AXIS]: colors.red[600],
  [TeamEnum.ALLIES]: colors.blue[600],
  [TeamEnum.MIXED]: colors.yellow[400],
  [TeamEnum.UNKNOWN]: colors.gray[500],
};

export function getColorForTeam(team: TeamEnum | undefined): string {
  if (team === undefined) {
    return colors.purple[600];
  }
  return teamColors[team];
}

export function getTeamFromAssociation(team: PlayerTeamAssociation | undefined): TeamEnum {
  if (team === undefined) {
    return TeamEnum.UNKNOWN;
  }
  return team.confidence === 'strong' ? team.side : TeamEnum.MIXED;
}
