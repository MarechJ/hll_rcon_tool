import { faker } from '@faker-js/faker';
import { generatePlayer } from '../factories/player';
import { generateEmptySquad } from '../factories/squad';
import { updateTeamState } from '../factories/team';
import { SQUAD_TYPES } from '../data/roles';

const PLAYTIME_INCREMENT = 15;

export const handleTeamView = (gameState) => {
  // First collect all players across both teams
  const allPlayers = [];
  ["axis", "allies"].forEach(team => {
    Object.values(gameState[team].squads).forEach(squad => {
      allPlayers.push(...squad.players);
    });
    if (gameState[team].commander) {
      allPlayers.push(gameState[team].commander);
    }
  });

  // Update playtime for all players (15 seconds since last fetch)
  ["axis", "allies"].forEach(team => {
    Object.values(gameState[team].squads).forEach(squad => {
      squad.players.forEach(player => {
        // Set profile values first
        if (player.profile) {
          player.profile.current_playtime_seconds += PLAYTIME_INCREMENT;
          player.profile.total_playtime_seconds += PLAYTIME_INCREMENT;
        }
        player.kills += faker.number.int({ min: 0, max: 3 });
        player.deaths += faker.number.int({ min: 0, max: 1 });
        player.combat += faker.number.int({ min: 0, max: 30 });
        player.offense += faker.number.int({ min: 0, max: 10 });
        player.defense += faker.number.int({ min: 0, max: 10 });
        player.support += faker.number.int({ min: 0, max: 50 });
      });
    });
    
    if (gameState[team].commander) {
      if (gameState[team].commander.profile) {
        gameState[team].commander.profile.current_playtime_seconds += PLAYTIME_INCREMENT;
        gameState[team].commander.profile.total_playtime_seconds += PLAYTIME_INCREMENT;
      }
    }
  });

  // Select one random player and set their profile to null after all updates
  const randomPlayer = faker.helpers.arrayElement(allPlayers);
  randomPlayer.profile = null;

  // Randomly modify the state (30% chance)
  if (faker.number.int({ min: 1, max: 10 }) > 7) {
    const team = faker.helpers.arrayElement(["axis", "allies"]);
    const squad = faker.helpers.arrayElement(Object.keys(gameState[team].squads));
    const squadData = gameState[team].squads[squad];

    // Randomly add or remove a player (50% chance for each)
    if (faker.datatype.boolean()) {
      // Add player if squad isn't full
      const maxPlayers = SQUAD_TYPES[squadData.type].maxPlayers;
      if (squadData.players.length < maxPlayers) {
        const newPlayer = generatePlayer(
          squad, 
          squadData.type,
          !squadData.has_leader && faker.datatype.boolean()
        );
        squadData.players.push(newPlayer);
        if (newPlayer.role === "officer" || newPlayer.role === "tankcommander" || newPlayer.role === "spotter") {
          squadData.has_leader = true;
        }
      }
    } else {
      // Remove player if squad has more than one player
      if (squadData.players.length > 1) {
        const removedPlayer = squadData.players.pop();
        // Update has_leader if we removed the leader
        if (["officer", "tankcommander", "spotter"].includes(removedPlayer.role)) {
          squadData.has_leader = squadData.players.some(p => 
            ["officer", "tankcommander", "spotter"].includes(p.role)
          );
        }
      }
    }

    // Occasionally add or remove a squad (10% chance)
    if (faker.number.int({ min: 1, max: 20 }) > 18) {
      const squadName = faker.helpers.arrayElement(["dog", "easy", "fox", "george"]);
      const squadType = faker.helpers.arrayElement(["infantry", "armor", "recon"]);

      if (!gameState[team].squads[squadName]) {
        // Add new squad
        gameState[team].squads[squadName] = generateEmptySquad(squadName, squadType);
        // Add initial player
        const initialPlayer = generatePlayer(
          squadName,
          squadType,
          faker.datatype.boolean() // 50% chance to start with a leader
        );
        gameState[team].squads[squadName].players.push(initialPlayer);
        gameState[team].squads[squadName].has_leader = ["officer", "tankcommander", "spotter"].includes(initialPlayer.role);
      } else {
        // Remove squad if it exists and isn't one of the original three
        if (!["able", "baker", "charlie"].includes(squadName)) {
          delete gameState[team].squads[squadName];
        }
      }
    }

    // Occasionally toggle commander (5% chance)
    if (faker.number.int({ min: 1, max: 20 }) > 19) {
      if (gameState[team].commander) {
        gameState[team].commander = null;
      } else {
        gameState[team].commander = generatePlayer("command", "infantry");
      }
    }
  }

  // Update team totals
  ["axis", "allies"].forEach(team => {
    updateTeamState(gameState[team]);
  });

  return {
    result: {
      fail_count: 0,
      ...gameState
    }
  };
}; 