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

export const generateTicks = (max: number, interval: number, negative?: boolean) => {
  let ticks = [];

  for (let i = 1; i < max / interval; i++) {
    ticks.push(i * interval);
    if (negative) {
      ticks.unshift(-i * interval);
    }
  }
  ticks.push(max);
  if (negative) {
    ticks.unshift(-max);
  }

  return ticks;
}

// https://hellletloose.fandom.com/wiki/Career_level
export const levelToRank = (level: number) => {
  if (level < 20) return "Private";
  if (level < 30) return "Private First Class";
  if (level < 40) return "Corporal";
  if (level < 50) return "Sergeant";
  if (level < 60) return "Staff Sergeant";
  if (level < 70) return "First Sergeant";
  if (level < 80) return "Master Sergeant";
  if (level < 90) return "2nd Lieutenant";
  if (level < 100) return "1st Lieutenant";
  if (level < 150) return "Captain";
  if (level < 200) return "Major";
  if (level < 250) return "Lieutenant Colonel";
  if (level < 300) return "Colonel";
  if (level < 350) return "Brigadier General";
  if (level < 400) return "Major General";
  if (level < 450) return "Lieutenant General";
  if (level < 500) return "General";
  return "General of the Army";
};

export function getPlayerTier(level: number) {
  if (level < 20) {
    return "Novice";
  } else if (level >= 20 && level < 75) {
    return "Apprentice";
  } else if (level >= 75 && level < 200) {
    return "Expert";
  } else if (level >= 200 && level < 350) {
    return "Master";
  } else {
    return "Legend";
  }
}

// Returns tier colors based on theme mode ("light" or "dark")
export const getTierColors = (mode = "light") => ({
  Novice: mode === "dark" ? colors.red[500] : colors.red[700],
  Apprentice: mode === "dark" ? colors.yellow[500] : colors.yellow[800],
  Expert: mode === "dark" ? colors.green[500] : colors.green[700],
  Master: mode === "dark" ? colors.blue[500] : colors.blue[700],
  Legend: mode === "dark" ? colors.purple[500] : colors.purple[700],
});
