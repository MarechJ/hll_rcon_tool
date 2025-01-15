import { faker } from '@faker-js/faker';
import { generateGameLog, generateGameLogs } from '../factories/gameLog';

// In-memory storage for logs
let storedLogs = [];

const initializeLogs = (gameState) => {
  if (storedLogs.length === 0) {
    storedLogs = generateGameLogs(gameState, 500);
  }
};

const generateNewLogs = (gameState, count = 10) => {
  const latestTimestamp = storedLogs.length > 0
    ? Math.max(...storedLogs.map(log => log.timestamp_ms))
    : Date.now();
  
  return Array.from({ length: count }, () => {
    const log = generateGameLog(gameState);
    const newTimestamp = new Date(latestTimestamp + faker.number.int({ min: 1000, max: 5000 }));
    return {
      ...log,
      timestamp_ms: newTimestamp.getTime(),
      event_time: newTimestamp.toISOString()
    };
  });
};

export const handleRecentLogs = (gameState, params = {}) => {
  const {
    end = 500,
    filter_action = [],
    filter_player = [],
    inclusive_filter = true
  } = params;

  // Initialize logs if empty
  initializeLogs(gameState);

  // Add new logs
  storedLogs = [...generateNewLogs(gameState, 10), ...storedLogs]
    // Keep only the specified number of logs
    .slice(0, end)
    // Sort by timestamp (most recent first)
    .sort((a, b) => b.timestamp_ms - a.timestamp_ms);

  // Apply filters if they exist
  let filteredLogs = storedLogs;
  if (filter_action.length > 0 || filter_player.length > 0) {
    filteredLogs = storedLogs.filter(log => {
      const matchesAction = filter_action.length === 0 || filter_action.includes(log.action);
      const matchesPlayer = filter_player.length === 0 || 
        filter_player.includes(log.player_name_1) || 
        (log.player_name_2 && filter_player.includes(log.player_name_2));

      return inclusive_filter 
        ? (matchesAction || matchesPlayer)
        : (matchesAction && matchesPlayer);
    });
  }

  // Extract unique actions and players from the filtered logs
  const actions = [...new Set(filteredLogs.map(log => log.action))].sort();
  const players = [...new Set([
    ...filteredLogs.map(log => log.player_name_1),
    ...filteredLogs.map(log => log.player_name_2).filter(Boolean)
  ])].sort();

  return {
    result: {
      actions,
      players,
      logs: filteredLogs
    }
  };
};
