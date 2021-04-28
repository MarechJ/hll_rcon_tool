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
import map_to_pict from './utils'


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
  titleBarTop: {
    background:
      "linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
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


const GamesScore = ({ classes }) => {
  const styles = useStyles();
  const [stats, setStats] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [maps, setMaps] = React.useState(new List());
  const [mapsPage, setMapsPage] = React.useState(1)
  const [mapsPageSize, setMapsPageSize] = React.useState(30)
  const [mapsTotal, setMapsTotal] = React.useState(0)
  const [refreshIntervalSec, setRefreshIntervalSec] = React.useState(10);
  const theme = useTheme()
  const md = useMediaQuery(theme.breakpoints.up('md'));
  const lg = useMediaQuery(theme.breakpoints.up('lg'));
  const xl = useMediaQuery(theme.breakpoints.up('xl'));
  const durationToHour = (val) =>
    new Date(val * 1000).toISOString().substr(11, 5);
  const scores = stats.get("stats", new iList());
  const lastRefresh = stats.get("snapshot_timestamp")
    ? moment.unix(stats.get("snapshot_timestamp")).format()
    : "N/A";

  moment.relativeTimeThreshold('m', 120)
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
      .then((data) => {
        if (data.failed) {return}
        setMapsPage(data.result.page)
        setMapsPageSize(data.result.page_size)
        setMapsTotal(data.result.total)
        setMaps(fromJS(data.result.maps))
      })
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
            <GridList cols={xl ? 8.5 : lg ? 5.5 : md ? 3.5 : 2.5} className={styles.gridList}>
              {maps.map((m) => {
                const start = moment(m.get("start"))
                const end = moment(m.get("end"))
                const duration = moment.duration(end - start)

                return <GridListTile>
                  <img src={map_to_pict[m.get("just_name")]} />
                  <GridListTileBar
                    className={styles.titleBarTop}
                    title={`${m.get("long_name")}`}
                    subtitle={`${duration.humanize()}`}
                    titlePosition="top"
                  />
                  <GridListTileBar
                    className={styles.titleBar}
                    title={`${start.format("dddd, MMM Do ")}`}
                    subtitle={`Started at: ${start.format("HH:mm")}`}
                    actionIcon={<IconButton color="inherit"><VisibilityIcon/></IconButton>}
                  />
                </GridListTile>
              })}
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
