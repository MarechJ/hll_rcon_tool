/**
 * Flatten the team view into a list of players.
 * @param {TeamViewResult} game The result of `get_team_view` API call.
 * @returns A list of all players in the game
 */
export const extractPlayers = (game) => {
  const players = []
  const teams = ['axis', 'allies', 'none', 'null']

  for (const teamKey of teams) {
    if (!(teamKey in game)) continue

    const team = game[teamKey]
    const squads = team['squads']

    for (const squadKey in squads) {
      const squadPlayers = squads[squadKey].players
      players.push(...squadPlayers)
    }

    if ('commander' in team && team.commander) {
      players.push(team.commander)
    }
  }

  return players
}

export const extractTeamState = (team) => {
  const levels = []
  const out = {}
  out['armycommander'] = 'commander' in team && team.commander ? 1 : 0
  out['armor'] = 0
  out['infantry'] = 0
  out['recon'] = 0
  out['avg_level'] = 0
  out['med_level'] = 0

  const squads = team['squads']

  for (const squadKey in squads) {
    const squadPlayers = squads[squadKey].players
    for (const player of squadPlayers) {
      switch (player.role) {
        case 'sniper':
        case 'spotter':
          out['recon']++
          break
        case 'tankcommander':
        case 'crewman':
          out['armor']++
          break
        default:
          out['infantry']++
          break
      }
      levels.push(player.level)
    }
  }

  if (team.count) {
    // get team average level
    out['avg_level'] = Math.round(levels.reduce((sum, level) => sum + level, 0) / team.count)

    // get team median level
    levels.sort((a, b) => a - b)
    const mid = Math.floor(levels.length / 2)
    out['med_level'] = levels[mid]
  }

  return out
}
