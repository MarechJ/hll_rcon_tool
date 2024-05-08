import {
  Grid,
  Typography,
  makeStyles,
  GridList,
  GridListTile,
  GridListTileBar,
  IconButton,
} from "@material-ui/core";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import VisibilityIcon from "@material-ui/icons/Visibility";
import LinkIcon from "@material-ui/icons/Link";
import CheckIcon from "@material-ui/icons/Check";
import React from "react";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS, List } from "immutable";
import moment from "moment";
import { useTheme } from "@material-ui/core/styles";
import Scores from "./Scores";
import { fade } from "@material-ui/core/styles/colorManipulator";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";

const useStyles = makeStyles((theme) => ({
  singleLine: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
  },
  transparentPaper: {
    backgroundColor: fade(theme.palette.background.paper, 0.6),
    borderRadius: "0px",
  },
  clickable: {
    cursor: "pointer",
  },
  gridList: {
    flexWrap: "nowrap",
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: "translateZ(0)",
  },
  selectedMap: {
    color: theme.palette.secondary.main,
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
  black: {
    backgroundColor: theme.palette.primary.main,
  },
}));

const GamesScore = ({ classes }) => {
  let { slug } = useParams();
  slug = parseInt(slug);
  console.log("Slug ", slug);
  const styles = useStyles();
  const [scores, setScores] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [maps, setMaps] = React.useState(new List());
  const [mapsPage, setMapsPage] = React.useState(1);
  const [mapsPageSize, setMapsPageSize] = React.useState(30);
  const [mapsTotal, setMapsTotal] = React.useState(0);

  const refreshIntervalSec = 10;
  const theme = useTheme();
  const sm = useMediaQuery(theme.breakpoints.up("sm"));
  const md = useMediaQuery(theme.breakpoints.up("md"));
  const lg = useMediaQuery(theme.breakpoints.up("lg"));
  const xl = useMediaQuery(theme.breakpoints.up("xl"));
  const durationToHour = (val) =>
    new Date(val * 1000).toISOString().substr(11, 5);

  const lastRefresh = scores.get("snapshot_timestamp")
    ? moment.unix(scores.get("snapshot_timestamp")).format()
    : "N/A";

  const getShareableLink = () => {
    return window.location.href;
  };
  const doSelectMap = (map_id) => {
    window.location.hash = `#/gamescoreboard/${map_id}`;
    console.log(`Change to ${map_id}`);
  };

  const [hasCopiedLink, setHasCopiedLink] = React.useState(false);
  const onCopyLink = () => {
    setHasCopiedLink(true);
    setTimeout(() => {
      setHasCopiedLink(false);
    }, 1000);
    toast.success("Link copied to clipboard");
  };

  moment.relativeTimeThreshold("m", 120);
  const getData = () => {
    setIsLoading(true);

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
        if (data.result.maps.length > 0 && !slug) {
          window.location.hash = `#/gamescoreboard/${data.result.maps[0].id}`;
        }
      })
      .catch(handle_http_errors);
  };

  React.useEffect(() => {
    if (!slug) {
      return;
    }

    get(`get_map_scoreboard?map_id=${slug}`)
      .then((res) => showResponse(res, "get_map_scoreboard", false))
      .then((data) =>
        data.result && data.result.player_stats
          ? setScores(fromJS(data.result.player_stats))
          : ""
      )
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
  }, [slug]);

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
    <>
      <Grid
        container
        spacing={2}
        justify="center"
        className={classes.gridContainer}
      >
        <Grid item xs={12} className={styles.transparentPaper}>
          <Typography color="secondary" variant="h4">
            {serverState.get("name")}
          </Typography>
        </Grid>
        {!maps.size ? (
          <Grid item className={styles.paper}>
            <Typography variant="h2">No games recorded yet</Typography>
          </Grid>
        ) : (
          <Grid item>
            <Typography variant="caption">
              Select a game below to see its stats
            </Typography>
          </Grid>
        )}
        <Grid item xs={12} className={`${classes.doublePadding}`}>
          <div className={styles.singleLine}>
            <GridList
              cols={
                xl
                  ? Math.min(maps.size, 8.5)
                  : lg
                  ? Math.min(maps.size, 5.5)
                  : md
                  ? Math.min(maps.size, 3.5)
                  : sm
                  ? Math.min(maps.size, 2.5)
                  : Math.min(maps.size, 1.5)
              }
              className={styles.gridList}
            >
              {maps.map((m) => {
                const start = moment(m.get("start") + "Z");
                const end = moment(m.get("end") + "Z");
                const duration = moment.duration(end - start);
                const isSelected = (isReturn, isNotReturn) =>
                  m.get("id") === slug ? isReturn : isNotReturn;

                return (
                  <GridListTile
                    className={styles.clickable}
                    onClick={() => doSelectMap(m.get("id"))}
                    key={`${m.get("name")}${m.get("start")}${m.get("end")}`}
                  >
                    <img
                      alt="Map"
                      src={`maps/${m.get("map", new Map()).get("image_name")}`}
                    />

                    <GridListTileBar
                      className={isSelected(
                        styles.selectedTitleBarTop,
                        styles.titleBarTop
                      )}
                      title={m.get("map", new Map()).get("pretty_name")}
                      subtitle={`${duration.humanize()}`}
                      titlePosition="top"
                    />
                    <GridListTileBar
                      className={isSelected(
                        styles.selectedTitleBar,
                        styles.titleBar
                      )}
                      title={`${start.format("dddd, MMM Do ")}`}
                      subtitle={`Started at: ${start.format("HH:mm")}`}
                      actionIcon={isSelected(
                        <IconButton color="inherit">
                          <CopyToClipboard
                            text={getShareableLink()}
                            onCopy={onCopyLink}
                          >
                            {hasCopiedLink ? (
                              <CheckIcon color="inherit" />
                            ) : (
                              <LinkIcon color="inherit" />
                            )}
                          </CopyToClipboard>
                        </IconButton>,
                        <IconButton
                          color="inherit"
                          onClick={() => doSelectMap(m.get("id"))}
                        >
                          <VisibilityIcon color="inherit" />
                        </IconButton>
                      )}
                    />
                  </GridListTile>
                );
              })}
            </GridList>
          </div>
        </Grid>
      </Grid>
      <Grid
        container
        spacing={2}
        justify="center"
        className={classes.gridContainer}
      >
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
    </>
  );
};

export default GamesScore;
