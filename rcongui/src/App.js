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
import { HashRouter, Route, Switch, BrowserRouter } from "react-router-dom";
import LogsHistory from "./components/LogsHistory";
import { createMuiTheme } from "@material-ui/core/styles";
import PlayersHistory from "./components/PlayersHistory";
import Header, { Footer } from "./components/Header";
import RconSettings from "./components/RconSettings";
import ServicesList from "./components/Services";
import { Typography } from "@material-ui/core";
import ScoreMenu from "./components/Scoreboard/ScoreMenu";
import GamesScore from "./components/Scoreboard/GamesScore";
import PlayerInfo from "./components/PlayerInfo";
import {
  LiveGameScore,
  LiveSessionScore,
} from "./components/Scoreboard/LiveScore";
import ServerInfo from "./components/Embeds/ServerInfo";
import GameView from "./components/GameView"

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
            direction === "column-reverse"
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
  editor: "vs-dark",
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
  editor: "vs-dark",
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

const GreyBlueDarkTheme = createMuiTheme({
  editor: "vs-dark",
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
  editor: "vs-dark",
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
      contrastText: "#fff",
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
    MuiChip: {
      deleteIcon: {
        color: "#212121",
      },
    },
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

const hllNoBg = createMuiTheme({
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
      contrastText: "#fff",
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
    MuiChip: {
      deleteIcon: {
        color: "#212121",
      },
    },
  },
});

function App() {
  const [isEmbed, setIsEmbed] = React.useState(false);
  const [userTheme, setThemeName] = React.useState(
    localStorage.getItem("theme")
  );
  const setTheme = (name) => {
    setThemeName(name);
    localStorage.setItem("theme", name);
  };

  React.useEffect(() => {
    const serarchParams = new URLSearchParams(window.location.search);

    setIsEmbed(serarchParams.has("embed"));
  }, [window.location.search]);

  const themes = {
    Dark: darkTheme,
    Light: lightTheme,
    GreenYellowDark: GreenYellowDarkTheme,
    GreenYellowLight: GreenYellowLightTheme,
    YellowGreen: YellowGreenTheme,
    Red: RedTheme,
    GreyBlueDark: GreyBlueDarkTheme,
    CamoDark: CamoDarkTheme,
    PurplePink: PurplePinkTheme,
    CamoLight: CamoLight,
    hll: hll,
  };

  const theme = process.env.REACT_APP_PUBLIC_BUILD
    ? isEmbed
      ? hllNoBg
      : hll
    : themes[userTheme]
    ? themes[userTheme]
    : lightTheme;
  const classes = useStyles();

  const Router = isEmbed ? BrowserRouter : HashRouter;

  return (
    <div className={"App " + classes.root}>
      <ThemeProvider theme={theme}>
        {isEmbed ? "" : <CssBaseline />}
        <ToastContainer />
        <Router>
          {isEmbed ? (
            ""
          ) : !process.env.REACT_APP_PUBLIC_BUILD ? (
            <Header classes={classes} />
          ) : (
            <ScoreMenu classes={classes} />
          )}

          <Switch>
          <Route path="/gameview" exact>
              <GameView classes={classes} />
            </Route>
            <Route path="/serverinfo" exact>
              <ServerInfo classes={classes} />
            </Route>
            <Route
              path="/livescore"
              default={process.env.REACT_APP_PUBLIC_BUILD}
              exact
            >
              <LiveSessionScore classes={classes} />
            </Route>
            <Route
              path={process.env.REACT_APP_PUBLIC_BUILD ? "/" : "/livegamescore"}
              default={process.env.REACT_APP_PUBLIC_BUILD}
              exact
            >
              <LiveGameScore classes={classes} />
            </Route>
            <Route path="/gamescoreboard/:slug">
              <GamesScore classes={classes} />
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
                    <PlayerInfo classes={classes} />
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
                        themeName={userTheme ? userTheme : "Light"}
                        themeNames={Object.keys(themes)}
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
          {isEmbed ? "" : <Footer classes={classes} />}
        </Router>
      </ThemeProvider>
    </div>
  );
}

export default App;
