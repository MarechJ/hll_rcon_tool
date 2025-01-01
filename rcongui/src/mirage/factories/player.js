import { faker } from '@faker-js/faker';
import { getSquadLeaderRole, getAvailableRoles } from '../data/roles';
import { generateProfile } from './profile';

export const generatePlayer = (squadName, squadType, isLeader = false) => {
  const name = faker.internet.userName();
  const playerId = faker.string.numeric(17);
  
  let role;
  if (isLeader) {
    role = getSquadLeaderRole(squadType);
  } else {
    const availableRoles = getAvailableRoles(squadType, false);
    role = faker.helpers.arrayElement(availableRoles);
  }

  return {
    name,
    player_id: playerId,
    country: faker.helpers.arrayElement([null, "US", "DE", "RU", "CZ", "FR", "GB"]),
    steam_bans: null,
    profile: generateProfile(playerId, name),
    is_vip: faker.datatype.boolean(),
    unit_id: faker.number.int({ min: 0, max: 24 }),
    unit_name: squadName,
    loadout: faker.helpers.arrayElement(["standard issue", "veteran"]),
    team: faker.helpers.arrayElement(["allies", "axis"]),
    role,
    kills: faker.number.int({ min: 0, max: 50 }),
    deaths: faker.number.int({ min: 0, max: 30 }),
    combat: faker.number.int({ min: 0, max: 500 }),
    offense: faker.number.int({ min: 0, max: 300 }),
    defense: faker.number.int({ min: 0, max: 400 }),
    support: faker.number.int({ min: 0, max: 1000 }),
    level: faker.number.int({ min: 1, max: 500 })
  };
};