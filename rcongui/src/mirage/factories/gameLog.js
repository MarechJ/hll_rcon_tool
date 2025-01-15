import { faker } from '@faker-js/faker';

const LOG_ACTIONS = [
  'ADMIN', 'ADMIN BANNED', 'ADMIN KICKED', 'CAMERA', 
  'CHAT[Allies][Team]', 'CHAT[Allies][Unit]',
  'CHAT[Axis][Team]', 'CHAT[Axis][Unit]',
  'CONNECTED', 'DISCONNECTED', 'KILL', 'MATCH', 'MATCH ENDED',
  'MATCH START', 'MESSAGE', 'TEAM KILL', 'TEAMSWITCH',
  'TK AUTO', 'TK AUTO BANNED', 'TK AUTO KICKED',
  'VOTE', 'VOTE COMPLETED', 'VOTE STARTED'
];

const getRandomPlayer = (gameState, team = null) => {
  const players = [];
  const targetTeam = team || faker.helpers.arrayElement(['axis', 'allies']);
  
  // Get commander if exists
  if (gameState[targetTeam].commander) {
    players.push(gameState[targetTeam].commander);
  }
  
  // Get all squad players
  Object.values(gameState[targetTeam].squads).forEach(squad => {
    players.push(...squad.players);
  });
  
  return faker.helpers.arrayElement(players);
};

const generateMessage = (action, player1, player2, weapon) => {
  switch (action) {
    case 'KILL':
      return `${player1.name}(${player1.team}/${player1.player_id}) -> ${player2.name}(${player2.team}/${player2.player_id}) with ${weapon}`;
    case 'TEAM KILL':
      return `${player1.name}(${player1.team}/${player1.player_id}) -> ${player2.name}(${player2.team}/${player2.player_id}) with ${weapon}`;
    case 'CHAT[Allies][Team]':
    case 'CHAT[Allies][Unit]':
    case 'CHAT[Axis][Team]':
    case 'CHAT[Axis][Unit]':
      return `${player1.name}(${player1.team}/${player1.player_id}): ${faker.lorem.sentence()}`;
    case 'CONNECTED':
    case 'DISCONNECTED':
      return `${player1.name}(${player1.player_id})`;
    default:
      return faker.lorem.sentence();
  }
};

export const generateGameLog = (gameState) => {
  const action = faker.helpers.arrayElement(LOG_ACTIONS);
  const timestamp = faker.date.recent();
  
  let player1, player2;
  
  switch (action) {
    case 'KILL':
      // For kills, get players from opposite teams
      player1 = getRandomPlayer(gameState, 'allies');
      player2 = getRandomPlayer(gameState, 'axis');
      break;
    case 'TEAM KILL':
      // For team kills, get players from same team
      const team = faker.helpers.arrayElement(['allies', 'axis']);
      player1 = getRandomPlayer(gameState, team);
      player2 = getRandomPlayer(gameState, team);
      break;
    case 'CHAT[Allies][Team]':
    case 'CHAT[Allies][Unit]':
      player1 = getRandomPlayer(gameState, 'allies');
      break;
    case 'CHAT[Axis][Team]':
    case 'CHAT[Axis][Unit]':
      player1 = getRandomPlayer(gameState, 'axis');
      break;
    default:
      player1 = getRandomPlayer(gameState);
  }

  const weapon = ['KILL', 'TEAM KILL'].includes(action) 
    ? faker.helpers.arrayElement(['MP40', 'WALTHER P38', 'M1 GARAND', 'THOMPSON']) 
    : null;

  return {
    version: 1,
    timestamp_ms: timestamp.getTime(),
    event_time: timestamp.toISOString(),
    relative_time_ms: faker.number.float({ min: -2000, max: 0 }),
    action,
    player_name_1: player1.name,
    player_id_1: player1.player_id,
    player_name_2: player2?.name || null,
    player_id_2: player2?.player_id || null,
    weapon,
    message: generateMessage(action, player1, player2, weapon),
    sub_content: null
  };
};

export const generateGameLogs = (gameState, count = 50) => {
  return Array.from({ length: count }, () => generateGameLog(gameState))
    .sort((a, b) => b.timestamp_ms - a.timestamp_ms);
};
