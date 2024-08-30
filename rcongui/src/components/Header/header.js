import React from "react";
import Grid from "@material-ui/core/Grid";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Link from "@material-ui/core/Link";
import { Link as RouterLink } from "react-router-dom";
import Button from "@material-ui/core/Button";
import ServerStatus from "./server-status";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import { navMenus } from "./nav-data";
import { LoginBox } from "./login";
import { Box, createStyles, makeStyles } from "@material-ui/core";

const useStyles = makeStyles((theme) =>
  createStyles({
    root: {
      display: "flex",
      flexGrow: 1,
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "start",
      padding: theme.spacing(0.25),
      minHeight: 0,
      gap: theme.spacing(0.25),
      [theme.breakpoints.up("md")]: {
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center",
        gap: theme.spacing(2),
        padding: theme.spacing(0.5),
      },
    },
    nav: {
      display: "flex",
      flexDirection: "row",
      flexGrow: 1,
      justifyContent: "space-between",
    },
  })
);

class LoginBox extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      username: "",
      password: "",
      open: false,
      isLoggedIn: false,
      interval: null,
    };

    this.login = this.login.bind(this);
    this.logout = this.logout.bind(this);
    this.isLoggedIn = this.isLoggedIn.bind(this);
  }

  componentDidMount() {
    const f = throttle(this.isLoggedIn, 1000 * 55);
    this.isLoggedIn();
    this.setState({
      interval: setInterval(f, 1000 * 60),
    });
  }

  componentWillUnmount() {
    clearInterval(this.state.interval);
  }

  isLoggedIn() {
    return get("is_logged_in")
      .then((response) => response.json())
      .then((res) => this.setState({ isLoggedIn: res.result.authenticated }))
      .catch(handle_http_errors);
  }

  login() {
    return postData(`${process.env.REACT_APP_API_URL}login`, {
      username: this.state.username,
      password: this.state.password,
    })
      .then((res) => showResponse(res, `login ${this.state.username}`, true))
      .then((data) => {
        if (data.failed === false) {
          this.setState({ isLoggedIn: true, open: false, password: "" });
        }
      })
      .catch(handle_http_errors);
  }

  logout() {
    return get("logout")
      .then(this.setState({ isLoggedIn: false }))
      .catch(handle_http_errors);
  }

  render() {
    const { open, username, password, isLoggedIn } = this.state;

    return (
      <React.Fragment>
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          onClick={() =>
            isLoggedIn === true ? this.logout() : this.setState({ open: true })
          }
          to="#"
        >
          {isLoggedIn === true ? "Logout" : "Login"}
        </Link>
        <LoginModal
          open={open}
          handleClose={() => this.setState({ open: false })}
          login={this.login}
          password={password}
          setPassword={(password) => this.setState({ password: password })}
          username={username}
          setUsername={(username) => this.setState({ username: username })}
        />
      </React.Fragment>
    );
  }
}

const Header = () => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const localClasses = useStyles();

  const handleOpenMenu = (name) => (event) => {
    setOpenedMenu({
      ...openedMenu,
      [name]: true,
    });
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = (name) => () => {
    setOpenedMenu({
      ...openedMenu,
      [name]: false,
    });
    setAnchorEl(null);
  };

  return (
    <Grid container >
      <div >
        <AppBar position="static" elevation={0} >
          <Toolbar >
            <Grid container>
              <Grid item xs={12}>
                <Grid container alignContent="flex-start" alignItems="center">
                  <Grid item>
                    <ServerStatus  />
                  </Grid>
                  <Grid item ></Grid>
                  <Grid item >
                    <nav >
                      <Link
                        variant="button"
                        color="inherit"
                        
                        onClick={(e) => setAnchorElLive(e.currentTarget)}
                      >
                        Live
                      </Link>
                      <Menu
                        id="live-menu"
                        anchorEl={anchorElLive}
                        keepMounted
                        open={Boolean(anchorElLive)}
                        onClose={() => setAnchorElLive(null)}
                      >
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to="/"
                        >
                          <MenuItem onClick={() => setAnchorElLive(null)}>
                            Live
                          </MenuItem>
                        </Link>
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to="/gameview"
                        >
                          <MenuItem onClick={() => setAnchorElLive(null)}>
                            Game view
                          </MenuItem>
                        </Link>
                      </Menu>
                      <Link
                        variant="button"
                        color="inherit"
                        
                        onClick={handleClick}
                      >
                        History
                      </Link>
                      <Menu
                        id="history-menu"
                        anchorEl={anchorEl}
                        keepMounted
                        open={Boolean(anchorEl)}
                        onClose={handleClose}
                      >
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/history"
                        >
                          <MenuItem onClick={handleClose}>Players</MenuItem>
                        </Link>
                        <Link color="inherit" component={RouterLink} to="/logs">
                          <MenuItem onClick={handleClose}>Logs</MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/combined_history"
                        >
                          <MenuItem onClick={handleClose}>Combined</MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/blacklists"
                        >
                          <MenuItem onClick={handleClose}>Blacklists</MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/auditlogs"
                        >
                          <MenuItem onClick={handleClose}>Audit Logs</MenuItem>
                        </Link>
                      </Menu>
                      <Link
                        variant="button"
                        color="inherit"
                        
                        onClick={(e) => {
                          setAnchorElSettings(e.currentTarget);
                        }}
                      >
                        Settings
                      </Link>
                      <Menu
                        id="settings-menu"
                        anchorEl={anchorElSettings}
                        keepMounted
                        open={Boolean(anchorElSettings)}
                        onClose={() => setAnchorElSettings(null)}
                      >
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/settings"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Settings
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/audit-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Audit Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/admin-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Admin Ping Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/watchlist-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Watchlist Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/camera-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Camera Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/chat-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Chat Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/kill-webhooks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Kill/Teamkills Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/automod-level"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Level Auto Mod
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/automod-no-leader"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            No Leader Auto Mod
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/automod-seeding"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Seeding Auto Mod
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/automod-solo-tank"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            No Solo Tank Auto Mod
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/rcon-gameserver"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            RCON Game Server Connection
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/rcon-server"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            CRCON Settings
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/chat-commands"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Chat Commands
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/scorebot"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Scorebot
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/steam"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Steam API
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/vac-gamebans"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            VAC/Game Bans
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/tk-ban"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            TK Ban On Connect
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/name-kicks"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Name Kicks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/log-lines"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Log Line Webhooks
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/expired-vip"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Expired VIP
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/gtx-server-name-change"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            GTX Server Name Change
                          </MenuItem>
                        </Link>
                        <Link
                          color="inherit"
                          component={RouterLink}
                          to="/settings/log-stream"
                        >
                          <MenuItem onClick={() => setAnchorElSettings(null)}>
                            Log Stream
                          </MenuItem>
                        </Link>
                      </Menu>
                      <Link
                        variant="button"
                        color="inherit"
                        
                        onClick={(e) => setAnchorElScores(e.currentTarget)}
                      >
                        Stats
                      </Link>
                      <Menu
                        id="score-menu"
                        anchorEl={anchorElScores}
                        keepMounted
                        open={Boolean(anchorElScores)}
                        onClose={() => setAnchorElScores(null)}
                      >
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to="/livescore"
                        >
                          <MenuItem onClick={() => setAnchorElScores(null)}>
                            Live Sessions
                          </MenuItem>
                        </Link>
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to="/livegamescore"
                        >
                          <MenuItem onClick={() => setAnchorElScores(null)}>
                            Live Game
                          </MenuItem>
                        </Link>
                        <Link
                          variant="button"
                          color="inherit"
                          component={RouterLink}
                          to="/gamescoreboard"
                        >
                          <MenuItem onClick={() => setAnchorElScores(null)}>
                            Games
                          </MenuItem>
                        </Link>
                        {/* <Link
                          variant="button"
                          color="inherit"
                          
                          component={RouterLink}
                          to="/server"
                        >
                          <MenuItem onClick={() => setAnchorElScores(null)}>
                            Server
                          </MenuItem>
                        </Link> */}
                      </Menu>

                      <LoginBox  component={RouterLink} />
                    </nav>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Toolbar>
        </AppBar>
      </div>
    </Grid>
  );
};

export default Header;
