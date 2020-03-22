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
import Link from "@material-ui/core/Link";
import CssBaseline from "@material-ui/core/CssBaseline";
import HLLSettings from "./components/SettingsView/hllSettings";
import { ThemeProvider } from '@material-ui/styles';
import {
  HashRouter as Router,
  Switch,
  Route,
  Link as RouterLink
} from "react-router-dom";
import { createMuiTheme } from '@material-ui/core/styles';
import Brightness4Icon from '@material-ui/icons/Brightness4';
import Checkbox from '@material-ui/core/Checkbox';
import Brightness4OutlinedIcon from '@material-ui/icons/Brightness4Outlined';
import UseAutcomplete from './components/PlayersHistory'
import PlayersHistory from "./components/PlayersHistory";
import Header from "./components/Header";


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


const darkTheme = createMuiTheme({
  palette: {
    type: 'dark',
  },
});

const lightTheme = createMuiTheme({
  palette: {
    type: 'light',
  },
});


function App() {
  const classes = useStyles();
  const [dark, setDark] = React.useState(localStorage.getItem('darKTheme'))
  const setSaveDark = (bool) => {localStorage.setItem('darKTheme', bool); setDark(bool)}
  const theme = dark ? darkTheme : lightTheme
 
  return (
    <div className={"App " + classes.root}>
      <ThemeProvider theme={theme} >
        <CssBaseline />
        <ToastContainer />
        <Router>
          <Header classes={classes} setSaveDark={setSaveDark} dark={dark}/>
          <Switch>
            <Route path="/" exact>
              <Live classes={classes} />
            </Route>
            <Route path="/history">
              <Grid container>
                <Grid item sm={12} lg={12}>
                  <PlayersHistory classes={classes} />
                 </Grid>
              </Grid>
            </Route>
            <Route path="/settings">
              <Grid container>
                <Grid item sm={12} lg={6}>
                  <HLLSettings classes={classes} />
                </Grid>
                <Grid item sm={12} lg={6}>
                    <h2>Advanced RCON settings</h2>
                    <small>Coming soon</small>
                </Grid>
              </Grid>
            </Route>
          </Switch>
        </Router>
      </ThemeProvider>
    </div>
  );
}

export default App;
