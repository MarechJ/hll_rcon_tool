import { createServer } from "miragejs";
import { handleTeamView } from "./routes/team-view";
import { createGameState } from "./state/game";
import { handleRecentLogs } from "./routes/recent-logs";

export function makeServer({ environment = "development" } = {}) {
  let gameState = createGameState();
  
  const server = createServer({
    environment,

    routes() {
      this.urlPrefix = process.env.REACT_APP_API_URL;
      
      this.get("/get_team_view", () => {
        return handleTeamView(gameState);
      });

      this.post("/get_recent_logs", (schema, request) => {
        const params = request.queryParams;
        return handleRecentLogs(gameState, {
          end: parseInt(params.end) || 500,
          filter_action: params.filter_action ? JSON.parse(params.filter_action) : [],
          filter_player: params.filter_player ? JSON.parse(params.filter_player) : [],
          inclusive_filter: params.inclusive_filter === 'true'
        });
      });

      this.passthrough();
    },
  });

  return server;
} 