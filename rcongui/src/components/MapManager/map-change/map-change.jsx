import {
  Box,
  Button,
  createStyles,
  IconButton,
  List,
  makeStyles,
} from "@material-ui/core";
import React from "react";
import { changeMap, get, getServerStatus } from "../../../utils/fetchUtils";
import MapSearch from "./map-search";
import { MapListItem } from "../map-list-item";
import CheckCircleOutlineIcon from "@material-ui/icons/CheckCircleOutline";
import ReplayIcon from "@material-ui/icons/Replay";
import LockIcon from "@material-ui/icons/Lock";
import Skeleton from "@material-ui/lab/Skeleton";
import { unifiedGamemodeName } from "../helpers";

const useStyles = makeStyles((theme) =>
  createStyles({
    main: {
      display: "flex",
      flexDirection: "column",
      gap: theme.spacing(1),
    },
    panel: {
      display: "flex",
      flexDirection: "row",
      gap: theme.spacing(1),
      alignItems: "center",
    },
    maps: {
      maxWidth: theme.breakpoints.values.sm,
      position: "relative",
      overflow: "auto",
      minHeight: 500,
      maxHeight: "70vh",
    },
  })
);

const UPDATE_INTERVAL = 60 * 1000;

function MapChange() {
  const [currentMap, setCurrentMap] = React.useState(null);
  const [maps, setMaps] = React.useState([]);
  const [nameFilter, setNameFilter] = React.useState("");
  const [modeFilters, setModeFilters] = React.useState({
    warfare: true,
    offensive: false,
    skirmish: false,
  });
  const [selected, setSelected] = React.useState("");
  const statusIntervalRef = React.useRef(null);
  const classes = useStyles();
  const filteredMaps = maps.filter(
    (map) =>
      modeFilters[unifiedGamemodeName(map.game_mode)] &&
      map.pretty_name.toLowerCase().includes(nameFilter.toLowerCase())
  );

  const updateServerStatus = async () => {
    const status = await getServerStatus();
    if (status) {
      setCurrentMap(status.map);
    }
  };

  const getMaps = async () => {
    const response = await get("get_maps");
    const data = await response.json();
    const mapLayers = data.result;
    if (mapLayers) {
      setMaps(mapLayers);
    }
  };

  const handleOnInputChange = (e) => {
    setNameFilter(e.target.value);
  };

  const handleConfirmMap = (mapLayer) => {
    changeMap(mapLayer.id);
    setSelected("");
  };

  const handleResetMap = () => {
    changeMap(currentMap.id);
  };

  const handleModeFilterClick = (filter) => {
    setModeFilters((prevFilters) => ({
      ...prevFilters,
      [filter]: !prevFilters[filter],
    }));
  };

  React.useEffect(() => {
    updateServerStatus();
    getMaps();
    statusIntervalRef.current = setInterval(
      updateServerStatus,
      UPDATE_INTERVAL
    );
    return () => clearInterval(statusIntervalRef.current);
  }, []);

  return (
    <Box className={classes.main}>
      <Box className={classes.panel}>
        <Button
          startIcon={<ReplayIcon />}
          color="secondary"
          onClick={handleResetMap}
          variant="outlined"
          size="small"
        >
          Map Reset
        </Button>
        <Button
          startIcon={<LockIcon />}
          disabled
          variant="outlined"
          size="small"
        >
          Switch Allies
        </Button>
        <Button
          startIcon={<LockIcon />}
          disabled
          variant="outlined"
          size="small"
        >
          Switch Axis
        </Button>
      </Box>
      {currentMap ? (
        <MapListItem
          style={{ borderBottom: "none" }}
          mapLayer={currentMap}
          primary={`>>> ${currentMap.pretty_name} <<<`}
          component={Box}
        />
      ) : (
        <Skeleton variant="rect" height={60} />
      )}
      <MapSearch
        onChange={handleOnInputChange}
        filters={modeFilters}
        onFilter={handleModeFilterClick}
      />
      <List dense={true} className={classes.maps}>
        {filteredMaps.map((mapLayer, index) => (
          <MapListItem
            button
            onClick={() => {
              setSelected(mapLayer.id);
            }}
            key={`${index}#${mapLayer.id}`}
            mapLayer={mapLayer}
            renderAction={(mapLayer) =>
              selected === mapLayer.id && (
                <IconButton
                  edge="end"
                  color="secondary"
                  aria-label="confirm"
                  onClick={() => handleConfirmMap(mapLayer)}
                >
                  <CheckCircleOutlineIcon />
                </IconButton>
              )
            }
          />
        ))}
      </List>
    </Box>
  );
}

export default MapChange;
