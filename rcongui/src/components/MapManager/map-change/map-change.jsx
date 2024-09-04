import { Box, Button, IconButton, List } from "@mui/material";
import React from "react";
import {
  changeMap,
} from "../../../utils/fetchUtils";
import MapSearch from "./map-search";
import { MapListItem } from "../map-list-item";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import { unifiedGamemodeName } from "../helpers";
import { styled } from '@mui/material/styles';

const Main = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(1),
}));

const Panel = styled('div')(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  gap: theme.spacing(1),
  alignItems: "center",
}));

const Maps = styled(List)(({ theme }) => ({
  maxWidth: theme.breakpoints.values.sm,
  position: "relative",
  overflow: "auto",
  minHeight: 500,
  maxHeight: "70vh",
}));



function MapChange({ maps }) {
  const [nameFilter, setNameFilter] = React.useState("");
  const [modeFilters, setModeFilters] = React.useState({
    warfare: true,
    offensive: false,
    skirmish: false,
  });
  const [selected, setSelected] = React.useState("");
  const statusIntervalRef = React.useRef(null);
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
    (<Main>
      <Panel>
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
      </Panel>
      {currentMap ? (
        <MapListItem
          style={{ borderBottom: "none" }}
          mapLayer={currentMap}
          primary={`>>> ${currentMap.pretty_name} <<<`}
          component={Box}
        />
      ) : (
        <Skeleton variant="rectangular" height={60} />
      )}
      <MapSearch
        onChange={handleOnInputChange}
        filters={modeFilters}
        onFilter={handleModeFilterClick}
      />
      <Maps dense={true}>
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
                  size="large">
                  <CheckCircleOutlineIcon />
                </IconButton>
              )
            }
          />
        ))}
      </Maps>
    </Main>)
  );
}

export default MapChange;
