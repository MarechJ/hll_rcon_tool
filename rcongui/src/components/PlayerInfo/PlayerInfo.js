import {
  get,
  handle_http_errors,
  postData,
  showResponse,
} from "../../utils/fetchUtils";
import React from "react";
import {
  Avatar,
  Button,
  Grid,
  Link,
  makeStyles,
  Popover,
} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import { ExpandMore } from "@material-ui/icons";
import moment from "moment";
import MUIDataTable from "mui-datatables";
import { withRouter } from "react-router";
import "./PlayerInfo.css";
import { ChatContent } from "../ChatWidget";
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  padding: {
    padding: theme.spacing(1),
  },
}));

const NamePopOver = ({ names }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "name-popover" : undefined;
  const styles = useStyles();
  // TODO replace with a List with sublist so that on can copy past the names, also see at what time it was created + last seen
  return (
    <Grid item>
      <Button endIcon={<ExpandMore />} onClick={handleClick}>
        <Typography variant="h3">{names[0].name}</Typography>
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "center",
        }}
      >
        <Grid container className={styles.padding}>
          {names.map((name, index) => {
            return (
              <Grid item xs={12}>
                <Typography key={index} variant="body2">
                  {name.name}
                </Typography>
              </Grid>
            );
          })}
        </Grid>
      </Popover>
    </Grid>
  );
};

const Punishment = ({ punishments }) => {
  const [myRowPerPage, setRowPerPage] = React.useState(
    Number(window.localStorage.getItem("punishments_row_per_page")) || 50
  );
  const saveRowsPerPage = (rowPerPage) => {
    window.localStorage.setItem("punishments_row_per_page", rowPerPage);
    setRowPerPage(Number(rowPerPage));
  };
  const columns = [
    { name: "action_type", label: "Type" },
    { name: "reason", label: "Reason" },
    { name: "by", label: "By" },
    {
      name: "time",
      label: "Time",
      options: {
        customBodyRenderLite: (dataIndex) =>
          moment(punishments[dataIndex].time).format("ddd Do MMM HH:mm:ss"),
      },
    },
  ];

  const options = {
    filter: false,
    rowsPerPage: myRowPerPage,
    selectableRows: "none",
    rowsPerPageOptions: [10, 25, 50, 100, 250, 500, 1000],
    onChangeRowsPerPage: saveRowsPerPage,
  };

  return (
    <MUIDataTable
      title="Punishments"
      data={punishments}
      columns={columns}
      options={options}
    />
  );
};

const Is = ({ bool, text }) =>
  bool ? (
    <Grid item>
      <Typography color="secondary" variant="button">
        {text}
      </Typography>
    </Grid>
  ) : (
    ""
  );

const PlayerInfoFunc = ({ classes }) => {
  const { steamId64 } = useParams();
  const [created, setCreated] = React.useState("0");
  const [names, setNames] = React.useState([]);
  const [sessions, setSessions] = React.useState([]);
  const [sessionsCount, setSessionsCount] = React.useState(1086);
  const [totalPlaytimeSeconds, setTotalPlaytimeSeconds] =
    React.useState(4495950);
  const [currentPlaytimeSeconds, setCurrentPlaytimeSeconds] =
    React.useState(17455);
  const [receivedActions, setReceivedActions] = React.useState([]);
  const [penaltyCount, setPenaltyCount] = React.useState({
    TEMPBAN: 0,
    PERMABAN: 0,
    PUNISH: 0,
    KICK: 0,
  });
  const [blacklist, setBlacklist] = React.useState({
    is_blacklisted: false,
    reason: "",
    by: "",
  });
  const [flags, setFlags] = React.useState([]);
  const [watchlist, setWatchlist] = React.useState({});
  const [steaminfo, setSteaminfo] = React.useState({});
  const [perma, setPerma] = React.useState(false);
  const [temp, setTemp] = React.useState(false);
  const [vip, setVip] = React.useState(false);
  const [loaded, setLoaded] = React.useState(false);
  const [comments, setComments] = React.useState(undefined);

  /**
   * fetch bans that currently affect the steamId64
   * @param steamId64
   */
  const fetchPlayerBan = (steamId64) => {
    get(`get_ban?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_ban", false))
      .then((data) => {
        const temp = data.result.find((ban, index) => {
          return ban.type === "temp";
        });
        const perma = data.result.find((ban, index) => {
          return ban.type === "perma";
        });
        if (temp !== undefined) {
          setTemp(true);
        }
        if (perma !== undefined) {
          setPerma(true);
        }
      })
      .catch(handle_http_errors);
  };

  /**
   * fetch Player data
   * @param steamId64
   */
  const fetchPlayer = (steamId64) => {
    get(`player?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_user", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          
            setCreated(data.result.created)
            setNames(data.result.names)
            setSessions(data.result.sessions)
            setSessionsCount(data.result.sessions_count)
            setTotalPlaytimeSeconds(data.result.total_playtime_seconds)
            setCurrentPlaytimeSeconds(data.result.current_playtime_seconds)
            setReceivedActions(data.result.received_actions)
            setPenaltyCount(data.result.penalty_count)
            setBlacklist(data.result.blacklist)
            setFlags(data.result.flags)
            setWatchlist(data.result.watchlist)
            setSteaminfo(data.result.steaminfo)
            setLoaded(true)
        
        }
      })
      .catch(handle_http_errors);
  };

  const fetchPlayerComments = (steamId64) => {
    get(`get_player_comment?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_player_comments", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          setComments(data.result);
        }
      })
      .catch(handle_http_errors);
  };

  const handleNewComment = (newComment) => {
    postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
      steam_id_64: steamId64,
      comment: newComment,
    })
      .then((response) => {
        return showResponse(response, "post_player_comments", false);
      })
      .then(() => {
        fetchPlayerComments(steamId64);
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  };

  React.useEffect(() => {
    fetchPlayer(steamId64);
    fetchPlayerBan(steamId64);
    fetchPlayerComments(steamId64);
  }, [steamId64]);

  return (
    <Grid container className={classes.root}>
      {loaded ? (
        <Grid item sm={12} className={classes.marginTop}>
          <Grid container>
            <Grid item xl={2} lg={2} md={2} sm={3} xs={12}>
              <Grid
                container
                justify="center"
                alignContent="center"
                wrap="wrap"
                direction="column"
                spacing={3}
              >
                <Grid item>
                  <Avatar
                    style={{
                      height: "150px",
                      width: "150px",
                      fontSize: "5rem",
                    }}
                    variant="square"
                    className={classes.square}
                    src={steaminfo?.profile?.avatarfull}
                  >
                    {names[0]?.name[0].toUpperCase()}
                  </Avatar>
                </Grid>
                <Grid item>
                  <Typography variant="h6">Last connection</Typography>
                  <Typography>
                    {moment(
                      sessions[0]?.end ||
                        sessions[0]?.start
                    ).format("ddd Do MMM HH:mm:ss")}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h6">Total play time</Typography>
                  <Typography>
                    {moment
                      .duration(totalPlaytimeSeconds, "seconds")
                      .humanize()}
                  </Typography>
                </Grid>

                <Grid item>
                  <Typography variant="h6">Player penalties</Typography>
                  <Typography>
                    Perma ban: {penaltyCount.PERMABAN}
                  </Typography>
                  <Typography>
                    Temp ban: {penaltyCount.TEMPBAN}
                  </Typography>
                  <Typography>Kick: {penaltyCount.KICK}</Typography>
                  <Typography>
                    Punish: {penaltyCount.PUNISH}
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h6">
                    <Link
                      href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamId64}`}
                    >
                      Raw profile
                    </Link>
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xl={7} lg={7} md={7} sm={5} xs={12}>
              <Grid
                container
                spacing={3}
                justify="flex-start"
                alignItems="flex-start"
                alignContent="flex-start"
              >
                <Grid item sm={12}>
                  <Grid
                    container
                    justify="flex-start"
                    alignItems="flex-start"
                    alignContent="flex-start"
                  >
                    <NamePopOver names={names} />
                  </Grid>
                </Grid>
                <Grid item sm={12}>
                  <Grid container spacing={2}>
                    {[
                      [vip, "VIP"],
                      [perma, "IS PERMABANNED"],
                      [temp, "IS TEMPBANNED"],
                      [blacklist?.is_blacklisted, "IS BLACKLISTED"],
                    ].map((e) => (
                      <Is bool={e[0]} text={e[1]} />
                    ))}
                  </Grid>
                </Grid>
                <Grid item sm={12}>
                  <Punishment punishments={receivedActions} />
                </Grid>
              </Grid>
            </Grid>
            <Grid item xl={3} lg={3} md={3} sm={4} xs={12}>
              <Grid item xs={12}>
                <Typography variant="h3">Comments</Typography>
              </Grid>
              <Grid item xs={12}>
                <ChatContent
                  data={comments}
                  handleMessageSend={handleNewComment}
                />
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      ) : (
        <div>pending</div>
      )}
    </Grid>
  );
};

class PlayerInfo extends React.Component {
  _mounted = false;
  constructor(props) {
    super(props);
    this.state = {
      steam_id_64: "",
      created: "0",
      names: [],
      sessions: [],
      sessions_count: 1086,
      total_playtime_seconds: 4495950,
      current_playtime_seconds: 17455,
      received_actions: [],
      penalty_count: {
        TEMPBAN: 0,
        PERMABAN: 0,
        PUNISH: 0,
        KICK: 0,
      },
      blacklist: {
        is_blacklisted: false,
        reason: "",
        by: "",
      },
      flags: [],
      watchlist: {},
      steaminfo: {},
      perma: false,
      temp: false,
      vip: false,
      loaded: false,
      comments: undefined,
    };
    this.handleNewComment = this.handleNewComment.bind(this);
  }

  /**
   * fetch bans that currently affect the steamId64
   * @param steamId64
   */
  fetchPlayerBan(steamId64) {
    get(`get_ban?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_ban", false))
      .then((data) => {
        const temp = data.result.find((ban, index) => {
          return ban.type === "temp";
        });
        const perma = data.result.find((ban, index) => {
          return ban.type === "perma";
        });
        if (temp !== undefined && this._mounted) {
          this.setState({ temp: true });
        }
        if (perma !== undefined && this._mounted) {
          this.setState({ perma: true });
        }
      })
      .catch(handle_http_errors);
  }

  /**
   * fetch Player data
   * @param steamId64
   */
  fetchPlayer(steamId64) {
    get(`player?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_user", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          this.setState({
            created: data.result.created,
            names: data.result.names,
            sessions: data.result.sessions,
            sessions_count: data.result.sessions_count,
            total_playtime_seconds: data.result.total_playtime_seconds,
            current_playtime_seconds: data.result.current_playtime_seconds,
            received_actions: data.result.received_actions,
            penalty_count: data.result.penalty_count,
            blacklist: data.result.blacklist,
            flags: data.result.flags,
            watchlist: data.result.watchlist,
            steaminfo: data.result.steaminfo,
            loaded: true,
          });
        }
      })
      .catch(handle_http_errors);
  }

  fetchPlayerComments(steamId64) {
    get(`get_player_comment?steam_id_64=${steamId64}`)
      .then((response) => showResponse(response, "get_player_comments", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          this.setState({ comments: data.result });
        }
      })
      .catch(handle_http_errors);
  }

  handleNewComment(newComment) {
    const { steamId64 } = this.props.match.params;
    postData(`${process.env.REACT_APP_API_URL}post_player_comment`, {
      steam_id_64: steamId64,
      comment: newComment,
    })
      .then((response) => {
        return showResponse(response, "post_player_comments", false);
      })
      .then(() => {
        this.fetchPlayerComments(steamId64);
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  }

  componentDidMount() {
    this._mounted = true;
    const { steamId64 } = this.props.match.params;
    if (steamId64 !== undefined) {
      this.fetchPlayer(steamId64);
      this.fetchPlayerBan(steamId64);
      this.fetchPlayerComments(steamId64);
    }
  }

  componentWillUnmount() {
    this._mounted = false;
    this.setState = (state, callback) => {
      return;
    };
  }

  render() {
    // TODO Fix mobile responsiveness
    const { classes } = this.props;
    const { steamId64 } = this.props.match.params;

    return (
      <Grid container className={classes.root}>
        {this.state.loaded ? (
          <Grid item sm={12} className={classes.marginTop}>
            <Grid container>
              <Grid item xl={2} lg={2} md={2} sm={3} xs={12}>
                <Grid
                  container
                  justify="center"
                  alignContent="center"
                  wrap="wrap"
                  direction="column"
                  spacing={3}
                >
                  <Grid item>
                    <Avatar
                      style={{
                        height: "150px",
                        width: "150px",
                        fontSize: "5rem",
                      }}
                      variant="square"
                      className={classes.square}
                      src={this.state.steaminfo?.profile?.avatarfull}
                    >
                      {this.state.names[0]?.name[0].toUpperCase()}
                    </Avatar>
                  </Grid>
                  <Grid item>
                    <Typography variant="h6">Last connection</Typography>
                    <Typography>
                      {moment(
                        this.state.sessions[0]?.end ||
                          this.state.sessions[0]?.start
                      ).format("ddd Do MMM HH:mm:ss")}
                    </Typography>
                  </Grid>
                  <Grid item>
                    <Typography variant="h6">Total play time</Typography>
                    <Typography>
                      {moment
                        .duration(this.state.total_playtime_seconds, "seconds")
                        .humanize()}
                    </Typography>
                  </Grid>

                  <Grid item>
                    <Typography variant="h6">Player penalties</Typography>
                    <Typography>
                      Perma ban: {this.state.penalty_count.PERMABAN}
                    </Typography>
                    <Typography>
                      Temp ban: {this.state.penalty_count.TEMPBAN}
                    </Typography>
                    <Typography>
                      Kick: {this.state.penalty_count.KICK}
                    </Typography>
                    <Typography>
                      Punish: {this.state.penalty_count.PUNISH}
                    </Typography>
                  </Grid>
                  <Grid item>
                    <Typography variant="h6">
                      <Link
                        href={`${process.env.REACT_APP_API_URL}player?steam_id_64=${steamId64}`}
                      >
                        Raw profile
                      </Link>
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xl={7} lg={7} md={7} sm={5} xs={12}>
                <Grid
                  container
                  spacing={3}
                  justify="flex-start"
                  alignItems="flex-start"
                  alignContent="flex-start"
                >
                  <Grid item sm={12}>
                    <Grid
                      container
                      justify="flex-start"
                      alignItems="flex-start"
                      alignContent="flex-start"
                    >
                      <NamePopOver names={this.state.names} />
                    </Grid>
                  </Grid>
                  <Grid item sm={12}>
                    <Grid container spacing={2}>
                      {[
                        [this.state.vip, "VIP"],
                        [this.state.perma, "IS PERMABANNED"],
                        [this.state.temp, "IS TEMPBANNED"],
                        [
                          this.state.blacklist?.is_blacklisted,
                          "IS BLACKLISTED",
                        ],
                      ].map((e) => (
                        <Is bool={e[0]} text={e[1]} />
                      ))}
                    </Grid>
                  </Grid>
                  <Grid item sm={12}>
                    <Punishment punishments={this.state.received_actions} />
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xl={3} lg={3} md={3} sm={4} xs={12}>
                <Grid item xs={12}>
                  <Typography variant="h3">Comments</Typography>
                </Grid>
                <Grid item xs={12}>
                  <ChatContent
                    data={this.state.comments}
                    handleMessageSend={this.handleNewComment}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        ) : (
          <div>pending</div>
        )}
      </Grid>
    );
  }
}

export default withRouter(PlayerInfoFunc);
