import React  from "react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PlayerView from "./components/PlayerView";
import useStyles from "./components/useStyles";
import Grid from "@material-ui/core/Grid";
import Logs from "./components/LogsView/logs";
import CssBaseline from "@material-ui/core/CssBaseline";
import HLLSettings from "./components/SettingsView/hllSettings";
import { ThemeProvider } from '@material-ui/styles';
import {
  HashRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import { createMuiTheme } from '@material-ui/core/styles';
import PlayersHistory from "./components/PlayersHistory";
import Header, { Footer } from "./components/Header";
import RconSettings from './components/RconSettings';
import {pink, red} from '@material-ui/core/colors';


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
  }
});

const withLove = createMuiTheme({
  palette: {
    primary: pink,
    secondary: red,
    background: {
      paper: pink
    }
  },
  overrides: {
    MuiCssBaseline: {
      "@global": {
        body: {
          backgroundSize: "cover",
          backgroundImage:
            'url("jk.jpg")'
        }
      }
    }
  }
});


const ThemeContext = React.createContext('light');


function App() {
  const classes = useStyles();
  const [dark, setDark] = React.useState(localStorage.getItem('darKTheme'))
  const setSaveDark = (bool) => {localStorage.setItem('darKTheme', bool); setDark(bool)}
  const theme = dark == "dark" ? darkTheme :  lightTheme

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
                  <RconSettings classes={classes} />
                </Grid>
              </Grid>
            </Route>
          </Switch>
          <Footer classes={classes} />
        </Router>
      </ThemeProvider>
    </div>
  );
}

export default App;
