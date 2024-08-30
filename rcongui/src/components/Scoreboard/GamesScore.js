import {
  Grid,
  Typography,
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
import Scores from "./Scores";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";

const GamesScore = () => {
  let { slug } = useParams();
  slug = parseInt(slug);
  const [scores, setScores] = React.useState(new iList());
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [isPaused, setPaused] = React.useState(false);
  const [maps, setMaps] = React.useState(new List());
  const [mapsPage, setMapsPage] = React.useState(1);
  const [mapsPageSize, setMapsPageSize] = React.useState(30);
  const [mapsTotal, setMapsTotal] = React.useState(0);

  const refreshIntervalSec = 10;
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

    get("get_public_info")
      .then((res) => showResponse(res, "get_public_info", false))
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

  document.title = serverState.get("name", new Map()).get("name", "HLL Stats");
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
        
      >
        <Grid item xs={12}>
          <Typography color="secondary" variant="h4">
            {serverState.get("name", new Map()).get("name")}
          </Typography>
        </Grid>
        {!maps.size ? (
          <Grid item>
            <Typography variant="h2">No games recorded yet</Typography>
          </Grid>
        ) : (
          <Grid item>
            <Typography variant="caption">
              Select a game below to see its stats
            </Typography>
          </Grid>
        )}
        <Grid item xs={12}>
          <div>
            <GridList
              cols={2}
            >
              {maps.map((m) => {
                const start = moment(m.get("start") + "Z");
                const end = moment(m.get("end") + "Z");
                const duration = moment.duration(end - start);
                const isSelected = (isReturn, isNotReturn) =>
                  m.get("id") === slug ? isReturn : isNotReturn;

                let score = '';
                if (m.get('result')) {
                  score = <div>Axis {m.get('result').get('axis')} - {m.get('result').get('allied')} Allied</div>
                }
                return (
                  <GridListTile
                    onClick={() => doSelectMap(m.get("id"))}
                    key={`${m.get("name")}${m.get("start")}${m.get("end")}`}
                  >
                    <img
                      alt="Map"
                      src={`maps/${m.get("map", new Map()).get("image_name")}`}
                    />

                    <GridListTileBar
                      title={m.get("map", new Map()).get("pretty_name")}
                      subtitle={<>
                        <div>{duration.humanize()}</div>
                        {score}
                      </>}
                      titlePosition="top"
                    />
                    <GridListTileBar
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
        
      >
        <Scores
          
          serverState={serverState}
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
