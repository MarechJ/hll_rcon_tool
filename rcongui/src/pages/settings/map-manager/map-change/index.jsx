import { Button, List } from "@mui/material";
import { changeMap } from "@/utils/fetchUtils";
import MapSearch from "./map-search";
import { MapListItem } from "@/components/MapManager/map-list-item";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import { unifiedGamemodeName } from "@/components/MapManager/helpers";
import { styled } from "@mui/styles";
import { useOutletContext } from "react-router-dom";
import {useState} from "react";

const Main = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: theme.spacing(1),
}));

const Maps = styled(List)(({ theme }) => ({
  maxWidth: theme.breakpoints.values.sm,
  position: "relative",
  overflow: "auto",
  minHeight: 500,
  maxHeight: "70vh",
}));

function MapChange() {
  const { maps } = useOutletContext();
  const [nameFilter, setNameFilter] = useState("");
  const [modeFilters, setModeFilters] = useState({
    warfare: true,
    offensive: false,
    skirmish: false,
  });
  const [selected, setSelected] = useState("");
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

  const handleListItemClick = (mapLayer) => {
    setSelected(mapLayer.id);
  };

  return (
    (<Main>
      <MapSearch
        onChange={handleOnInputChange}
        filters={modeFilters}
        onFilter={handleModeFilterClick}
      />
      <Maps dense={true}>
        {filteredMaps.map((mapLayer, index) => (
          <MapListItem
            key={`${index}#${mapLayer.id}`}
            asButton={true}
            onClick={() => handleListItemClick(mapLayer)}
            mapLayer={mapLayer}
            secondaryAction={
              selected === mapLayer.id && (
                <Button
                  endIcon={<CheckCircleOutlineIcon />}
                  edge="end"
                  color="secondary"
                  aria-label="confirm"
                  onClick={() => handleConfirmMap(mapLayer)}
                  size="large"
                >
                  Confirm
                </Button>
              )
            }
          />
        ))}
      </Maps>
    </Main>)
  );
}

export default MapChange;
