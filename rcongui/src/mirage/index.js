import { createServer } from "miragejs";
import { handleTeamView } from "./routes/team-view";
import { createGameState } from "./state/game";

export function makeServer({ environment = "development" } = {}) {
  let gameState = createGameState();
  
  const server = createServer({
    environment,

    routes() {
      this.urlPrefix = process.env.REACT_APP_API_URL;
      
      this.get("/get_team_view", () => {
        return handleTeamView(gameState);
      });

      this.passthrough();
    },
  });

  return server;
} 