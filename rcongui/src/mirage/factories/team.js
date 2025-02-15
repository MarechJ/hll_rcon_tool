import { faker } from '@faker-js/faker';
import { generateSquad } from './squad';
import { generatePlayer } from './player';

const SPECIAL_USERNAMES = [
  'X',  // Single character
  '[VLK]Player',  // Starts with non-alphanumeric
  '*StarPlayer*',  // Starts with non-alphanumeric
  '_UnderscoreUser',  // Starts with non-alphanumeric
  '~TildeUser',  // Starts with non-alphanumeric
  '. . .', // Only dots and spaces
  '[', // Single bracket
];

// Generate initial team state
export const generateTeam = () => {
  const state = {
    squads: {
      able: generateSquad("able", "infantry"),
      baker: generateSquad("baker", "infantry"),
      charlie: generateSquad("charlie", "armor"),
      dog: generateSquad("dog", "recon"),
      null: generateSquad("null"),
    },
    commander: faker.datatype.boolean() ? generatePlayer("command", "infantry") : null,
    combat: 0,
    offense: 0,
    defense: 0,
    support: 0,
    kills: 0,
    deaths: 0,
    count: 0
  };

  // Add special username players to random squads
  SPECIAL_USERNAMES.forEach(specialName => {
    const randomSquad = faker.helpers.arrayElement(Object.keys(state.squads));
    const squadData = state.squads[randomSquad];
    const specialPlayer = generatePlayer(randomSquad, squadData.type);
    specialPlayer.name = specialName;
    squadData.players.push(specialPlayer);
  });

  // Calculate team totals
  Object.values(state.squads).forEach(squad => {
    squad.players.forEach(player => {
      state.combat += player.combat;
      state.offense += player.offense;
      state.defense += player.defense;
      state.support += player.support;
      state.kills += player.kills;
      state.deaths += player.deaths;
      state.count += 1;
    });
  });

  // Add commander stats if present
  if (state.commander) {
    state.combat += state.commander.combat;
    state.offense += state.commander.offense;
    state.defense += state.commander.defense;
    state.support += state.commander.support;
    state.kills += state.commander.kills;
    state.deaths += state.commander.deaths;
    state.count += 1;
  }

  return state;
};

// Helper to update team state (for use in the mirage server)
export const updateTeamState = (team) => {
  team.combat = 0;
  team.offense = 0;
  team.defense = 0;
  team.support = 0;
  team.kills = 0;
  team.deaths = 0;
  team.count = 0;

  Object.values(team.squads).forEach(squad => {
    squad.players.forEach(player => {
      team.combat += player.combat;
      team.offense += player.offense;
      team.defense += player.defense;
      team.support += player.support;
      team.kills += player.kills;
      team.deaths += player.deaths;
      team.count += 1;
    });
  });

  if (team.commander) {
    team.combat += team.commander.combat;
    team.offense += team.commander.offense;
    team.defense += team.commander.defense;
    team.support += team.commander.support;
    team.kills += team.commander.kills;
    team.deaths += team.commander.deaths;
    team.count += 1;
  }
}; 