import {
  AppBar,
  Link,
  Grid,
  Toolbar,
  Typography,
  makeStyles,
  Paper,
  LinearProgress,
  GridList,
  GridListTile,
  GridListTileBar,
  IconButton,
  StarBorderIcon,
  tileData,
  Button,
} from "@material-ui/core";
import useMediaQuery from '@material-ui/core/useMediaQuery';
import VisibilityIcon from '@material-ui/icons/Visibility';
import React, { Fragment } from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS, set, List } from "immutable";
import moment from "moment";
import { useTheme } from "@material-ui/core/styles";
import Scores from "./Scores";

const useStyles = makeStyles((theme) => ({
  singleLine: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
    backgroundColor: theme.palette.background.paper,
  },
  gridList: {
    flexWrap: "nowrap",
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: "translateZ(0)",
  },
  titleBar: {
    background:
      "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
  },
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

const GamesScore = ({ classes }) => {
  const styles = useStyles();
  const [stats, setStats] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [maps, setMaps] = React.useState(new List());
  const [mapsPage, setMapsPage] = React.useState(1)
  const [mapsPageSize, setMapsPageSize] = React.useState(30)
  const [refreshIntervalSec, setRefreshIntervalSec] = React.useState(10);
  const theme = useTheme()
  const md = useMediaQuery(theme.breakpoints.up('sm'));
  const lg = useMediaQuery(theme.breakpoints.up('md'));
  const xl = useMediaQuery(theme.breakpoints.up('lg'));
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
    get("get_scoreboard_maps")
      .then((res) => showResponse(res, "get_scoreboard_maps", false))
      .then((data) => setStats(fromJS(data.result)))
      .catch(handle_http_errors);
  };

  React.useEffect(() => {
    getData();
  }, []);

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
        <Grid xs={12} className={`${classes.doublePadding}`}>
          <div className={styles.singleLine}>
            <GridList cols={xl ? 8 : lg ? 6 : md ? 4 : 2} className={styles.gridList}>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13].map((e) => (
                <GridListTile>
                  <img src="maps/carentan.webp" />
                  <GridListTileBar
                    className={styles.titleBar}
                    title="Carentan"
                    subtitle="2020/04/18"
                    actionIcon={<IconButton color={e === 1 ? "secondary" : "inherit"}><VisibilityIcon/></IconButton>}
                  />
                </GridListTile>
              ))}
            </GridList>
          </div>
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

export default GamesScore;
