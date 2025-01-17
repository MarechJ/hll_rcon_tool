import { faker } from '@faker-js/faker';
import { SEEDING_MESSAGES, ADMIN_MESSAGES, PUNISHMENT_REASONS } from '../data/messages';

const generateNames = (playerId, currentName) => {
  const names = [
    {
      id: faker.number.int({ min: 1, max: 30000 }),
      name: currentName,
      player_id: playerId,
      created: faker.date.recent({ days: 60 }).toISOString(),
      last_seen: faker.date.recent().toISOString()
    }
  ];

  if (faker.datatype.boolean(0.3)) {
    const oldName = {
      id: faker.number.int({ min: 1, max: 30000 }),
      name: faker.internet.username(),
      player_id: playerId,
      created: faker.date.past({ years: 1 }).toISOString(),
      last_seen: faker.date.recent({ days: 90 }).toISOString()
    };
    names.push(oldName);
  }

  return names;
};

const generateFlags = () => {
  if (faker.datatype.boolean(0.3)) {
    const numFlags = faker.number.int({ min: 1, max: 3 });
    return Array(numFlags).fill(null).map(() => ({
      id: faker.number.int({ min: 1, max: 100 }),
      flag: faker.internet.emoji(),
      comment: faker.helpers.arrayElement(['', 'Good player', 'Regular']),
      modified: faker.date.recent().toISOString()
    }));
  }
  return [];
};

const generatePenaltyCount = () => {
  if (faker.datatype.boolean(0.4)) {
    return {
      KICK: faker.number.int({ min: 0, max: 10 }),
      PUNISH: faker.number.int({ min: 0, max: 100 }),
      TEMPBAN: faker.number.int({ min: 0, max: 5 }),
      PERMABAN: faker.number.int({ min: 0, max: 1 })
    };
  }
  return {
    KICK: 0,
    PUNISH: 0,
    TEMPBAN: 0,
    PERMABAN: 0
  };
};

const generateWatchlist = (playerId) => {
  const isWatched = faker.datatype.boolean(0.8);
  if (faker.datatype.boolean(0.2)) {
    return {
      id: faker.number.int({ min: 1, max: 100 }),
      modified: isWatched ? faker.date.recent().toISOString() : null,
      player_id: playerId,
      is_watched: isWatched,
      reason: isWatched ? faker.helpers.arrayElement([
        "I am watching you!",
        "Suspicious behavior",
        "Team killing history",
        "Under observation"
      ]) : null,
      by: faker.internet.username(),
      count: faker.number.int({ min: 0, max: 10 })
    };
  }
  return null;
};

const generateReceivedActions = () => {
  if (faker.datatype.boolean(0.4)) {
    const numActions = faker.number.int({ min: 1, max: 8 });
    return Array(numActions).fill(null).map(() => {
      const actionType = faker.helpers.arrayElement([
        "KICK", "PUNISH", "TEMPBAN", "PERMABAN", "MESSAGE",
        "SeedingRulesAutomod"
      ]);
      
      let reason, by;
      
      if (actionType === "SeedingRulesAutomod") {
        const count = faker.number.int({ min: 1, max: 5 });
        reason = SEEDING_MESSAGES.ATTACK_4TH_CAP(count);
        by = "SeedingRulesAutomod";
      } else if (actionType === "MESSAGE") {
        reason = faker.helpers.arrayElement(ADMIN_MESSAGES);
        by = faker.internet.username();
      } else {
        reason = faker.helpers.arrayElement(PUNISHMENT_REASONS);
        by = faker.internet.username();
      }

      return {
        action_type: actionType,
        reason,
        by,
        time: faker.date.recent({ days: 30 }).toISOString()
      };
    }).sort((a, b) => new Date(b.time) - new Date(a.time));
  }
  return [];
};

const generateSteamInfo = (playerId, type = "public") => {
  const baseInfo = {
    id: faker.number.int({ min: 1, max: 30000 }),
    created: faker.date.past().toISOString(),
    updated: faker.helpers.arrayElement([null, faker.date.recent().toISOString()]),
  };

  switch (type) {
    case "public": {
      const avatarHash = faker.string.alphanumeric(40).toLowerCase();
      return {
        ...baseInfo,
        profile: {
          avatar: `https://avatars.steamstatic.com/${avatarHash}.jpg`,
          avatarmedium: `https://avatars.steamstatic.com/${avatarHash}_medium.jpg`,
          avatarfull: `https://avatars.steamstatic.com/${avatarHash}_full.jpg`,
          avatarhash: avatarHash,
          gameid: "686810",
          steamid: playerId,
          realname: faker.person.fullName(),
          loccityid: faker.number.int({ min: 1000, max: 99999 }),
          lastlogoff: faker.date.future().getTime() / 1000,
          profileurl: `https://steamcommunity.com/id/${playerId}/`,
          personaname: faker.helpers.arrayElement([
            `[${faker.string.alpha(3).toUpperCase()}] ${faker.internet.username()}`,
            faker.internet.username(),
          ]),
          timecreated: faker.date.past().getTime() / 1000,
          gameserverip: `${faker.internet.ip()}:${faker.number.int({ min: 1000, max: 9999 })}`,
          locstatecode: faker.helpers.arrayElement(["U3", "NY", "CA", "TX"]),
          personastate: faker.number.int({ min: 0, max: 6 }),
          profilestate: 1,
          gameextrainfo: "Hell Let Loose",
          primaryclanid: faker.string.numeric(18),
          loccountrycode: faker.location.countryCode(),
          gameserversteamid: faker.string.numeric(17),
          personastateflags: 0,
          communityvisibilitystate: 3
        },
        country: faker.location.countryCode(),
        bans: {
          SteamId: playerId,
          VACBanned: false,
          EconomyBan: "none",
          CommunityBanned: false,
          NumberOfVACBans: 0,
          DaysSinceLastBan: 0,
          NumberOfGameBans: 0
        },
        has_bans: false
      };
    }

    case "private":
      return {
        ...baseInfo,
        profile: null,
        country: null,
        bans: null,
        has_bans: false
      };

    case "none":
    default:
      return null;
  }
};

const generateVip = (serverNumber, isActiveVip) => {
  return {
    server_number: serverNumber,
    expiration: isActiveVip ? faker.date.future().toISOString() : faker.date.between({ from: new Date() - 1000 * 60 * 60 * 24 * 30, to: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30) }).toISOString()
  };
};

const generateVips = (isVip, serverNumber) => {
  const vips = [];
  if (isVip) {
    vips.push(generateVip(serverNumber, true));
  }
  Array(faker.number.int({ min: 0, max: 2 })).fill(null).forEach((_, index) => {
    vips.push(generateVip(serverNumber + index + 1));
  });
  return vips;
};

export const generateProfile = (playerId, playerName, isVip = false, serverNumber = 1) => ({
  id: faker.number.int({ min: 1, max: 30000 }),
  player_id: playerId,
  created: faker.date.recent().toISOString(),
  names: generateNames(playerId, playerName),
  sessions: [
    {
      id: faker.number.int({ min: 50000, max: 60000 }),
      player_id: playerId,
      start: faker.date.recent().toISOString(),
      end: null,
      created: faker.date.recent().toISOString()
    }
  ],
  sessions_count: faker.number.int({ min: 1, max: 1000 }),
  total_playtime_seconds: faker.number.int({ min: 0, max: 1000000 }),
  current_playtime_seconds: faker.number.int({ min: 0, max: 150 }),
  received_actions: generateReceivedActions(),
  penalty_count: generatePenaltyCount(),
  blacklist: null,
  flags: generateFlags(),
  watchlist: generateWatchlist(playerId),
  steaminfo: generateSteamInfo(
    playerId, 
    faker.helpers.arrayElement(['public', 'private', 'none'])
  ),
  vips: generateVips(isVip, serverNumber),
}); 
