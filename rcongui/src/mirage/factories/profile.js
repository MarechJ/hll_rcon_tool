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
      name: faker.internet.userName(),
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
      flag: faker.helpers.arrayElement(['😍', '🎮', '⭐', '🎯', '🏆', '👑']),
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
  if (faker.datatype.boolean(0.2)) {
    return {
      id: faker.number.int({ min: 1, max: 100 }),
      modified: faker.helpers.arrayElement([null, faker.date.recent().toISOString()]),
      player_id: playerId,
      is_watched: true,
      reason: faker.helpers.arrayElement([
        "I am watching you!",
        "Suspicious behavior",
        "Team killing history",
        "Under observation"
      ]),
      by: faker.internet.userName(),
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
        by = faker.internet.userName();
      } else {
        reason = faker.helpers.arrayElement(PUNISHMENT_REASONS);
        by = faker.internet.userName();
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

export const generateProfile = (playerId, playerName) => ({
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
  total_playtime_seconds: faker.number.int({ min: 1000, max: 1000000 }),
  current_playtime_seconds: faker.number.int({ min: 100, max: 5000 }),
  received_actions: generateReceivedActions(),
  penalty_count: generatePenaltyCount(),
  blacklist: null,
  flags: generateFlags(),
  watchlist: generateWatchlist(playerId),
  steaminfo: null,
  vips: []
}); 