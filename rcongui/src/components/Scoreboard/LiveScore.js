import {
  AppBar,
  Link,
  Grid,
  Toolbar,
  Typography,
  makeStyles,
  LinearProgress,
  GridList,
  GridListTile,
  GridListTileBar,
} from "@material-ui/core";
import React from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS } from "immutable";
import moment from "moment";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import { useTheme } from "@material-ui/core/styles";
import Scores from "./Scores";
import map_to_pict from "./utils";
import { fade } from "@material-ui/core/styles/colorManipulator";
import { Link as RouterLink } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  padRight: {
    paddingRight: theme.spacing(1),
  },
  paper: {
    backgroundColor: theme.palette.background.paper,
  },
  transparentPaper: {
    backgroundColor: fade(theme.palette.background.paper, 0.6),
    borderRadius: "0px",
  },
  root: {
    display: "flex",
  },
  details: {
    display: "flex",
    flexDirection: "column",
  },
  content: {
    flex: "1 0 auto",
  },
  cover: {
    width: 200,
  },
  controls: {
    display: "flex",
    alignItems: "center",
    paddingLeft: theme.spacing(1),
    paddingBottom: theme.spacing(1),
  },
  playIcon: {
    height: 38,
    width: 38,
  },
  titleBar: {
    background:
      "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
  },
  titleBarTop: {
    background:
      "linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
  },
}));

const LiveSessionScore = ({ classes }) => (
  <LiveScore
    classes={classes}
    endpoint="live_scoreboard"
    title="LIVE SESSIONS"
    explainText={
      <React.Fragment>
        Only ingame players are shown. Stats are reset on disconnection, not per
        game, check the{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/livegamescore"
        >
          Live Game
        </Link>{" "}
        or{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/gamescoreboard"
        >
          Past games
        </Link>{" "}
        for historical data. Real deaths only are counted (e.g. not redeploys /
        revives)
      </React.Fragment>
    }
  />
);

const LiveGameScore = ({ classes }) => (
  <LiveScore
    classes={classes}
    endpoint="get_live_game_stats"
    title="CURRENT GAME"
    explainText={
      <React.Fragment>
        All players that are or were in the game are shown, check the{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/livescore"
        >
          Live Sessions
        </Link>{" "}for live stats accross several games
        or{" "}
        <Link
          variant="button"
          color="inherit"
          component={RouterLink}
          to="/gamescoreboard"
        >
          Past games
        </Link>{" "}
        for historical data. Real deaths only are counted (e.g. not redeploys /
        revives)
      </React.Fragment>
    }
  />
);

const LiveScore = ({ classes, endpoint, explainText, title }) => {
  const styles = useStyles();
  const [stats, setStats] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [refreshIntervalSec, setRefreshIntervalSec] = React.useState(10);
  const durationToHour = (val) =>
    new Date(val * 1000).toISOString().substr(11, 5);
  const scores = stats.get("stats", new iList());
  const lastRefresh = stats.get("snapshot_timestamp")
    ? moment.unix(stats.get("snapshot_timestamp")).format()
    : "N/A";

  const getData = () => {
    setIsLoading(true);
    console.log("Loading data");
    get(endpoint)
      .then((res) => showResponse(res, endpoint, false))
      .then((data) => {
        const map_ = fromJS(data.result);
        setStats(map_);
        setRefreshIntervalSec(map_.get("refresh_interval_sec", 10));
        // TODO add code to sync the refresh time with one of the server by checking the last refresh timestamp
      })
      .catch(handle_http_errors);
    get("public_info")
      .then((res) => showResponse(res, "public_info", false))
      .then((data) => setServerState(fromJS(data.result)))
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
  };

  React.useEffect(getData, []);

  React.useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(getData, refreshIntervalSec * 1000);
      return () => clearInterval(interval);
    }
  }, [isPaused, refreshIntervalSec]);

  document.title = serverState.get("name", "HLL Stats");
  let started = serverState.get("current_map", new Map()).get("start");
  started = started
    ? new Date(Date.now() - new Date(started * 1000))
        .toISOString()
        .substr(11, 8)
    : "N/A";

  return (
    <React.Fragment>
      <Grid container spacing={2} justify="center" className={classes.padding}>
        <Grid
          item
          xs={12}
          className={`${classes.doublePadding} ${styles.transparentPaper}`}
        >
          <Typography color="secondary" variant="h4">
            {serverState.get("name")}
          </Typography>
        </Grid>
        <Grid xs={12} md={10} lg={10} xl={8} className={classes.doublePadding}>
          <LiveHeader
            classes={classes}
            serverState={serverState}
            styles={styles}
            started={started}
            lastRefresh={lastRefresh}
            refreshIntervalSec={refreshIntervalSec}
            setPaused={setPaused}
            isPaused={isPaused}
            isLoading={isLoading}
            explainText={explainText}
            title={title}
          />
        </Grid>
      </Grid>
      <Grid container spacing={2} justify="center" className={classes.padding}>
        <Scores
          classes={classes}
          serverState={serverState}
          styles={styles}
          started={started}
          lastRefresh={lastRefresh}
          refreshIntervalSec={refreshIntervalSec}
          setPaused={setPaused}
          isPaused={isPaused}
          isLoading={isLoading}
          scores={scores}
          durationToHour={durationToHour}
          type="live"
        />
      </Grid>
    </React.Fragment>
  );
};

const LiveHeader = ({
  classes,
  serverState,
  styles,
  started,
  lastRefresh,
  refreshIntervalSec,
  setPaused,
  isPaused,
  isLoading,
  explainText,
  title
}) => {
  const theme = useTheme();
  const isXs = useMediaQuery(theme.breakpoints.down("sm"));
  const nextMapString = React.useMemo(() => {
    const [map, nbVotes] = serverState
      .get("vote_status")
      ?.get("winning_maps")
      ?.get(0) || ["", 0];
    const totalVotes = serverState.get("vote_status")?.get("total_votes");
    const nextMap = serverState.get("next_map");

    if (map === nextMap) {
      return `Nextmap ${nextMap} with ${nbVotes} out of ${totalVotes} votes`;
    }
    return `Nextmap: ${nextMap}`;
  }, [serverState]);

  return (
    <AppBar position="relative" style={{ minHeight: "144px" }}>
      <Toolbar className={classes.doublePadding}>
        <GridList cols={isXs ? 1 : 2}>
          <GridListTile>
            <Grid container spacing={1} className={styles.padRight}>
              <Grid item xs={12}>
                <Typography variant="h4" display="inline" color="inherit">
                  {title}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2">{explainText}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption">
                  Auto-refresh every {refreshIntervalSec} seconds:{" "}
                  <Link onClick={() => setPaused(!isPaused)} color="secondary">
                    {isPaused ? "click to unpause" : "click to pause"}
                  </Link>{" "}
                  - Last update: {lastRefresh}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <LinearProgress
                  style={{ visibility: isLoading ? "visible" : "hidden" }}
                  className={classes.grow}
                  color="secondary"
                />
              </Grid>
            </Grid>
          </GridListTile>
          <GridListTile>
            <img
              alt="Map"
              src={
                map_to_pict[
                  serverState
                    .get("current_map", new Map())
                    .get("just_name", "foy")
                ]
              }
            />
            <GridListTileBar
              className={styles.titleBarTop}
              title={serverState
                .get("current_map", new Map())
                .get("human_name", "N/A")}
              subtitle=""
              titlePosition="top"
            />
            <GridListTileBar
              className={styles.titleBarBottom}
              title={`Elapsed: ${started} - Players: ${serverState.get(
                "nb_players"
              )}`}
              subtitle={nextMapString}
              titlePosition="bottom"
            />
          </GridListTile>
        </GridList>
      </Toolbar>
    </AppBar>
  );
};

export { LiveGameScore, LiveSessionScore };
