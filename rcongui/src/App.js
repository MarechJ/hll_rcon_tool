import React from "react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PlayerView from "./components/PlayerView";
import useStyles from "./components/useStyles";
import Grid from "@material-ui/core/Grid";
import Logs from "./components/LogsView/logs";
import CssBaseline from "@material-ui/core/CssBaseline";
import HLLSettings from "./components/SettingsView/hllSettings";
import { ThemeProvider } from "@material-ui/styles";
import { HashRouter as Router, Switch, Route } from "react-router-dom";
import LogsHistory from "./components/LogsHistory";
import { createMuiTheme } from "@material-ui/core/styles";
import PlayersHistory from "./components/PlayersHistory";
import Header, { Footer } from "./components/Header";
import RconSettings from "./components/RconSettings";
import { pink, red } from "@material-ui/core/colors";
import ServicesList from "./components/Services";
import PlayerGrid from "./components/PlayersHistory/playerGrid";
import { isNull } from "lodash";
import { LiveScore } from "./components/Scoreboard";
import { Typography } from "@material-ui/core";
import ScoreMenu from './components/Scoreboard/ScoreMenu'
import GamesScore from "./components/Scoreboard/GamesScore";
import PlayerInfo from "./components/PlayerInfo";

const Live = ({ classes }) => {
  const [mdSize, setMdSize] = React.useState(6);
  const [direction, setDirection] = React.useState("");
  const isFullScreen = () => mdSize !== 6;
  const toggleMdSize = () => (isFullScreen() ? setMdSize(6) : setMdSize(12));

  return (
    <Grid container spacing={1} direction={direction}>
      <Grid item sm={12} md={mdSize}>
        <PlayerView
          classes={classes}
          onFullScreen={() => {
            setDirection("");
            toggleMdSize();
          }}
          isFullScreen={isFullScreen()}
        />
      </Grid>
      <Grid item sm={12} md={mdSize}>
        <Logs
          classes={classes}
          onFullScreen={() => {
            direction == "column-reverse"
              ? setDirection("")
              : setDirection("column-reverse");
            toggleMdSize();
          }}
          isFullScreen={isFullScreen()}
        />
      </Grid>
    </Grid>
  );
};

// Easy way to make ugly ass themes: https://material.io/resources/color/#!/?view.left=0&view.right=0&primary.color=33691E&secondary.color=3E2723
const darkTheme = createMuiTheme({
  palette: {
    type: "dark",
  },
});

const lightTheme = createMuiTheme({
  palette: {
    type: "light",
  },
});

const GreenYellowDarkTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#5edfca",
      main: "#17ad99",
      dark: "#007d6b",
      contrastText: "#fff",
    },
    secondary: {
      light: "#ffe54c",
      main: "#ffb300",
      dark: "#c68400",
      contrastText: "#000",
    },
    background: {
      default: "#303030",
      paper: "#424242",
    },
    text: {
      primary: "#fff",
      secondary: " rgba(255, 255, 255, 0.7)",
      disabled: "rgba(255, 255, 255, 0.5)",
    },
  },
});

const GreenYellowLightTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#5edfca",
      main: "#17ad99",
      dark: "#007d6b",
      contrastText: "#fff",
    },
    secondary: {
      light: "#ffe54c",
      main: "#ffb300",
      dark: "#c68400",
      contrastText: "#000",
    },
  },
});

const YellowGreenTheme = createMuiTheme({
  palette: {
    secondary: {
      light: "#5edfca",
      main: "#17ad99",
      dark: "#007d6b",
      contrastText: "#fff",
    },
    primary: {
      light: "#ffe54c",
      main: "#ffb300",
      dark: "#c68400",
      contrastText: "#000",
    },
  },
});

const RedTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#ff7961",
      main: "#f44336",
      dark: "#ba000d",
      contrastText: "#fff",
    },
    secondary: {
      light: "#708690",
      main: "#445963",
      dark: "#1b3039",
      contrastText: "#000",
    },
  },
});

const GreyBlueTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#8eacbb",
      main: "#607d8b",
      dark: "#34515e",
      contrastText: "#fff",
    },
    secondary: {
      light: "#c3fdff",
      main: "#90caf9",
      dark: "#5d99c6",
      contrastText: "#fff",
    },
    background: {
      default: "#303030",
      paper: "#424242",
    },
    text: {
      primary: "#fff",
      secondary: " rgba(255, 255, 255, 0.7)",
      disabled: "rgba(255, 255, 255, 0.5)",
    },
  },
});

const PurplePinkTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#d05ce3",
      main: "#9c27b0",
      dark: "#6a0080",
      contrastText: "#000",
    },
    secondary: {
      light: "#ffeeff",
      main: "#f8bbd0",
      dark: "#c48b9f",
      contrastText: "#fff",
    },
  },
});

const CamoDarkTheme = createMuiTheme({
  palette: {
    primary: {
      light: "#629749",
      main: "#33691e",
      dark: "#003d00",
      contrastText: "#000",
    },
    secondary: {
      light: "#ffffb3",
      main: "#ffe082",
      dark: "#caae53",
      contrastText: "#000",
    },
    background: {
      default: "#343434",
      paper: "#424242",
    },
    text: {
      primary: "#fff",
      secondary: " rgba(255, 255, 255, 0.7)",
      disabled: "rgba(255, 255, 255, 0.5)",
    },
  },
});

const CamoLight = createMuiTheme({
  palette: {
    primary: {
      light: "#629749",
      main: "#33691e",
      dark: "#003d00",
      contrastText: "#000",
    },
    secondary: {
      light: "#6a4f4b",
      main: "#3e2723",
      dark: "#1b0000",
      contrastText: "#000",
    },
    background: {
      default: "#ffffe5",
      paper: "#fff8e1",
    },
    text: {
      primary: "#000",
      secondary: " rgba(0, 0, 0, 0.7)",
      disabled: "rgba(0, 0, 0, 0.5)",
    },
  },
});

const hll = createMuiTheme({
  palette: {
    primary: {
      light: "#484848",
      main: "#212121",
      dark: "#000000",
      contrastText: "#fff",
    },
    secondary: {
      light: "#ffac42",
      main: "#f47b00",
      dark: "#ba4c00",
      contrastText: "#000",
    },
    background: {
      default: "#343434",
      paper: "#5b5b5b",
    },
    text: {
      primary: "#ffffff",
      secondary: " rgba(0, 0, 0, 0.7)",
      disabled: "rgba(0, 0, 0, 0.5)",
    },
  },
  overrides: {
    MuiCssBaseline: {
      "@global": {
        body: {
          backgroundRepeat: "no-repeat",
          backgroundAttachment: "fixed",
          backgroundSize: "cover",
          backgroundImage: 'url("hll.jpg")',
        },
      },
    },
  },
});

const withLove = createMuiTheme({
  palette: {
    primary: pink,
    secondary: red,
    background: {
      paper: pink,
    },
  },
  overrides: {
    MuiCssBaseline: {
      "@global": {
        body: {
          backgroundSize: "cover",
          backgroundImage: 'url("jk.jpg")',
        },
      },
    },
  },
});

const ThemeContext = React.createContext("light");

function App() {
  const classes = useStyles();
  const [userTheme, setThemeName] = React.useState(
    localStorage.getItem("theme")
  );
  const setTheme = (name) => {
    setThemeName(name);
    localStorage.setItem("theme", name);
  };

  const themes = {
    Dark: darkTheme,
    Light: lightTheme,
    GreenYellowDark: GreenYellowDarkTheme,
    GreenYellowLight: GreenYellowLightTheme,
    YellowGreen: YellowGreenTheme,
    Red: RedTheme,
    GreyBlue: GreyBlueTheme,
    CamoDark: CamoDarkTheme,
    PurplePink: PurplePinkTheme,
    CamoDark: CamoDarkTheme,
    CamoLight: CamoLight,
    hll: hll,
  };

  const theme = process.env.REACT_APP_PUBLIC_BUILD
    ? hll
    : themes[userTheme]
    ? themes[userTheme]
    : lightTheme;

  return (
    <div className={"App " + classes.root}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ToastContainer />
        <Router>
          {!process.env.REACT_APP_PUBLIC_BUILD ? (
            <Header classes={classes} />
          ) : (
            ""
          )}
          <ScoreMenu classes={classes} />
          <Switch>
            
            <Route path="/" default exact>
              <LiveScore classes={classes} />
            </Route>
            <Route path="/gamescoreboard">
              <GamesScore classes={classes} />
            </Route>
            {!process.env.REACT_APP_PUBLIC_BUILD ? (
              <React.Fragment>
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
                <Route path="/player/:steamId64">
                  <Grid container>
                    <PlayerInfo classes={classes}/>
                  </Grid>
                </Route>
                <Route path="/settings">
                  <Grid container>
                    <Grid item sm={12} lg={6}>
                      <HLLSettings classes={classes} />
                    </Grid>
                    <Grid item sm={12} lg={6}>
                      <RconSettings
                        classes={classes}
                        theme={userTheme ? userTheme : "Light"}
                        themes={Object.keys(themes)}
                        setTheme={setTheme}
                      />
                    </Grid>
                  </Grid>
                </Route>
                <Route path="/services">
                  <Grid container>
                    <Grid item sm={12} lg={12}>
                      <ServicesList classes={classes} />
                    </Grid>
                  </Grid>
                </Route>
                <Route path="/logs">
                  <Grid container>
                    <Grid item sm={12} lg={12}>
                      <LogsHistory classes={classes} />
                    </Grid>
                  </Grid>
                </Route>
                <Route path="/combined_history">
                  <Grid container spacing={2}>
                    <Grid item sm={12}>
                      <Typography variant="h4">Players</Typography>
                    </Grid>
                    <Grid item sm={12}>
                      <PlayersHistory classes={classes} />
                    </Grid>
                    <Grid item sm={12}>
                      <Typography variant="h4">Historical Logs</Typography>
                    </Grid>
                    <Grid item sm={12}>
                      <LogsHistory classes={classes} />
                    </Grid>
                  </Grid>
                </Route>
              </React.Fragment>
            ) : (
              ""
            )}
          </Switch>

          <Footer classes={classes} />
        </Router>
      </ThemeProvider>
    </div>
  );
}

export default App;
