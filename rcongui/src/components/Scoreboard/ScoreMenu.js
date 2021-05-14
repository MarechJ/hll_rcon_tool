import React from "react";
import { AppBar, Link, Toolbar } from "@material-ui/core";
import { Link as RouterLink } from "react-router-dom";

const ScoreMenu = ({classes}) => (
  <AppBar position="static">
    <Toolbar>
    <nav className={classes.title}>
      <Link
        variant="button"
        color="inherit"
        className={classes.firstLink}
        component={RouterLink}
        to="/"
      >
        Live
      </Link>
      <Link
        variant="button"
        color="inherit"
        className={classes.firstLink}
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
