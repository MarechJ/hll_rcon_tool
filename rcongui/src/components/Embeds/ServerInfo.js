import React from "react";
import {
  Grid,
  Typography,
  AppBar,
  Toolbar,
  LinearProgress,
  GridList,
  GridListTile,
  useTheme,
  useMediaQuery,
  makeStyles,
  GridListTileBar,
} from "@material-ui/core";
import { fade } from "@material-ui/core/styles/colorManipulator";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS } from "immutable";
import map_to_pict from "../Scoreboard/utils";

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
  gridList: {
    maxWidth: 500,
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: "translateZ(0)",
  },
}));

const ServerInfo = ({ classes }) => {
  const styles = useStyles();
  const theme = useTheme();
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const isXs = useMediaQuery(theme.breakpoints.down("sm"));

  const getData = () => {
    setIsLoading(true);

    get("public_info")
      .then((res) => showResponse(res, "public_info", false))
      .then((data) => setServerState(fromJS(data.result)))
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
  };

  React.useEffect(getData, []);

  React.useEffect(() => {
    const interval = setInterval(getData, 10 * 1000);
    return () => clearInterval(interval);
  }, []);

  let started = serverState.get("current_map", new Map()).get("start");
  started = started
    ? new Date(Date.now() - new Date(started * 1000))
        .toISOString()
        .substr(11, 8)
    : "N/A";

  const nextMapString = React.useMemo(() => {
    const [map, nbVotes] = serverState
      .get("vote_status")
      ?.get("winning_maps")
      ?.get(0) || ["", 0];
    const totalVotes = serverState.get("vote_status")?.get("total_votes");
    const nextMap = serverState.get("next_map")?.get("name");

    if (map === nextMap) {
      return `Nextmap ${nextMap} ${nbVotes}/${totalVotes} votes`;
    }
    return `Nextmap: ${nextMap}`;
  }, [serverState]);

 
  return (
    <GridList cols={1} className={styles.gridList}>
      <GridListTile>
        <img
          alt="Map"
          src={
            map_to_pict[
              serverState.get("current_map", new Map()).get("just_name", "foy")
            ]
          }
        />
        <GridListTileBar
          className={styles.titleBarTop}
          title={serverState.get("name")}
          subtitle={serverState
            .get("current_map", new Map())
            .get("human_name", "N/A")}
          titlePosition="top"
        />
        <GridListTileBar
          className={styles.titleBarBottom}
          title={`Time: ${started} - Players: ${serverState.get("player_count")}/${serverState.get("max_player_count")}`}
          subtitle={nextMapString}
          titlePosition="bottom"
        />
      </GridListTile>
    </GridList>
  );
};

export default ServerInfo;
