import React from "react";
import { AppBar, Link, Toolbar } from "@material-ui/core";
import { Link as RouterLink } from "react-router-dom";

const ScoreMenu = () => (
  <AppBar position="static">
    <Toolbar>
      <nav >
        <Link
          variant="button"
          color="inherit"
          
          component={RouterLink}
          to="/"
        >
          Live game
        </Link>
        <Link
          variant="button"
          color="inherit"
          
          component={RouterLink}
          to="/livescore"
        >
          Live sessions
        </Link>
        <Link
          variant="button"
          color="inherit"
          
          component={RouterLink}
          to="/gamescoreboard"
        >
          Last games
        </Link>
      </nav>
    </Toolbar>
  </AppBar>
);

export default ScoreMenu;
