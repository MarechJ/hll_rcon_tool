import React, { Component } from "react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PlayerView from "./components/PlayerView";
import useStyles from "./components/useStyles";

function App() {
  const classes = useStyles();

  return (
    <div className={"App " + classes.root}>
      <ToastContainer />
      <PlayerView classes={classes} />
    </div>
  );
}

export default App;
