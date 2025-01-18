import dayjs from 'dayjs'
import {PlayerBase} from "@/types/player";
import {PlayerBaseWithAwards} from "@/pages/games/[id]";
import {ScoreboardMapStats} from "@/types/api";

export function getGameDuration(start: string, end: string) {
  const duration = dayjs.duration(dayjs(end).diff(dayjs(start)));

  return duration.format('H:mm:ss');
}

function isMostlyInfantry( player: PlayerBase ) {
  const nonInfantryKills = (player.kills_by_type.armor ?? 0) + (player.kills_by_type.commander ?? 0) + (player.kills_by_type.artillery ?? 0);
  return nonInfantryKills / player.kills < 0.25 && nonInfantryKills <= 5;
}

export const enrichPlayersWithAwards = (game: ScoreboardMapStats) => {
  const isShortGame = dayjs(game.end).diff(dayjs(game.start), 'minutes') < 25;

  if (isShortGame) {
    return game.player_stats.map(player => ({...player, awards: []}));
  }

  const maxStatsValues = calcMaxStatsValues(game.player_stats);

  const playersWithMaxValues = Object.entries(maxStatsValues).flatMap(([_, value]) => value.playerIds);

  return game.player_stats.map(player => {
    const enrichedPlayer: PlayerBaseWithAwards = {...player, awards: []};

    if (isMostlyInfantry(player)) {
      if (player.kills >= 10 && player.deaths === 0) {
        enrichedPlayer.awards.push({type: "zero_deaths", amount: player.kills})
      }
    }

    if (player.kills === 0 && player.deaths >= 10) {
      enrichedPlayer.awards.push({type: "zero_kills", amount: player.deaths})
    }

    if (player.kill_death_ratio === 1 && player.kills >= 10) {
      enrichedPlayer.awards.push({type: "kd_of_one", amount: player.kills})
    }

    if (playersWithMaxValues.includes(player.player_id)) {
      enrichedPlayer.awards.push(...Object.entries(maxStatsValues)
        .filter(([_, value]) => value.amount > 0 && value.playerIds.includes(player.player_id))
        .map(([key, value]) => ({type: key, amount: value.amount}))
      );
    }

    return enrichedPlayer;
  });
}


const allowedStats = [
  "kills_streak",
  "deaths",
  "deaths_without_kill_streak",
  "teamkills",
  "deaths_by_tk",
  "kill_death_ratio",
  "kills_by_type",
  "support",
  "zero_deaths",
  "zero_kills",
  "kd_of_one",
  "kills_by_type.commander",
  "kills_by_type.bazooka",
  "kills_by_type.grenade",
  "kills_by_type.mine",
  "kills_by_type.pak",
  "kills_by_type.satchel",

  // 'kills_by_type.infantry' already easily identifiable by the weapon type bar, would make awards to cluttered
  // 'kills_by_type.sniper' already easily identifiable by the weapon type bar, would make awards to cluttered
  // 'kills_by_type.artillery' already easily identifiable by the weapon type bar, would make awards to cluttered
  // 'kills_by_type.armor' already easily identifiable by the weapon type bar, would make awards to cluttered
  // 'kills_by_type.machine_gun' already easily identifiable by the weapon type bar, would make awards to cluttered

  // "kills" is already covered by various kills_by_type
  // "longest_life_secs", // too inaccurate
  // "shortest_life_secs", // too inaccurate
  // "combat", // covered by other awards (most likely tanker or AT)
  // "offense", // it is just the time being in enemy territory
  // "defense", // it is just the time being in friendly territory
  // "time_seconds", // most players are there the whole round
];

// stats which would be boring/useless, if tanks, artillery or commander would be included
const infOnlyStats = [
  "kills_streak",
  "kill_death_ratio",
  "teamkills",
  "support",
];

/**
 *  For each stat calc the max value and the playerIds which have this max value
 */
const calcMaxStatsValues = (stats: PlayerBase[]) => {
  const result: Partial<Record<keyof PlayerBase, {amount: number, playerIds: string[]}>> = {};

  stats.forEach((player) => {
    Object.entries(player).forEach(([key, value]) => {
      if (!allowedStats.includes(key)) {
        return;
      }
      if (infOnlyStats.includes(key) && !isMostlyInfantry(player)) {
        return;
      }
      if (typeof value === 'number') {
        calcMaxValue(result, key, value, player.player_id);
      } else if (value && typeof value === 'object') {
        Object.entries(value as Record<string, number>).forEach(([nestedKey, nestedValue]) => {
          if (typeof nestedValue === 'number') {
            const compositeKey = `${key}.${nestedKey}` as keyof PlayerBase;
            if (!allowedStats.includes(compositeKey)) {
              return;
            }
            calcMaxValue(result, compositeKey, nestedValue, player.player_id);
          }
        });
      }
    });
  });
  return result;
}

const calcMaxValue = (result: Partial<Record<keyof PlayerBase, {amount: number, playerIds: string[]}>>, key: string, value: number, playerId: string) => {
  const currentMaxValue = result[key as keyof PlayerBase];
  if (!currentMaxValue || currentMaxValue.amount < value) {
    result[key as keyof PlayerBase] = { amount: value, playerIds: [playerId] };
  } else if (currentMaxValue.amount === value) {
    currentMaxValue.playerIds.push(playerId);
  }
}

