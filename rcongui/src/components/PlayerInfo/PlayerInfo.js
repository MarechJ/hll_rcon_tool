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
  Popover,
} from "@mui/material";
import Typography from "@mui/material/Typography";
import { ExpandMore } from "@mui/icons-material";
import moment from "moment";
import MUIDataTable from "mui-datatables";
import { withRouter } from "react-router";
import { ChatContent } from "../ChatWidget";
import MessageHistory from "../MessageHistory";
import { toast } from "react-toastify";
import { useParams } from "react-router-dom";
import CollapseCard from "../collapseCard";
import makePlayerProfileUrl from "../../utils/makePlayerProfileUrl";

// return a label for steam and windows ids types
const getLinkLabel = (id) => {
  if (id.length === 17) {
    // valid steam id is 17 digits...
    return "Steam";
  } else {
    // xbox gamertags are unique and cost $$ to change...
    // otherwise assume it's a T17 guid and return
    // a url to https://xboxgamertag.com/search/ name
    return "xboxgamertag.com";
  }
};

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
  // TODO replace with a List with sublist so that on can copy past the names, also see at what time it was created + last seen
  return (
    <Grid item>
      <Button endIcon={<ExpandMore />} onClick={handleClick}>
        <Typography variant="h3">{names.length ? names[0].name : "Player has no recorded names"}</Typography>
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
        <Grid container>
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
          moment
            .utc(punishments[dataIndex].time)
            .local()
            .format("ddd Do MMM HH:mm:ss"),
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

const PlayerInfo = () => {
  const { playerId } = useParams();
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
  const [isBlacklisted, setIsBlacklisted] = React.useState(false);
  const [flags, setFlags] = React.useState([]);
  const [watchlist, setWatchlist] = React.useState({});
  const [steaminfo, setSteaminfo] = React.useState({});
  const [perma, setPerma] = React.useState(false);
  const [temp, setTemp] = React.useState(false);
  const [vip, setVip] = React.useState(false);
  const [loaded, setLoaded] = React.useState(false);
  const [comments, setComments] = React.useState(undefined);
  const [messages, setMessages] = React.useState(undefined);

  /**
   * fetch bans that currently affect the playerId
   * @param playerId
   */
  const fetchPlayerBan = (playerId) => {
    get(`get_ban?player_id=${playerId}`)
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
   * @param playerId
   */
  const fetchPlayer = (playerId) => {
    get(`get_player_profile?player_id=${playerId}`)
      .then((response) => showResponse(response, "get_player_profile", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          setCreated(data.result.created);
          setNames(data.result.names);
          setSessions(data.result.sessions);
          setSessionsCount(data.result.sessions_count);
          setTotalPlaytimeSeconds(data.result.total_playtime_seconds);
          setCurrentPlaytimeSeconds(data.result.current_playtime_seconds);
          setReceivedActions(data.result.received_actions);
          setPenaltyCount(data.result.penalty_count);
          setIsBlacklisted(data.result.is_blacklisted);
          setFlags(data.result.flags);
          setWatchlist(data.result.watchlist);
          setSteaminfo(data.result.steaminfo);
          setLoaded(true);
        }
      })
      .catch(handle_http_errors);
  };

  const fetchMessages = (playerId) => {
    get(`get_player_messages?player_id=${playerId}`)
      .then((response) => showResponse(response, "get_player_messages", false))
      .then((data) => {
        if (
          data.result !== undefined &&
          data.result !== null &&
          Object.keys(data.result).length !== 0
        ) {
          setMessages(data.result);
        }
      })
      .catch(handle_http_errors);
  };

  const fetchPlayerComments = (playerId) => {
    get(`get_player_comments?player_id=${playerId}`)
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
      player_id: playerId,
      comment: newComment,
    })
      .then((response) => {
        return showResponse(response, "post_player_comment", false);
      })
      .then(() => {
        fetchPlayerComments(playerId);
      })
      .catch((error) => toast.error("Unable to connect to API " + error));
  };

  React.useEffect(() => {
    fetchPlayer(playerId);
    fetchPlayerBan(playerId);
    fetchMessages(playerId);
    fetchPlayerComments(playerId);
  }, [playerId]);

  return (
    (<Grid container >
      {loaded ? (
        <Grid item sm={12} >
          <Grid container spacing={2}>
            <Grid item xl={2} lg={2} md={2} sm={3} xs={12}>
              <Grid
                container
                justifyContent="center"
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
                    
                    src={steaminfo?.profile?.avatarfull}
                  >
                    {names[0]?.name[0].toUpperCase()}
                  </Avatar>
                </Grid>
                <Grid item>
                  <Typography variant="h6">
                    <Link href={makePlayerProfileUrl(playerId, names[0]?.name)}>
                      {getLinkLabel(playerId)} Profile
                    </Link>
                  </Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h6">Last connection</Typography>
                  <Typography>
                    {moment(sessions[0]?.end || sessions[0]?.start).format(
                      "ddd Do MMM HH:mm:ss"
                    )}
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
                  <Typography>Perma ban: {penaltyCount.PERMABAN}</Typography>
                  <Typography>Temp ban: {penaltyCount.TEMPBAN}</Typography>
                  <Typography>Kick: {penaltyCount.KICK}</Typography>
                  <Typography>Punish: {penaltyCount.PUNISH}</Typography>
                </Grid>
                <Grid item>
                  <Typography variant="h6">
                    <Link
                      href={`${process.env.REACT_APP_API_URL}get_player_profile?player_id=${playerId}`}
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
                justifyContent="flex-start"
                alignItems="flex-start"
                alignContent="flex-start"
              >
                <Grid item sm={12}>
                  <Grid
                    container
                    justifyContent="flex-start"
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
                      [isBlacklisted, "IS BLACKLISTED"],
                      [perma, "IS PERMABANNED"],
                      [temp, "IS TEMPBANNED"],
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
            <Grid item xl={3} xs={12}>
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <CollapseCard title="Comments" startOpen>
                    <ChatContent
                      data={comments}
                      handleMessageSend={handleNewComment}
                    />
                  </CollapseCard>
                </Grid>
                <Grid item xs={12}>
                  <CollapseCard
                    title="Message History"
                    startOpen
                  >
                    <MessageHistory data={messages} />
                  </CollapseCard>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      ) : (
        <div>pending</div>
      )}
    </Grid>)
  );
};

export default withRouter(PlayerInfo);
