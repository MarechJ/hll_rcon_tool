import { faker } from '@faker-js/faker';
import { getSquadLeaderRole, getAvailableRoles } from '../data/roles';
import { generateProfile } from './profile';
import { getAllPlatforms } from '@/constants/platforms';

export const generatePlayer = (squadName, squadType, isLeader = false, serverNumber = 1, clanTag = "") => {
  const name = clanTag + faker.internet.username();

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
    vehicle_kills: faker.number.int(0),
    vehicles_destroyed: faker.number.int(0),
    map_playtime_seconds: faker.number.int({ min: 1, max: 10*60*60 }),
    level: faker.number.int({ min: 1, max: 500 }),
    eos_id: faker.string.alphanumeric(32),
    world_position: {
      x: faker.number.float({ min: -100_000, max: 100_000 }),
      y: faker.number.float({ min: -100_000, max: 100_000 }),
      z: faker.number.float({ min: -100_000, max: 100_000 }),
    },
    clan_tag: faker.person.suffix(),
    platform: faker.helpers.arrayElement(getAllPlatforms().map(p => p.value)),
    team_kills: faker.number.int({ min: 0, max: 10 }),
  };
};