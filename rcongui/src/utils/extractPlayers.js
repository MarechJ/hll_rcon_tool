import { normalizePlayerProfile } from "./lib";

/**
 * Flatten the team view into a list of players.
 * @param {TeamViewResult} game The result of `get_team_view` API call.
 * @returns A list of all players in the game
 */
export const extractPlayers = (game) => {
  const players = [];
  const teams = ["axis", "allies", "none", "null"];

  for (const teamKey of teams) {
    if (!(teamKey in game)) continue;

    const team = game[teamKey];
    const squads = team["squads"];

    for (const squadKey in squads) {
      const squadPlayers = squads[squadKey].players;
      players.push(...squadPlayers);
    }

    if ("commander" in team && team.commander) {
      players.push(team.commander);
    }
  }

  return players;
};

const getKpm = (kills, time_seconds) => {
  if (kills === 0 || time_seconds === 0) return 0;
  return Number((kills / time_seconds * 60));
};

const getAvg = (arr) => {
  return arr.reduce((sum, value) => sum + value, 0) / arr.length;
};

const getMedian = (arr) => {
  const sorted = arr.sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : getAvg([sorted[mid - 1], sorted[mid]]);
};

const extendPlayer = (player) => {
  const profile = normalizePlayerProfile(player.profile);
  // const kpm = getKpm(player.kills, profile.current_playtime_seconds);
  return {
    ...player,
    profile,
    // kpm,
  };
};

// TODO
// The current_playtime_seconds can be the time of the player's session,
// so it's not a good metric to use for KPM.
export const extractTeamState = (team) => {
  const totals = [
    "combat",
    "offense",
    "defense",
    "support",
    "kills",
    "deaths",
    "count",
  ];
  const teamLevels = [];
  // const teamKpm = [];
  const out = {};
  out["commander"] = "commander" in team && team.commander ? extendPlayer(team.commander) : null;
  out["armor"] = 0;
  out["infantry"] = 0;
  out["recon"] = 0;
  out["avg_level"] = 0;
  out["med_level"] = 0;
  out["no_sl_squads"] = [];
  out["players_in_lobby"] = [];
  out["squads"] = [];
  // out["kpm"] = 0;

  for (const total of totals) {
    out[total] = team[total] || 0;
  }

  const squads = team["squads"];

  for (const squadKey in squads) {
    const squad = squads[squadKey];

    const squadLevels = [];
    // const squadKpm = [];

    const squadPlayers = squad.players.map(extendPlayer);

    squadPlayers.forEach((player) => {
      squadLevels.push(player.level);
      // squadKpm.push(player.kpm);
      teamLevels.push(player.level);
      // teamKpm.push(player.kpm);
      switch (player.role) {
        case "sniper":
        case "spotter":
          out["recon"]++;
          break;
        case "tankcommander":
        case "crewman":
          out["armor"]++;
          break;
        default:
          out["infantry"]++;
          break;
      }
    });

    out["squads"].push({
      ...squad,
      name: squadKey,
      players: squadPlayers,
      // kpm: getAvg(squadKpm),
      level: getAvg(squadLevels),
    });

    // If the squad has no leader, it's a no SL squad
    if (squadKey !== "null" && squad.has_leader === false) {
      out["no_sl_squads"].push(squadKey);
    }
  }

  if (team.count) {
    out["avg_level"] = getAvg(teamLevels);
    out["med_level"] = getMedian(teamLevels);
    // out["kpm"] = getAvg(teamKpm);
  }

  return out;
};
