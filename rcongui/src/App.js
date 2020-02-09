import React, { Component } from "react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PlayerView from "./components/PlayerView";
import useStyles from "./components/useStyles";
import Grid from "@material-ui/core/Grid";
import Logs from './components/LogsView/logs'

function App() {
  const classes = useStyles();

  return (
    <div className={"App " + classes.root}>
      <ToastContainer />
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
