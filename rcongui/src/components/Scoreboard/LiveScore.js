import {
  AppBar,
  Link,
  Grid,
  Toolbar,
  Typography,
  makeStyles,
  Paper,
  Card,
  CardContent,
  CardMedia,
  LinearProgress,
  Select,
  FormControl,
  InputLabel,
  MenuItem,
  Chip,
} from "@material-ui/core";
import React, { Fragment } from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS, set } from "immutable";
import moment from "moment";
import useMediaQuery from '@material-ui/core/useMediaQuery';
import { useTheme } from '@material-ui/core/styles';
import Scores from "./Scores";

const useStyles = makeStyles((theme) => ({
  paper: {
    backgroundColor: theme.palette.background.paper,
  },
  transparentPaper: {
    backgroundColor: theme.palette.background.paper,
    opacity: "0.6",
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
}));

const map_to_pict = {
  carentan: "maps/carentan.webp",
  foy: "maps/foy.webp",
  hill400: "maps/hill400.webp",
  hurtgenforest: "maps/hurtgen.webp",
  omahabeach: "maps/omaha.webp",
  purpleheartlane: "maps/omaha.webp",
  stmariedumont: "maps/smdm.webp",
  stmereeglise: "maps/sme.webp",
  utahbeach: "maps/utah.webp",
};

const LiveScore = ({ classes }) => {
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
    get("public_info")
      .then((res) => showResponse(res, "public_info", false))
      .then((data) => setServerState(fromJS(data.result)))
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
    get("live_scoreboard")
      .then((res) => showResponse(res, "livescore", false))
      .then((data) => setStats(fromJS(data.result)))
      .catch(handle_http_errors);
  };

  React.useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(getData, refreshIntervalSec * 1000);
      return () => clearInterval(interval);
    }
  }, [isPaused]);

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
}) => {
  const theme = useTheme();
  const isXs = useMediaQuery(theme.breakpoints.down('sm'));
  
  return (
    <AppBar position="relative" style={{ minHeight: "144px" }}>
      <Toolbar className={classes.doublePadding}>
        <Grid
          container
          justify={isXs ? "center" : "flex-start"}
          alignItems="flex-start"
          alignContent="flex=start"
        
          spacing={1}
        >
          <Grid
            item
            xs={12}
            sm={3}
            md={2}
            lg={2}
            alignContent="center"
            alignItems="center"
            justify="center"
            style={{
              flex: "grow",
              maxWidth: "220px",
              backgroundRepeat: "no-repeat",
              backgroundSize: "auto 150px",
              backgroundImage: `url(${
                map_to_pict[
                  serverState
                    .get("current_map", new Map())
                    .get("just_name", "foy")
                ]
              })`,
              minHeight: "150px",
            }}
          >
            <Paper elevation={0} className={styles.transparentPaper}>
              <Typography variant="caption">Current map</Typography>
            </Paper>
            <Paper elevation={0} className={styles.transparentPaper}>
              <Typography variant="h6">
                {serverState
                  .get("current_map", new Map())
                  .get("human_name", "N/A")}
              </Typography>
            </Paper>
            <Paper elevation={0} className={styles.transparentPaper}>
              <Typography variant="caption">Elapsed: {started}</Typography>
            </Paper>
            <Paper elevation={0} className={styles.transparentPaper}>
              <Typography variant="caption">
                Players: {serverState.get("nb_players")}
              </Typography>
            </Paper>
          </Grid>
          <Grid item sm={9} xs={12}>
            <Grid container spacing={1}>
              <Grid item xs={12}>
                {" "}
                <Typography variant="h4" display="inline" color="secondary">
                  LIVE STATS
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h4">{serverState.get("name")}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption">
                  Only ingame players are shown. Stats reset on disconnection, not per
                  game.Real deaths only (excludes redeploys / revives)
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption">
                  Last update: {lastRefresh} - Auto-refresh {refreshIntervalSec}{" "}
                  sec:{" "}
                  <Link onClick={() => setPaused(!isPaused)} color="secondary">
                    {isPaused ? "unpause" : "pause"}
                  </Link>
                </Typography>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <LinearProgress
              style={{ visibility: isLoading ? "visible" : "hidden" }}
              className={classes.grow}
              color="secondary"
            />
          </Grid>
        </Grid>
      </Toolbar>
    </AppBar>
  );
};


export default LiveScore;