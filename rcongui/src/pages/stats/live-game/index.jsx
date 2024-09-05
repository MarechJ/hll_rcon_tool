import { Link } from "@mui/material";
import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { LiveScore } from "../../../components/Scoreboard/LiveScore";

const LiveGameScore = () => (
  <LiveScore
    endpoint="get_live_game_stats"
    title="CURRENT GAME"
    explainText={
      <React.Fragment>
        All players that are or were in the game are shown, check the{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/livescore"
        >
          Live Sessions
        </Link>{" "}
        for live stats accross several games or{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/gamescoreboard"
        >
          Past games
        </Link>{" "}
        for historical data. Real deaths only are counted (e.g. not redeploys /
        revives)
      </React.Fragment>
    }
  />
);

export default LiveGameScore;
