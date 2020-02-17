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

function ButtonAppBar() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar
        position="static"
        
        elevation={0}
        className={classes.appBar}
      >
        <Toolbar className={classes.toolbar}>
          <nav>
            <Link
              variant="button"
              color="inherit"
              href="#"
              className={classes.firstLink}
            >
              Live
            </Link>
            <Link
              variant="button"
              color="inherit"
              href="#"
              className={classes.link}
            >
              Settings
            </Link>
            <Link
              variant="button"
              color="inherit"
              href="#"
              className={classes.link}
            >
              Services
            </Link>
          </nav>
        </Toolbar>
      </AppBar>
    </div>
  );
}

function App() {
  const classes = useStyles();

  return (
    <div className={"App " + classes.root}>
      <CssBaseline />
      <ToastContainer />
      <Grid container spacing={1}>
        <Grid item sm={12} md={12}>
          <ButtonAppBar />
        </Grid>
      </Grid>
      <Grid container spacing={1}>
        <Grid item sm={12} md={6}>
          <PlayerView classes={classes} />
        </Grid>
        <Grid item sm={12} md={6}>
          <Logs classes={classes} />
        </Grid>
      </Grid>
    </div>
  );
}

export default App;
