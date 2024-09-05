import {
  Typography,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  IconButton,
} from "@mui/material";
import Grid from "@mui/material/Unstable_Grid2";
import VisibilityIcon from "@mui/icons-material/Visibility";
import LinkIcon from "@mui/icons-material/Link";
import CheckIcon from "@mui/icons-material/Check";
import React from "react";
import { get, handle_http_errors, showResponse } from "../../../utils/fetchUtils";
import { List as iList, Map, fromJS, List } from "immutable";
import moment from "moment";
import Scores from "../../../components/Scoreboard/Scores";
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

  return (<>
    <Grid
      container
      spacing={2}
      justifyContent="center"
      
    >
      <Grid xs={12}>
        <Typography color="secondary" variant="h4">
          {serverState.get("name", new Map()).get("name")}
        </Typography>
      </Grid>
      {!maps.size ? (
        <Grid>
          <Typography variant="h2">No games recorded yet</Typography>
        </Grid>
      ) : (
        <Grid>
          <Typography variant="caption">
            Select a game below to see its stats
          </Typography>
        </Grid>
      )}
      <Grid xs={12}>
        <div>
          <ImageList
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
                (<ImageListItem
                  onClick={() => doSelectMap(m.get("id"))}
                  key={`${m.get("name")}${m.get("start")}${m.get("end")}`}
                >
                  <img
                    alt="Map"
                    src={`maps/${m.get("map", new Map()).get("image_name")}`}
                  />
                  <ImageListItemBar
                    title={m.get("map", new Map()).get("pretty_name")}
                    subtitle={<>
                      <div>{duration.humanize()}</div>
                      {score}
                    </>}
                    titlePosition="top"
                  />
                  <ImageListItemBar
                    title={`${start.format("dddd, MMM Do ")}`}
                    subtitle={`Started at: ${start.format("HH:mm")}`}
                    actionIcon={isSelected(
                      <IconButton color="inherit" size="large">
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
                      <IconButton color="inherit" onClick={() => doSelectMap(m.get("id"))} size="large">
                        <VisibilityIcon color="inherit" />
                      </IconButton>
                    )}
                  />
                </ImageListItem>)
              );
            })}
          </ImageList>
        </div>
      </Grid>
    </Grid>
    <Grid
      container
      spacing={2}
      justifyContent="center"
      
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
  </>);
};

export default GamesScore;
