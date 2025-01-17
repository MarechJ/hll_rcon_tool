import { faker } from '@faker-js/faker';
import { getSquadLeaderRole, getAvailableRoles } from '../data/roles';
import { generateProfile } from './profile';

export const generatePlayer = (squadName, squadType, isLeader = false, serverNumber = 1) => {
  const name = faker.internet.username();

  const steamId = "7656119" + faker.string.numeric(10);
  const otherId = faker.string.alphanumeric({ length: 32, casing: "lower" });
  const playerId = faker.helpers.arrayElement([steamId, otherId]);
  const isVip = faker.datatype.boolean(0.3);

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
    country: faker.helpers.arrayElement([null, faker.location.countryCode()]),
    steam_bans: null,
    profile: generateProfile(playerId, name, isVip, serverNumber),
    is_vip: isVip,
    unit_id: faker.number.int({ min: 0, max: 24 }),
    unit_name: squadName,
    loadout: faker.helpers.arrayElement(["standard issue", "veteran"]),
    team: faker.helpers.arrayElement(["allies", "axis"]),
    role,
    kills: faker.number.int(0),
    deaths: faker.number.int(0),
    combat: faker.number.int(0),
    offense: faker.number.int(0),
    defense: faker.number.int(0),
    support: faker.number.int(0),
    level: faker.number.int({ min: 1, max: 500 })
  };
};