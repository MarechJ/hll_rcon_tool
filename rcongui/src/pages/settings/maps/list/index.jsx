import { useRouteLoaderData } from "react-router-dom";
import { useState } from "react";
import { Box } from "@mui/material";
import { MapList } from "../MapList";
import { MapChangeListItem } from "../MapListItem";
import { MapFilter } from "../MapFilter";
import { useMapChange } from "@/hooks/useMapChange";

const MapListPage = () => {
  const { maps } = useRouteLoaderData("maps");
  const [filteredMapOptions, setFilteredMapOptions] = useState(maps);
  const { MapChangeDialog, openMapChangeDialog } = useMapChange();

  const handleFilterChange = (filteredMaps) => {
    setFilteredMapOptions(filteredMaps);
  };

  return (
    <>
      <Box
        sx={{
          height: "fit-content",
          py: 2,
          maxWidth: (theme) => theme.breakpoints.values.md,
        }}
      >
        <MapFilter maps={maps} onFilterChange={handleFilterChange} />
        <MapList
          maps={filteredMapOptions}
          renderItem={(mapLayer) => (
            <MapChangeListItem
              mapLayer={mapLayer}
              key={mapLayer.id}
              onClick={() => openMapChangeDialog(mapLayer)}
            />
          )}
        />
      </Box>
      <MapChangeDialog />
    </>
  );
};

export default MapListPage;