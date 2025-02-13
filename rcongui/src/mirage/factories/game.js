import { faker } from '@faker-js/faker';
import { generateTeam, generateNullTeam } from './team';

export const createInitialState = () => {
  const state = {
    axis: generateTeam(),
    allies: generateTeam(),
    null: generateNullTeam()
  };

  // Ensure at least one squad has no leader
  const randomTeam = faker.helpers.arrayElement(Object.keys(state).filter(team => team !== 'null'));
  const randomSquad = faker.helpers.arrayElement(Object.keys(state[randomTeam].squads));
  state[randomTeam].squads[randomSquad].has_leader = false;
  state[randomTeam].squads[randomSquad].players = state[randomTeam].squads[randomSquad].players
    .filter(p => !["officer", "tankcommander", "spotter"].includes(p.role));

  // Ensure one team has no commander
  if (state.axis.commander && state.allies.commander) {
    state[faker.helpers.arrayElement(["axis", "allies"])].commander = null;
  }

  return state;
}; 