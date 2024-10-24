import React from "react";
import {
  ImageList,
  ImageListItem,
  ImageListItemBar,
} from "@mui/material";
import { get, handle_http_errors, showResponse } from "../../utils/fetchUtils";
import { List as iList, Map, fromJS } from "immutable";

const ServerInfo = () => {
  const [serverState, setServerState] = React.useState(new Map());
  const [isLoading, setIsLoading] = React.useState(true);
  const [mapName, setMapName] = React.useState("");

  const getData = () => {
    setIsLoading(true);

    get("get_public_info")
      .then((res) => showResponse(res, "get_public_info", false))
      .then((data) => setServerState(fromJS(data.result)))
      .then(() => setIsLoading(false))
      .catch(handle_http_errors);
  };

  React.useEffect(getData, []);

  React.useEffect(() => {
    const interval = setInterval(getData, 10 * 1000);
    return () => clearInterval(interval);
  }, []);

  React.useEffect(() => {
    if (serverState.get("current_map") !== undefined) {
      setMapName(serverState.get("current_map")?.get("name"));
    }
  }, [serverState]);

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
    <ImageList cols={1} >
      <ImageListItem>
        <img
          alt="Map"
          src={`maps/${serverState
            .get("current_map")
            ?.get("map")
            ?.get("image_name")}`}
        />
        <ImageListItemBar
          
          title={serverState.get("name", new Map()).get("name")}
          subtitle={serverState
            .get("current_map", new Map())
            .get("map")
            ?.get("pretty_name")}
          titlePosition="top"
        />
        <ImageListItemBar
          
          title={`Time: ${started} - Players: ${serverState.get(
            "player_count"
          )}/${serverState.get("max_player_count")}`}
          subtitle={nextMapString}
          titlePosition="bottom"
        />
      </ImageListItem>
    </ImageList>
  );
};

export default ServerInfo;
