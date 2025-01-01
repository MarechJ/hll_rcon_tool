import { faker } from '@faker-js/faker';
import { SQUAD_TYPES } from '../data/roles';
import { generatePlayer } from './player';

// Generate an empty squad structure
export const generateEmptySquad = (name, type = "infantry") => ({
  name,
  type,
  players: [],
  has_leader: false,
  combat: 0,
  offense: 0,
  defense: 0,
  support: 0,
  kills: 0,
  deaths: 0
});

// Generate a squad with players
export const generateSquad = (name, type = "infantry") => {
  const maxPlayers = SQUAD_TYPES[type].maxPlayers;
  const minPlayers = 1;
  const numPlayers = faker.number.int({ min: minPlayers, max: maxPlayers });
  const hasLeader = faker.datatype.boolean(); // 50% chance to have a leader

  const squad = generateEmptySquad(name, type);
  
  // Add leader first if squad has one
  if (hasLeader) {
    squad.players.push(generatePlayer(name, type, true));
    squad.has_leader = true;
  }
  
  // Add remaining players
  const remainingSlots = numPlayers - (hasLeader ? 1 : 0);
  for (let i = 0; i < remainingSlots; i++) {
    squad.players.push(generatePlayer(name, type, false));
  }

  // Calculate squad statistics
  squad.combat = squad.players.reduce((sum, p) => sum + p.combat, 0);
  squad.offense = squad.players.reduce((sum, p) => sum + p.offense, 0);
  squad.defense = squad.players.reduce((sum, p) => sum + p.defense, 0);
  squad.support = squad.players.reduce((sum, p) => sum + p.support, 0);
  squad.kills = squad.players.reduce((sum, p) => sum + p.kills, 0);
  squad.deaths = squad.players.reduce((sum, p) => sum + p.deaths, 0);

  return squad;
}; 