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
import ServerStatsPage from "./components/ServerStats";
import GameView from "./components/GameView";
import AuditLog from "./components/AuditLog";
import {
  AdminPingWebhooks,
  AuditWebhooks,
  WatchlistWebhooks,
  CameraWebhooks,
  ChatWebhooks,
  KillWebhooks,
  LogLineWebhooks,
} from "./components/UserSettings/webHooks";
import {
  LevelAutoMod,
  NoLeaderAutoMod,
  SeedingAutoMod,
  NoSoloTankAutoMod,
} from "./components/UserSettings/autoMods";
import {
  RconConnectionSettings,
  RconServerSettings,
  Scorebot,
  SteamAPI,
  VacGameBans,
  TeamKillBanOnConnect,
  NameKicks,
  ExpiredVIP,
  GTXNameChange
} from "./components/UserSettings/miscellaneous";

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
            <Route path="/auditlogs" exact>
              <AuditLog classes={classes} />
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
                <Route path="/settings/">
                  <Switch>
                    <Route path="/settings/settings">
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
                    <Route path="/settings/audit-webhooks">
                      <Grid container spacing={2}>
                        <AuditWebhooks
                          description="Audit Webhooks"
                          getEndpoint="get_audit_discord_webhooks_config"
                          setEndpoint="set_audit_discord_webhooks_config"
                          validateEndpoint="validate_audit_discord_webhooks_config"
                          describeEndpoint="describe_audit_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/admin-webhooks">
                      <Grid container spacing={2}>
                        <AdminPingWebhooks
                          description="Admin Ping Webhooks"
                          getEndpoint="get_admin_pings_discord_webhooks_config"
                          setEndpoint="set_admin_pings_discord_webhooks_config"
                          validateEndpoint="validate_admin_pings_discord_webhooks_config"
                          describeEndpoint="describe_admin_pings_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/watchlist-webhooks">
                      <Grid container spacing={2}>
                        <WatchlistWebhooks
                          description="Watchlist Webhooks"
                          getEndpoint="get_watchlist_discord_webhooks_config"
                          setEndpoint="set_watchlist_discord_webhooks_config"
                          validateEndpoint="validate_watchlist_discord_webhooks_config"
                          describeEndpoint="describe_watchlist_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/camera-webhooks">
                      <Grid container spacing={2}>
                        <CameraWebhooks
                          description="Camera Webhooks"
                          getEndpoint="get_camera_discord_webhooks_config"
                          setEndpoint="set_camera_discord_webhooks_config"
                          validateEndpoint="validate_camera_discord_webhooks_config"
                          describeEndpoint="describe_camera_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/chat-webhooks">
                      <Grid container spacing={2}>
                        <ChatWebhooks
                          description="Chat Webhooks"
                          getEndpoint="get_chat_discord_webhooks_config"
                          setEndpoint="set_chat_discord_webhooks_config"
                          validateEndpoint="validate_chat_discord_webhooks_config"
                          describeEndpoint="describe_chat_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/kill-webhooks">
                      <Grid container spacing={2}>
                        <KillWebhooks
                          description="Kill/Team Kill Webhooks"
                          getEndpoint="get_kills_discord_webhooks_config"
                          setEndpoint="set_kills_discord_webhooks_config"
                          validateEndpoint="validate_kills_discord_webhooks_config"
                          describeEndpoint="describe_kills_discord_webhooks_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/log-lines">
                      <Grid container spacing={2}>
                        <LogLineWebhooks
                          description="Log Line Webhooks"
                          getEndpoint="get_log_line_webhook_config"
                          setEndpoint="set_log_line_webhook_config"
                          validateEndpoint="validate_log_line_webhook_config"
                          describeEndpoint="describe_log_line_webhook_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/automod-level">
                      <Grid container spacing={2}>
                        <LevelAutoMod
                          description="Level Auto Mod"
                          getEndpoint="get_auto_mod_level_config"
                          setEndpoint="set_auto_mod_level_config"
                          validateEndpoint="validate_auto_mod_level_config"
                          describeEndpoint="describe_auto_mod_level_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/automod-no-leader">
                      <Grid container spacing={2}>
                        <NoLeaderAutoMod
                          description="No Leader Auto Mod"
                          getEndpoint="get_auto_mod_no_leader_config"
                          setEndpoint="set_auto_mod_no_leader_config"
                          validateEndpoint="validate_auto_mod_no_leader_config"
                          describeEndpoint="describe_auto_mod_no_leader_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/automod-seeding">
                      <Grid container spacing={2}>
                        <SeedingAutoMod
                          description="Seeding Auto Mod"
                          getEndpoint="get_auto_mod_seeding_config"
                          setEndpoint="set_auto_mod_seeding_config"
                          validateEndpoint="validate_auto_mod_seeding_config"
                          describeEndpoint="describe_auto_mod_seeding_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/automod-solo-tank">
                      <Grid container spacing={2}>
                        <NoSoloTankAutoMod
                          description="No Solo Tank Auto Mod"
                          getEndpoint="get_auto_mod_solo_tank_config"
                          setEndpoint="set_auto_mod_solo_tank_config"
                          validateEndpoint="validate_auto_mod_solo_tank_config"
                          describeEndpoint="describe_auto_mod_solo_tank_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/rcon-gameserver">
                      <Grid container spacing={2}>
                        <RconConnectionSettings
                          description="Game Server Connection Settings"
                          getEndpoint="get_rcon_connection_settings_config"
                          setEndpoint="set_rcon_connection_settings_config"
                          validateEndpoint="validate_rcon_connection_settings_config"
                          describeEndpoint="describe_rcon_connection_settings_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/rcon-server">
                      <Grid container spacing={2}>
                        <RconServerSettings
                          description="General CRCON Settings"
                          getEndpoint="get_rcon_server_settings_config"
                          setEndpoint="set_rcon_server_settings_config"
                          validateEndpoint="validate_rcon_server_settings_config"
                          describeEndpoint="describe_rcon_server_settings_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/scorebot">
                      <Grid container spacing={2}>
                        <Scorebot
                          description="Scorebot"
                          getEndpoint="get_scorebot_config"
                          setEndpoint="set_scorebot_config"
                          validateEndpoint="validate_scorebot_config"
                          describeEndpoint="describe_scorebot_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/steam">
                      <Grid container spacing={2}>
                        <SteamAPI
                          description="Steam API"
                          getEndpoint="get_steam_config"
                          setEndpoint="set_steam_config"
                          validateEndpoint="validate_steam_config"
                          describeEndpoint="describe_steam_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/vac-gamebans">
                      <Grid container spacing={2}>
                        <VacGameBans
                          description="VAC/Game Bans"
                          getEndpoint="get_vac_game_bans_config"
                          setEndpoint="set_vac_game_bans_config"
                          validateEndpoint="validate_vac_game_bans_config"
                          describeEndpoint="describe_vac_game_bans_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/tk-ban">
                      <Grid container spacing={2}>
                        <TeamKillBanOnConnect
                          description="TK Ban On Connect"
                          getEndpoint="get_tk_ban_on_connect_config"
                          setEndpoint="set_tk_ban_on_connect_config"
                          validateEndpoint="validate_tk_ban_on_connect_config"
                          describeEndpoint="describe_tk_ban_on_connect_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/name-kicks">
                      <Grid container spacing={2}>
                        <NameKicks
                          description="Name Kicks"
                          getEndpoint="get_name_kick_config"
                          setEndpoint="set_name_kick_config"
                          validateEndpoint="validate_name_kick_config"
                          describeEndpoint="describe_name_kick_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/Message-on-connect">
                      <Grid container spacing={2}>
                        <MessageOnConnect
                          description="Message on connect"
                          getEndpoint="get_message_on_connect_config"
                          setEndpoint="set_message_on_connect_config"
                          validateEndpoint="validate_message_on_connect_config"
                          describeEndpoint="describe_message_on_connect_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/expired-vip">
                      <Grid container spacing={2}>
                        <ExpiredVIP
                          description="Expired VIP"
                          getEndpoint="get_expired_vip_config"
                          setEndpoint="set_expired_vip_config"
                          validateEndpoint="validate_expired_vip_config"
                          describeEndpoint="describe_expired_vip_config"
                        />
                      </Grid>
                    </Route>
                    <Route path="/settings/gtx-server-name-change">
                      <Grid container spacing={2}>
                        <GTXNameChange
                          description="GTX Server Name Change"
                          getEndpoint="get_server_name_change_config"
                          setEndpoint="set_server_name_change_config"
                          validateEndpoint="validate_server_name_change_config"
                          describeEndpoint="describe_server_name_change_config"
                        />
                      </Grid>
                    </Route>
                  </Switch>
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
                <Route path="/server">
                  <Grid container>
                    <Grid item sm={12} lg={12}>
                      <ServerStatsPage classes={classes} />
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
