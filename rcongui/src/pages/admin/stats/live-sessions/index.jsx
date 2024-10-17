import { Link } from "@mui/material";
import React from "react";
import { Link as RouterLink } from "react-router-dom";
import { LiveScore } from "@/components/Scoreboard/LiveScore";

const LiveSessionScore = () => (
  <LiveScore
    endpoint="get_live_scoreboard"
    title="LIVE SESSIONS"
    explainText={
      <React.Fragment>
        Only ingame players are shown. Stats are reset on disconnection, not per
        game, check the{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/livegamescore"
        >
          Live Game
        </Link>{" "}
        or{" "}
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

export default LiveSessionScore;
