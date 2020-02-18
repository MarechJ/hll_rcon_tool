import React, { Component } from "react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PlayerView from "./components/PlayerView";
import useStyles from "./components/useStyles";
import Grid from "@material-ui/core/Grid";
import Logs from "./components/LogsView/logs";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import Link from "@material-ui/core/Link";
import CssBaseline from "@material-ui/core/CssBaseline";
import {
  HashRouter as Router,
  Switch,
  Route,
  Link as RouterLink
} from "react-router-dom";

function ButtonAppBar() {
  const classes = useStyles();

  return (
    <div className={classes.grow}>
      <AppBar position="static" elevation={0} className={classes.appBar}>
        <Toolbar className={classes.toolbar}>
          <nav>
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
              className={classes.link}
              component={RouterLink}
              to="/settings"
            >
              Settings
            </Link>
          </nav>
        </Toolbar>
      </AppBar>
    </div>
  );
}

const Live = ({ classes }) => (
  <Grid container spacing={1}>
    <Grid item sm={12} md={6}>
      <PlayerView classes={classes} />
    </Grid>
    <Grid item sm={12} md={6}>
      <Logs classes={classes} />
    </Grid>
  </Grid>
);

function App() {
  const classes = useStyles();

  return (
    <div className={"App " + classes.root}>
      <CssBaseline />
      <ToastContainer />
      <Router>
        <Grid container className={classes.grow}>
        <div className={classes.grow}>
      <AppBar position="static" elevation={0} className={classes.appBar}>
        <Toolbar className={classes.toolbar}>
          <nav>
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
              className={classes.link}
              component={RouterLink}
              to="/settings"
            >
              Settings
            </Link>
          </nav>
        </Toolbar>
      </AppBar>
    </div>
        </Grid>
        <Switch>
          <Route path="/" exact >
            <Live classes={classes} />
          </Route>
          <Route path="/settings">
            <h1>Under construction</h1>
          </Route>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
