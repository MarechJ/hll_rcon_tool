import { normalizePlayerProfile } from "./lib";

/**
 * Flatten the team view into a list of players.
 * @param {TeamViewResult} game The result of `get_team_view` API call.
 * @returns A list of all players in the game
 */
export const extractPlayers = (game) => {
  const players = [];
  const teams = ["axis", "allies", "unassigned"];

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
  return {
    ...player,
    profile,
  };
};

export const extractTeamState = (aTeam, name, searchTerm = "") => {
  const team = aTeam ?? {};
  const teamLevels = [];
  const out = {};
  out["name"] = name ?? "unknown";
  out["commander"] = null;
  out["armor"] = 0;
  out["infantry"] = 0;
  out["recon"] = 0;
  out["avg_level"] = 0;
  out["med_level"] = 0;
  out["no_sl_squads"] = [];
  out["players_in_lobby"] = [];
  out["squads"] = [];
  out["vips"] = 0;
  out["count"] = 0;
  const totals = ["combat", "offense", "defense", "support", "kills", "deaths"];
  for (const total of totals) {
    out[total] = 0;
  }

  const commander =
    "commander" in team && team.commander ? extendPlayer(team.commander) : null;
  if (
    commander &&
    (commander.name.includes(searchTerm) ||
      commander.player_id.includes(searchTerm))
  ) {
    out["commander"] = commander;
  }

  if (out["commander"]) {
    if (
      commander.name.includes(searchTerm) ||
      commander.player_id.includes(searchTerm)
    ) {
      out["count"]++;
      if (commander.is_vip) {
        out["vips"]++;
      }
    }
  }

  const squads = team["squads"];

  for (const squadKey in squads) {
    const squad = squads[squadKey];

    const squadLevels = [];

    const squadPlayers = squad.players
      .map(extendPlayer)
      .filter(
        (player) =>
          player.name.includes(searchTerm) ||
          player.player_id.includes(searchTerm)
      );

    if (squadPlayers.length > 0) {
      squadPlayers.forEach((player) => {
        for (const total of totals) {
          out[total] += player[total] || 0;
        }
        out["count"]++;
        squadLevels.push(player.level);
        teamLevels.push(player.level);
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
        if (player.is_vip) {
          out["vips"]++;
        }
      });

      out["squads"].push({
        ...squad,
        name: squadKey,
        players: squadPlayers,
        level: getAvg(squadLevels),
      });

      // If the squad has no leader, it's a no SL squad
      if (squadKey !== "null" && squad.has_leader === false) {
        out["no_sl_squads"].push(squadKey);
      }
    }
  }

  if (team.count) {
    out["avg_level"] = getAvg(teamLevels);
    out["med_level"] = getMedian(teamLevels);
  }

  return out;
};
