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
  Box,
} from "@material-ui/core";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import VisibilityIcon from "@material-ui/icons/Visibility";
import React, { Fragment } from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS, set, List } from "immutable";
import moment from "moment";
import { useTheme } from "@material-ui/core/styles";
import Scores from "./Scores";
import map_to_pict from "./utils";

const useStyles = makeStyles((theme) => ({
  singleLine: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
  },
  clickable: {
    cursor: "pointer"
  },
  gridList: {
    flexWrap: "nowrap",
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: "translateZ(0)",
  },
  selectedMap: {
    color: theme.palette.secondary.main
  },
  titleBar: {
    background:
      "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
  },
  titleBarTop: {
    background:
      "linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)",
  },
  selectedTitleBar: {
    background:
      "linear-gradient(to top, rgba(244,123,0,0.3) 0%, rgba(0,0,0,0)  70%, rgba(0,0,0,0) 100%)",
  },
  selectedTitleBarTop: {
    background:
      "linear-gradient(to bottom, rgba(244,123,0,0.3) 0%, rgba(0,0,0,0) 70%, rgba(0,0,0,0) 100%)",
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
  const [scores, setScores] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [maps, setMaps] = React.useState(new List());
  const [mapsPage, setMapsPage] = React.useState(1);
  const [mapsPageSize, setMapsPageSize] = React.useState(30);
  const [mapsTotal, setMapsTotal] = React.useState(0);
  const [currentMapId, setCurrentMapId] = React.useState(null);
  const [refreshIntervalSec, setRefreshIntervalSec] = React.useState(10);
  const theme = useTheme();
  const md = useMediaQuery(theme.breakpoints.up("md"));
  const lg = useMediaQuery(theme.breakpoints.up("lg"));
  const xl = useMediaQuery(theme.breakpoints.up("xl"));
  const durationToHour = (val) =>
    new Date(val * 1000).toISOString().substr(11, 5);

  const lastRefresh = scores.get("snapshot_timestamp")
    ? moment.unix(scores.get("snapshot_timestamp")).format()
    : "N/A";

  moment.relativeTimeThreshold("m", 120);
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
        if (data.failed) {
          return;
        }
        setMapsPage(data.result.page);
        setMapsPageSize(data.result.page_size);
        setMapsTotal(data.result.total);
        setMaps(fromJS(data.result.maps));
        if (data.result.maps && currentMapId === null) {
          setCurrentMapId(data.result.maps[0].id);
        }
      })
      .catch(handle_http_errors);
  };

  const getStatsFromMap = React.useMemo(() => {
    if (!currentMapId) { return }
    get(`get_map_scoreboard?map_id=${currentMapId}`)
      .then((res) => showResponse(res, "get_map_scoreboard", false))
      .then((data) =>
        data.result ? setScores(fromJS(data.result.player_stats)) : ""
      )
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
  }, [currentMapId]);

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
      <Grid container spacing={1} justify="center" className={classes.padding}>
        {!maps.size ? (
          <Grid item className={styles.paper}>
            <Typography variant="h2">No games recorded yet</Typography>
          </Grid>
        ) : (
          <Grid item>
          <Typography variant="caption">Select a game</Typography>
        </Grid>
        )}
        <Grid xs={12} className={`${classes.doublePadding}`}>
          <div className={styles.singleLine}>
            <GridList
              cols={
                xl
                  ? Math.min(maps.size, 8.5)
                  : lg
                  ? Math.min(maps.size, 5.5)
                  : md
                  ? Math.min(maps.size, 3.5)
                  : Math.min(maps.size, 2.5)
              }
              className={styles.gridList}
            >
              {maps.map((m) => {
                const start = moment(m.get("start") + 'Z');
                const end = moment(m.get("end") + 'Z');
                const duration = moment.duration(end - start);
                const isSelected = (isReturn, isNotReturn) => m.get("id") === currentMapId ? isReturn : isNotReturn

                return (
                  <GridListTile
                    class={styles.clickable}
                    onClick={() => setCurrentMapId(m.get("id"))}
                    key={`${m.get("name")}${m.get("start")}${m.get("end")}`}
                  >
                    <img src={map_to_pict[m.get("just_name")]} />
                    
                    <GridListTileBar
                      className={isSelected(styles.selectedTitleBarTop, styles.titleBarTop)}
                      title={m.get("long_name")}
                      subtitle={`${duration.humanize()}`}
                      titlePosition="top"
                    />
                    <GridListTileBar
                      className={isSelected(styles.selectedTitleBar, styles.titleBar)}
                      title={`${start.format("dddd, MMM Do ")}`}
                      subtitle={`Started at: ${start.format("HH:mm")}`}
                      actionIcon={
                        isSelected("", <IconButton color="inherit">
                          <VisibilityIcon color="inherit" onClick={() => setCurrentMapId(m.get("id"))}/>
                        </IconButton>)
                      }
                    />
                  </GridListTile>
                );
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
