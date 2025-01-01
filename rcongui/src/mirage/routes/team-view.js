import { faker } from '@faker-js/faker';
import { generatePlayer } from '../factories/player';
import { generateEmptySquad } from '../factories/squad';
import { updateTeamState } from '../factories/team';
import { SQUAD_TYPES } from '../data/roles';

export const handleTeamView = (gameState) => {
  // Update playtime for all players (15 seconds since last fetch)
  ["axis", "allies"].forEach(team => {
    Object.values(gameState[team].squads).forEach(squad => {
      squad.players.forEach(player => {
        player.profile.current_playtime_seconds += 15;
        player.profile.total_playtime_seconds += 15;
      });
    });
    if (gameState[team].commander) {
      gameState[team].commander.profile.current_playtime_seconds += 15;
      gameState[team].commander.profile.total_playtime_seconds += 15;
    }
  });

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