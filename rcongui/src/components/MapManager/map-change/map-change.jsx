import {
  Box,
  Button,
  createStyles,
  List,
  makeStyles,
} from "@material-ui/core";
import React from "react";
import {
  changeMap,
} from "../../../utils/fetchUtils";
import MapSearch from "./map-search";
import { MapListItem } from "../map-list-item";
import CheckCircleOutlineIcon from "@material-ui/icons/CheckCircleOutline";
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
      position: "relative",
      overflow: "auto",
      minHeight: 500,
      maxHeight: "70vh",
    },
  })
);


function MapChange({ maps }) {
  const [nameFilter, setNameFilter] = React.useState("");
  const [modeFilters, setModeFilters] = React.useState({
    warfare: true,
    offensive: false,
    skirmish: false,
  });
  const [selected, setSelected] = React.useState("");
  const classes = useStyles();
  const filteredMaps = maps.filter(
    (map) =>
      modeFilters[unifiedGamemodeName(map.game_mode)] &&
      map.pretty_name.toLowerCase().includes(nameFilter.toLowerCase())
  );

  const handleOnInputChange = (e) => {
    setNameFilter(e.target.value);
  };

  const handleConfirmMap = (mapLayer) => {
    changeMap(mapLayer.id);
    setSelected("");
  };

  const handleModeFilterClick = (filter) => {
    setModeFilters((prevFilters) => ({
      ...prevFilters,
      [filter]: !prevFilters[filter],
    }));
  };

  return (
    <Box className={classes.main}>
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
                <Button
                  endIcon={<CheckCircleOutlineIcon />}
                  edge="end"
                  color="secondary"
                  aria-label="confirm"
                  onClick={() => handleConfirmMap(mapLayer)}
                >
                  Confirm
                </Button>
              )
            }
          />
        ))}
      </List>
    </Box>
  );
}

export default MapChange;
