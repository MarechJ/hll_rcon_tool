import {Faceoff, Player, PlayerTeamAssociation,TeamEnum } from '@/types/player'
import colors from 'tailwindcss/colors'

export function mergeKillsDeaths(player: Player) {
  const { most_killed: killsByPlayer, death_by: deathsByPlayer } = player
  const allPlayerKeys = new Set(Object.keys(killsByPlayer).concat(Object.keys(deathsByPlayer)))
  const merged: Faceoff[] = []
  // hacky way to recognize if key is player's name or players'id
  // if any of the keys has any other value than [a-z0-9] it is set of names
  // as it used to be recorded like that 
  const isSetOfNames = allPlayerKeys.keys().some(key => !key.match(/^[a-zA-Z0-9]+$/))
  allPlayerKeys.forEach((key) => {
    const faceoff: Faceoff =
    isSetOfNames
      ? {
          name: key,
          kills: killsByPlayer[key] ?? 0,
          deaths: deathsByPlayer[key] ?? 0,
          diff: (killsByPlayer[key] ?? 0) - (deathsByPlayer[key] ?? 0),
        }
      : {
          id: key,
          kills: killsByPlayer[key] ?? 0,
          deaths: deathsByPlayer[key] ?? 0,
          diff: (killsByPlayer[key] ?? 0) - (deathsByPlayer[key] ?? 0),
        }

    merged.push(faceoff)
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

export function getTeamFromAssociation(team?: PlayerTeamAssociation | string | null): TeamEnum {
  if (team === undefined || team === null) {
    return TeamEnum.UNKNOWN;
  }
  if (typeof team === "string") {
    if (team === "axis") return TeamEnum.AXIS;
    if (team === "allies") return TeamEnum.ALLIES;
    return TeamEnum.UNKNOWN;
  }
  if (typeof team === "object" && "confidence" in team) {
    return team.confidence === 'strong' ? team.side : TeamEnum.MIXED;
  }
  return TeamEnum.UNKNOWN
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
